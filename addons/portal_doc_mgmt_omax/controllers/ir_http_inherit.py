# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields as odoo_fields, http, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError, AccessDenied
from odoo.http import content_disposition, Controller, request, route
from odoo.tools import file_open, file_path, replace_exceptions
from odoo.addons.web.controllers.binary import Binary


class CustomeBinary(Binary):
        
    @http.route(['/web/content',
        '/web/content/<string:xmlid>',
        '/web/content/<string:xmlid>/<string:filename>',
        '/web/content/<int:id>',
        '/web/content/<int:id>/<string:filename>',
        '/web/content/<string:model>/<int:id>/<string:field>',
        '/web/content/<string:model>/<int:id>/<string:field>/<string:filename>'], type='http', auth="public")

    def content_common(self, xmlid=None, model='ir.attachment', id=None, field='raw',
                       filename=None, filename_field='name', mimetype=None, unique=False,
                       download=False, access_token=None, nocache=False, portal=False):    

        if portal:
            portal = int(portal)
            if portal == request.session.uid:
                with replace_exceptions(UserError, by=request.not_found()):
                    record = request.env['ir.binary'].sudo()._find_record(xmlid, model, id and int(id), access_token)
                    stream = request.env['ir.binary'].sudo()._get_stream_from(record, field, filename, filename_field, mimetype)
        else:
            with replace_exceptions(UserError, by=request.not_found()):
                record = request.env['ir.binary']._find_record(xmlid, model, id and int(id), access_token)
                stream = request.env['ir.binary']._get_stream_from(record, field, filename, filename_field, mimetype)
        send_file_kwargs = {'as_attachment': download}
        if unique:
            send_file_kwargs['immutable'] = True
            send_file_kwargs['max_age'] = http.STATIC_CACHE_LONG
        if nocache:
            send_file_kwargs['max_age'] = None

        return stream.get_response(**send_file_kwargs)




