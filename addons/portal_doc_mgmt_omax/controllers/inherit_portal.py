# -*- coding: utf-8 -*-
import base64
import functools
import json
import logging
import math
import re

from werkzeug import urls

from odoo import fields as odoo_fields, http, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError, AccessDenied
from odoo.http import content_disposition, Controller, request, route
from odoo.tools import consteq
from odoo.addons.portal.controllers.portal import CustomerPortal

class CustomeCustomerPortal(CustomerPortal):

    MANDATORY_BILLING_FIELDS = ["name", "phone", "email", "street", "city", "country_id"]
    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name"]

    _items_per_page = 80

    def _prepare_portal_layout_values(self):
        sales_user = False
        partner = request.env.user.partner_id
        if partner.user_id and not partner.user_id._is_public():
            sales_user = partner.user_id
        return {
            'sales_user': sales_user,
            'page_name': 'home',
        }

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        attachments = http.request.env['ir.attachment'].sudo().search([('shared_user_ids','in',http.request.env.user.id)])
        models = []
        for attachment in attachments:
            if attachment.res_model:
                if attachment.res_model not in models:
                    models.append(attachment.res_model)
                    attachment_count = http.request.env['ir.attachment'].sudo().search([('res_model','=',attachment.res_model),('shared_user_ids','in',http.request.env.user.id)])
                    counts = 0
                    for count in attachment_count:
                        counts = counts + 1
                    ir_model = http.request.env['ir.model'].sudo().search([('model','=', attachment.res_model)])
                    values[str(ir_model.name)+'_count'] = counts
        return values

    @route(['/my/docs/<string:name>'], type='http', auth="user", website=True)
    def docs(self, name, **kw):
        ir_attachment = http.request.env['ir.attachment'].sudo().search([('res_model','=',name),('shared_user_ids','in',http.request.env.user.id)])
        data = []
        page_name = None
        for attachment in ir_attachment:
            data.append([attachment.name,attachment.create_uid.name, attachment.create_date, attachment.id])
            ir_model = http.request.env['ir.model'].sudo().search([('model','=', attachment.res_model)])
            page_name = ir_model.name
        doc_data = {'details' : data, 'page_name' : 'Shared_Doc', 'page_name_real' : page_name}
        return request.render("portal_doc_mgmt_omax.portal_shared_documents", doc_data)

    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        values = self._prepare_portal_layout_values()
        attachments = http.request.env['ir.attachment'].sudo().search([('shared_user_ids','in',http.request.env.user.id)])
        models = []
        models_name = []
        for attachment in attachments:
            if attachment.res_model:
                if attachment.res_model not in models:
                    models.append(attachment.res_model)
                    ir_model = http.request.env['ir.model'].sudo().search([('model','=', attachment.res_model)])
                    models_name.append([ir_model.name, attachment.res_model])
        values['models'] = models_name
        return request.render("portal.portal_my_home", values)

    
    
    
    
