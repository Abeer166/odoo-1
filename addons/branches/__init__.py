
from odoo import SUPERUSER_ID, api

from . import models


def pre_init_check_vers(cr):
    from odoo.service import common
    from odoo.exceptions import Warning
    version_info = common.exp_version()
    server_serie =version_info.get('server_serie')
    if server_serie!='16.0':raise Warning('Module support Odoo series 16.0 found {}.'.format(server_serie))
    return True
