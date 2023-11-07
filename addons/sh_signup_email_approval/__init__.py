# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from . import controllers
from . import wizard
from . import models


from odoo import api, SUPERUSER_ID


def _post_init_res_users_apply_verified(cr, registry):

    env = api.Environment(cr, SUPERUSER_ID, {})
    env.cr.execute("UPDATE res_users SET sh_user_from_signup='t'")
    env.cr.commit()
