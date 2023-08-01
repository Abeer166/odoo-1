from odoo import models, fields, api, _
import re

class AccountMove(models.Model):
    _inherit = 'account.move'

    # whatsapp_invoice_message = fields.Char(string='Whatsapp Invoice')

    def send_invoice_whatsapp_msg(self):
        # Find the e-mail template
        invoice_url = self.get_portal_url()
        print(">>>>>>>>>>>>>>>>>>>inv_obj...............", invoice_url)
        template = self.env.ref('account.email_template_edi_invoice')
        print("<><><><><><>><>template<><<><>><><<>>><>", template)
        # You can also find the e-mail template like this:
        # template = self.env['ir.model.data'].get_object('mail_template_demo', 'example_email_template')
 
        # Send out the e-mail template to the user
        self.env['mail.template'].browse(template.id).send_mail(self.id)
        # message_content = "Hello, Your order" + " " + self.name +" "+ "amounting in" +" "+ str(self.amount_total) +" "+ "has been confirmed."  "Thank you for your trust! Do not hesitate to contact us if you have any questions."
        invoice_msg_content ="Dear"+" "+self.partner_id.name+",<br><br>"+"Here is your invoice"+" "+self.name+" "+"(with reference:"+" "+ self.invoice_origin+") amounting in"+" "+str(self.amount_total)+" "+"from My Company.<br> This invoice is already paid. Do not hesitate to contact us if you have any questions."
        # print(",.,.,.,.,.,.invoice_msg_content>>>>>>>>>>>>>>.", invoice_msg_content)
        invoice_msg = re.sub('<[^>]*>', ' ', invoice_msg_content)
        # print(",.,.,.,.,.,.invoice_msg>>>>>>>>>>>>>>.", invoice_msg)
        url_content = "  In the below link, You can see and download the invoice.  " + "http://104.248.37.2:8069"+invoice_url
        url = re.sub('<[^>]*>', ' ', url_content)
        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'odoo.whatsapp.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_user_id': self.partner_id.id, 'default_message':invoice_msg+url_content},   
                }    
                
