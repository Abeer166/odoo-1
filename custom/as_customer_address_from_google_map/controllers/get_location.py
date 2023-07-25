import logging

from odoo import http
from odoo.http import request
from odoo import http, SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo import fields


class Google_Map(http.Controller):

    @http.route(['/set_current_location_name_contact/'], type='json', auth="public")
    def set_current_location_name_contact(self, **post):
        active_id = post.get('active_id')
        location_name = post.get('location_name')
        addres_component_length = post.get('addres_component_length')
        address = post.get('address')
        latitude = post.get('latitude')
        longitude = post.get('longitude')
        get_partner_rec = request.env['res.partner'].sudo().browse(int(active_id))
        try:
            if addres_component_length:
                perfect_address = {
                    'street' : False,
                    'street2' : False,
                    'city' : False,
                    'state_id' : False,
                    'country_id' : False,
                    'zip' : False,
                    'location_name': location_name,
                    'partner_latitude': latitude,
                    'partner_longitude': longitude,
                    'date_localization': fields.Datetime.now()
                }
                for i in range(0, addres_component_length):
                    if address[i].get('types')[0] == 'administrative_area_level_3':
                        perfect_address.update({'city': address[i].get('long_name') or False})
                    elif address[i].get('types')[0] == 'administrative_area_level_1':
                        state_id = request.env['res.country.state'].search([('name', '=ilike', address[i].get('long_name'))])
                        perfect_address.update({'state_id': state_id.id or False})
                    elif address[i].get('types')[0] == 'country':
                        country_id = request.env['res.country'].search([('name', '=ilike', address[i].get('long_name'))])
                        perfect_address.update({'country_id': country_id.id or False})
                    elif address[i].get('types')[0] == 'postal_code':
                        perfect_address.update({'zip': address[i].get('long_name') or False})


                location_list = location_name.split(', ')
                index = location_list.index(perfect_address['city'])

                if index:
                    location_list.pop(index)
                country = request.env['res.country'].browse(perfect_address['country_id']).name
                index1 = location_list.index(country)
                if index1:
                    location_list.pop(index1)

                remove_state = location_list.pop(-1)

                perfect_address.update({'street': ', '.join(location_list[:2])})
                perfect_address.update({'street2': ', '.join(location_list[2:])})

                if perfect_address and get_partner_rec:
                    get_partner_rec.update(perfect_address)
        except:
            pass
        return True