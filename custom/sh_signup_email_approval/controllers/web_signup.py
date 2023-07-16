# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
import random
from odoo.http import request
from odoo import http, _
from odoo.addons.web.controllers.home import ensure_db, Home
from odoo.exceptions import UserError, AccessError


class WebHome(Home):

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = {key: qcontext.get(key)
                  for key in ('login', 'name', 'password')}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_lang_codes = [code for code,
                                _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '').split('_')[0]
        if lang in supported_lang_codes:
            values['lang'] = lang
        self._signup_with_values(qcontext.get('token'), values)

        # ----------------------------------------------------------

        user_id = request.env['res.users'].sudo().search(
            [('login', '=', values.get('login'))], limit=1)
        # user_email_template = request.env.ref(
        #     'sh_signup_email_approval.sh_user_mail_template', raise_if_not_found=False)
        if user_id:
            verification_number = random.randrange(1000, 9999)
            user_id.sudo().write({'verification_code': str(
                verification_number), 'sh_password': qcontext.get('password')})
            # user_email_template.sudo().send_mail(user_id.id, force_send=True)

        # ----------------------------------------------------------
        request.env.cr.commit()

    @http.route('/web/signup/verify/<int:user_id>', type='http', auth='public', website=True,
                sitemap=False, csrf=False)
    def web_auth_signup_verify(self, user_id, *args, **kw):
        if not user_id or not kw.get('access_token'):
            raise AccessError(_("User id or access_token is missing"))

        get_user_info = request.env['res.users'].sudo().search_read(
            [('id', '=', user_id), ('sh_access_token', '=', kw.get('access_token'))], limit=1)

        if not get_user_info:
            raise AccessError(_("Something went wrong."))
        request.session.logout()
        return request.render('sh_signup_email_approval.sh_signup_verfiy_template', {})
