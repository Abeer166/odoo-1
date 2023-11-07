# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models



class ir_attachment_inherit(models.Model):
    _inherit = 'ir.attachment'

    shared_user_ids = fields.Many2many('res.users','users_id_rel','attachment_id','user_id',string="Share with other",
                                       domain=lambda self: [('id', '!=', self.env.user.id)])
    
    def action_share_doc_portal(self, attach_id=False):
        if attach_id:
            res_company = self.env.company
            ir_attachment = self.env['ir.attachment'].browse(attach_id)
            if res_company.attachment_restriction == True:
                if self.env.user.id == ir_attachment.create_uid.id:
                    return True
                else:
                    return False
            else:
                return True            

    def _getModelName(self,model):
        model = self.env['ir.model'].sudo().search([('model','=',model)])
        return model.name
        
    def _remMail(self,user_ids):
        for user in self.env['res.users'].browse(user_ids):
            subject = 'Removal of Attachment from Portal'
            email_to = str(user.login)
            body = '''Dear <b>%s</b>,<br/>
            Attachment <b>%s</b> from <b>%s</b> category is removed from portal.<br/>
            Thanks<br/>
            <b>%s</b>'''%(user.name,self.name,self._getModelName(self.res_model),self.env.user.name)
            email = self.env['mail.mail'].sudo().create({'subject':subject,'email_to':email_to,'body_html':body,'auto_delete':True})
            email.send()
            
    def _addMail(self,user_ids):
        for user in self.env['res.users'].browse(user_ids):
            subject = 'Attachment shared on Portal'
            email_to = str(user.login)
            body = '''Dear <b>%s</b>,<br/>
            Attachment <b>%s</b> is shared with you on the portal.<br/>
            You can find it in <b>%s</b> category.<br/>
            Thanks<br/>
            <b>%s</b>'''%(user.name,self.name,self._getModelName(self.res_model),self.env.user.name)
            email = self.env['mail.mail'].sudo().create({'subject':subject,'email_to':email_to,'body_html':body,'auto_delete':True})
            email.send()
        

    def write(self,vals):
        if vals.get('shared_user_ids'):
            notify_shared = []
            notify_reoved = []
            existing_list = self.shared_user_ids.ids
            latest_list = vals.get('shared_user_ids')[0][2]
            for l in latest_list:
                if l not in existing_list:
                    notify_shared.append(l)
            for e in existing_list:
                if e not in latest_list:
                    notify_reoved.append(e)
            if notify_shared:
                self._addMail(notify_shared)
            if notify_reoved:
                self._remMail(notify_reoved)
        return super(ir_attachment_inherit,self).write(vals)

