# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields


class ShMassApproveRejectWizard(models.TransientModel):
    _name = 'sh.mass.approve.reject.wizard'
    _description = 'Mass Approve Reject Wizard Details'

    sh_mass_update_selection = fields.Selection(
        string='Approve/Reject', selection=[('approve', 'Approve'), ('reject', 'Reject')], required=True)

    def action_mass_update(self):
        if self.env.context and self.env.context.get('active_ids'):
            users = self.env['res.users'].browse(
                self.env.context.get('active_ids'))
            for user in users:
                if self.sh_mass_update_selection == 'approve':
                    user.sh_user_from_signup = True
                else:
                    user.sh_user_from_signup = False
