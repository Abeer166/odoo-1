from odoo import fields, models, api, _, tools


class pos_config(models.Model):
	_inherit = 'pos.config'

	allow_show_popup = fields.Boolean(string='Allow To Show Opening Closing Popup')


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'
	
	allow_show_popup = fields.Boolean(related='pos_config_id.allow_show_popup',readonly=False)

