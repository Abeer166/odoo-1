from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    whatsappp_number=fields.Char(string="Whatsapp No")

    def send_msg(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'odoo.whatsapp.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_user_id': self.id},
                }


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    additional_note = fields.Char(string='Additional Note')

    def send_whatsapp_msg(self):
        # Find the e-mail template
        template = self.env.ref('sale.email_template_edi_sale')
        print("<><><><><><>><>template<><<><>><><<>>><>", template)
        # You can also find the e-mail template like this:
        # template = self.env['ir.model.data'].get_object('mail_template_demo', 'example_email_template')
 
        # Send out the e-mail template to the user
        self.env['mail.template'].browse(template.id).send_mail(self.id)
        message_content = "Hello, Your order" + " " + self.name +" "+ "amounting in" +" "+ str(self.amount_total) +" "+ "has been confirmed."  "Thank you for your trust! Do not hesitate to contact us if you have any questions."
        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'odoo.whatsapp.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_user_id': self.partner_id.id, 'default_message':message_content},   
                }    
                
