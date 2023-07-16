# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    'name': 'Signup Email Verification',
    'author': 'Softhealer Technologies',
    'website': 'http://www.softhealer.com',
    "support": "support@softhealer.com",
    'category': 'Website',
    'summary': "Verify Email Signup, Email Verification Module, Sign-up Email Confirmation, Account Activate By Email, Log-in Email Verification,Sign-in Mail Verification, Signup Verification, Log-in Verification, Email OTP Verification,E-mail Verification Odoo",
    'description': """
Whenever any user sign up, that will pass to the email verification process, the user can log in after email verification. For email, verification users have to verify with the verification code that sent in a user email address. It shows alert if you entered an invalid verification code. Only verified users can access the system.
 Signup Email Verification Odoo
 Verify Email At Signup Module, Email Verification, Email Confirmation On Sign-up, Account Activate By Email, Log-in Email Verification, Sign-in Mail Verification, Signup Verification Odoo
Verify Email At Signup, Email Verification  Module, Sign-up Email Confirmation, Account Activate By Email, Log-in Email Verification, Sign-in Mail Verification, Signup Verification App, Log-in Verification, Email OTP Verification, Odoo Email Verification, Odoo E-mail Verification, Mail OTP Odoo

                    """,
    'version': '16.0.1',
    'depends': [
        'base',
        'auth_signup',
        'portal'
    ],
    'application': True,
    'data': [
        "security/ir.model.access.csv",
        "data/user_mail_template.xml",
        'views/user_signup_approve_view.xml',
        "views/sh_mass_update_action.xml",
        "views/user_signup_template.xml",
        "wizard/sh_mass_approve_reject_wizard.xml",
    ],
    'assets': {
        'web.assets_frontend': [
            'sh_signup_email_approval/static/src/js/sh_code_verify.js',
        ],
    },

    'images': ['static/description/background.png', ],
    "live_test_url": "https://youtu.be/AUuwbuCwgGY",
    "license": "OPL-1",
    'auto_install': False,
    'installable': True,
    'post_init_hook': '_post_init_res_users_apply_verified',
    "price": 35,
    "currency": "EUR"

}
