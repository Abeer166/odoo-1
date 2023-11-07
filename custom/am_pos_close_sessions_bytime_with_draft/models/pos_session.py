# -*- coding: utf-8 -*-

from odoo import fields, models, api, _ , tools
from odoo.exceptions import Warning
from odoo.exceptions import RedirectWarning, UserError, ValidationError
import random
import psycopg2
import base64
import pytz
from odoo.http import request
from functools import partial
from odoo.tools import float_is_zero

from datetime import date, datetime,timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import logging

_logger = logging.getLogger(__name__)

class PosConfig(models.Model):
    _inherit='pos.config'

    close_session_hour = fields.Integer(string='Close Session at ',default=23, help='Close Session At time in Day from 0:23, by default UTC Time if need to change to current Timezone change user in scheduler action')
    flag_close_session_hour = fields.Boolean(string='Close Session By Automated',default=False, help='Close Session Automated')

class ResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    close_session_hour = fields.Integer(related='pos_config_id.close_session_hour', readonly=False,string='Close Session at ', help='Close Session At time in Day from 0:23, by default UTC Time if need to change to current Timezone cchange user in scheduler action')
    flag_close_session_hour = fields.Boolean(related='pos_config_id.flag_close_session_hour', readonly=False,string='Close Session By Automated', help='Close Session Automated')

class PosSession(models.Model):
    _inherit='pos.session'
    def _validate_session(self, balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None):
        bank_payment_method_diffs = bank_payment_method_diffs or {}
        self.ensure_one()
        sudo = self.user_has_groups('point_of_sale.group_pos_user')
        if self.order_ids or self.statement_line_ids:
            self.cash_real_transaction = sum(self.statement_line_ids.mapped('amount'))
            if self.state == 'closed':
                raise UserError(_('This session is already closed.'))
            self._check_if_no_draft_orders()
            self._check_invoices_are_posted()
            cash_difference_before_statements = self.cash_register_difference
            if self.update_stock_at_closing:
                self._create_picking_at_end_of_session()
                self.order_ids.filtered(lambda o: not o.is_total_cost_computed)._compute_total_cost_at_session_closing(self.picking_ids.move_ids)
            try:
                data = self.with_company(self.company_id)._create_account_move(balancing_account, amount_to_balance, bank_payment_method_diffs)
            except AccessError as e:
                if sudo:
                    data = self.sudo().with_company(self.company_id)._create_account_move(balancing_account, amount_to_balance, bank_payment_method_diffs)
                else:
                    raise e

            try:
                balance = sum(self.move_id.line_ids.mapped('balance'))
                with self.move_id._check_balanced({'records': self.move_id.sudo()}):
                    pass
            except UserError:
                # Creating the account move is just part of a big database transaction
                # when closing a session. There are other database changes that will happen
                # before attempting to create the account move, such as, creating the picking
                # records.
                # We don't, however, want them to be committed when the account move creation
                # failed; therefore, we need to roll back this transaction before showing the
                # close session wizard.
                self.action_pos_session_closing_control(self._get_balancing_account(), balance)
                self.env.cr.rollback()
                return self._close_session_action(balance)

            self._post_statement_difference(cash_difference_before_statements)
            if self.move_id.line_ids:
                self.move_id.sudo().with_company(self.company_id)._post()
                # Set the uninvoiced orders' state to 'done'
                self.env['pos.order'].search([('session_id', '=', self.id), ('state', '=', 'paid')]).write({'state': 'done'})
            else:
                self.move_id.sudo().unlink()
            self.sudo().with_company(self.company_id)._reconcile_account_move_lines(data)
        else:
            self._post_statement_difference(self.cash_register_difference)

        self.write({'state': 'closed'})
        return True

    def automated_close_sessions_bytime(self):
        user = self.user_id or self.env.user
        tz = pytz.timezone(user.tz) or pytz.utc
        # print(datetime.now(tz).strftime('%Y-%m-%d 00:30:59'))
        now_hour = datetime.now(tz).hour

        print(now_hour)

        pos_sessions = self.env['pos.session'].search([('state','=','opened'),('config_id.flag_close_session_hour','=',True),('config_id.close_session_hour','=',now_hour)])
        print(pos_sessions)
        for session in pos_sessions:
            try:
                draft_orders = session.order_ids.filtered(lambda order: order.state == 'draft').unlink()
                session.action_pos_session_closing_control()
                print("Done session id "+str(session.id))
            except Exception as e:
                print("Fail session id "+str(session.id) +" : ",e)
