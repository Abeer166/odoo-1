# -*- coding: utf-8 -*-

from odoo import fields, models

class pos_config(models.Model):
    _inherit = 'pos.config'

    allow_default_cash = fields.Boolean(string='Set Default Cash Opening')
    default_opening = fields.Float(string='Editable Opening Amount')
    hide_closing = fields.Boolean(string='Hide Closing Summary')


class PosSession(models.Model):
    _inherit = 'pos.session'

    def set_cashbox_pos(self, cashbox_value, notes):
        self.state = 'opened'
        self.opening_notes = notes
        difference = cashbox_value - self.cash_register_balance_start
        if self.config_id.allow_default_cash:
            #Set to zero to prevent cash difference posting
            difference = 0
        self.cash_register_balance_start = cashbox_value
        self._post_statement_difference(difference)
        self._post_cash_details_message('Opening', difference, notes)