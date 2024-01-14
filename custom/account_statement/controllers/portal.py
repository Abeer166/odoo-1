# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details

import binascii
from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request, content_disposition
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression



class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        company = request.env.user.company_id
        
        if 'customer_count' in counters:
            values['customer_count'] = len(partner.balance_invoice_ids)
        return values


    @http.route(['/my/request', '/my/request/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_request(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        balance_invoice_ids = request.env.user.partner_id.balance_invoice_ids
        if not sortby:
           sortby = 'active_or_not'

        # count for pager
        customer_count = len(partner.balance_invoice_ids)
        # make pager
        pager = portal_pager(
                url="/my/request",
                url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
                total=customer_count,
                page=page,
                step=self._items_per_page
        )
        # search the count to display, according to the pager data
        customer_rq = balance_invoice_ids
        request.session['my_customer_history'] = customer_rq.ids[:100]

        values.update({
                'date': date_begin,
                'customer_rq': customer_rq,
                'page_name': 'request',
                'pager': pager,
                'default_url': '/my/request',
                'sortby': sortby,
            })
        return request.render("account_statement.portal_customer_statement_view", values)


    @http.route('/customer_portal/download_pdf', type='http', auth='user')
    def download_customer_report(self,access_token=None):
        partner = request.env.user.partner_id
        pdf = request.env["ir.actions.report"].sudo()._render_qweb_pdf('account_statement.report_customert_print',partner.id)[0]
        report_name = 'Customer Statement' +'.pdf'
        return request.make_response(pdf, headers=[('Content-Type', 'application/pdf'),('Content-Disposition', content_disposition(report_name))])


    @http.route('/send_customer/send_mail', type='http', auth='user', website = True)
    def send_customer_statement(self, access_token=None):
        partner = request.env.user.partner_id
        partners_to_email = [child for child in partner.child_ids if child.type == 'invoice' and child.email]
        if not partners_to_email and partner.email:
            partners_to_email = [partner]
        if partners_to_email:
            for partner_to_email in partners_to_email:
                mail_template_id = request.env.ref('account_statement.email_template_customer_statement')
                mail_template_id.sudo().send_mail(partner_to_email.id)
                vals = {'page_name':'send_mail'}
        return request.render('account_statement.send_mail_success_page', vals)



    @http.route('/send_supplier/send_mail', type='http', auth='user', website = True)
    def send_supplier_statement(self, access_token=None):
        partner = request.env.user.partner_id
        partners_to_email = [child for child in partner.child_ids if child.type == 'invoice' and child.email]
        if not partners_to_email and partner.email:
            partners_to_email = [partner]
        if partners_to_email:
            for partner_to_email in partners_to_email:
                mail_template_id = request.env.ref('account_statement.email_template_supplier_statement')
                mail_template_id.sudo().send_mail(partner_to_email.id)
                vals = {'page_name':'send_sup_mail'}
        return request.render('account_statement.send_mail_success_page', vals)



   

class SupplierPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        
        if 'supplier_count' in counters:
            values['supplier_count'] = len(partner.supplier_invoice_ids)
        return values


    @http.route(['/my/sup_request', '/my/sup_request/page/<int:page>'], type='http', auth="user", website=True)
    def portal_supplier_request(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        supplier_invoice_ids = request.env.user.partner_id.supplier_invoice_ids
        if not sortby:
           sortby = 'active_or_not'

        # count for pager
        supplier_count = len(partner.supplier_invoice_ids)
        # make pager
        pager = portal_pager(
                url="/my/request",
                url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
                total=supplier_count,
                page=page,
                step=self._items_per_page
        )
        supplier_rq = supplier_invoice_ids
        request.session['my_supplier_history'] = supplier_rq.ids[:100]

        values.update({
                'date': date_begin,
                'supplier_rq': supplier_rq,
                'page_name': 'sup_request',
                'pager': pager,
                'default_url': '/my/sup_request',
                'sortby': sortby,
            })
        return request.render("account_statement.portal_supplier_statement_view", values)


    @http.route('/supplier_portal/download_pdf', type='http', auth='user')
    def download_supplier_report(self, payslip_id=None, access_token=None, **kw):
        partner = request.env.user.partner_id
        pdf = request.env["ir.actions.report"].sudo()._render_qweb_pdf('account_statement.report_supplier_print',partner.id)[0]
        report_name = 'Supplier Statement' +'.pdf'
        return request.make_response(pdf, headers=[('Content-Type', 'application/pdf'),('Content-Disposition', content_disposition(report_name))])








