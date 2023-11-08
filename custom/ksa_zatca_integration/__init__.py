# -*- coding: utf-8 -*-

from . import models, wizard, reports


def post_init_hook(cr, registry):
    cr.execute("UPDATE account_move SET invoice_datetime = invoice_date ")
