# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

import werkzeug
from odoo.http import request
from odoo import http, _
import json
import random
import odoo
from odoo.addons.web.controllers.home import ensure_db, Home
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.exceptions import AccessError


class ShWebSignup(AuthSignupHome):
    @http.route()
    def web_auth_signup(self, *args, **kw):
        response = super(ShWebSignup, self).web_auth_signup(args=args, kw=kw)

        if response.qcontext.get('error') and response.qcontext.get('error') == 'Another user is already registered using this email address.':
            get_user = request.env['res.users'].sudo().search(
                [('login', '=', response.qcontext.get('login'))], limit=1)

            if get_user and get_user.share and get_user.sh_access_token and get_user.sh_user_from_signup == False:

                user_email_template = request.env.ref(
                    'sh_signup_email_approval.sh_user_mail_template', raise_if_not_found=False)
                verification_number = random.randrange(1000, 9999)
                get_user.sudo().write({'verification_code': str(
                    verification_number), 'sh_password': response.qcontext.get('password')})

                user_email_template.sudo().send_mail(get_user.id, force_send=True)

                url = '/web/signup/verify/' + \
                    str(get_user.id)+'?'+'access_token=' + \
                    get_user.sh_access_token
                return werkzeug.utils.redirect(url)
        return response


class VerifyUserValidation(http.Controller):
    @http.route(['/verify/user/validation'], type='json', auth='public', website=True)
    def verify_user_validation(self, url, code):
        url = str(url)
        split_url = url.split("/")
        u_id = split_url[-1].split('?')
        if not u_id[0] or not u_id[1]:
            raise AccessError(_("Something went wrong."))
        else:
            sh_access_token = u_id[1].split('=')[1]
            get_user_info = request.env['res.users'].sudo().search([('id', '=', int(
                u_id[0])), ('sh_access_token', '=', sh_access_token), ('verification_code', '=', code)], limit=1)

            if not get_user_info:
                return json.dumps({'user_found': False})
            else:
                get_user_info.sh_user_from_signup = True
                request.session.authenticate(
                    request.session.db, get_user_info.login, get_user_info.sh_password)
                import threading
                threading.current_thread().uid = get_user_info.id
                # terminate transaction before re-creating cursor below
                request._cr.commit()
                odoo.modules.registry.Registry.new(request.session.db)
                request._cr.reset()
                threading.current_thread().uid = get_user_info.id
                return json.dumps({'user_found': True})


class CustomSignupHome(Home):

    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        response = super(CustomSignupHome, self).web_login(*args, **kw)

        invitation_scope = request.env['ir.config_parameter'].sudo(
        ).get_param('auth_signup.invitation_scope', 'b2b')

        if invitation_scope and invitation_scope == 'b2c' and request.params.get('login_success'):

            user_id = request.env['res.users'].sudo().search(
                [('login', '=', request.params['login']), ('sh_user_from_signup', '=', False)])

            if user_id and user_id.has_group('base.group_portal'):
                user_email_template = request.env.ref(
                    'sh_signup_email_approval.sh_user_mail_template', raise_if_not_found=False)
                verification_number = random.randrange(1000, 9999)
                user_id.sudo().write({'verification_code': str(
                    verification_number)})

                user_email_template.sudo().send_mail(user_id.id, force_send=True)

                url = '/web/signup/verify/' + \
                    str(user_id.id)+'?'+'access_token='+user_id.sh_access_token

                return werkzeug.utils.redirect(url)

        return response
