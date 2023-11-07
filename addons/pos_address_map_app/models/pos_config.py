# -*- coding: utf-8 -*-

from itertools import groupby
from datetime import datetime, timedelta
from odoo.http import request
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools import html2plaintext
import odoo.addons.base.models.decimal_precision as dp

class POSConfig(models.Model):
	_inherit = 'pos.config'

	add_api_key = fields.Char('Google API key')


	def get_api_key(self):
		user = request.env.user
		# pos_session = self.env['pos.session'].search([('state', '=', 'opened'), ('user_id', '=', user.id)])
		pos_session = self.env['pos.session'].sudo().search([('user_id','=',user.id),('state','in',['opening_control', 'opened'])])
		return pos_session.config_id.add_api_key


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	add_api_key = fields.Char(related='pos_config_id.add_api_key',readonly=False)

	def get_api_key(self):
		user = request.env.user
		# pos_session = self.env['pos.session'].search([('state','=','opened'),('user_id','=',user.id)])
		pos_session = self.env['pos.session'].sudo().search(
			[('user_id', '=', user.id), ('state', 'in', ['opening_control', 'opened'])])
		return pos_session.config_id.add_api_key
