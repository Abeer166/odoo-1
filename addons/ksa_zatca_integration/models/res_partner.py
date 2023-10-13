# -*- coding: utf-8 -*-
from odoo import fields, models, exceptions, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    building_no = fields.Char('Building Number', help="https://splonline.com.sa/en/national-address-1/")
    additional_no = fields.Char('Additional Number', help="https://splonline.com.sa/en/national-address-1/")
    district = fields.Char('District')
    country_id_name = fields.Char(related="country_id.name")
    # vat = fields.Char(help="|) VAT registration number (if applicable) for the buyer and in case the buyer "
    #                        "is part of a VAT group then the VAT group Registration number should be entered."
    #                        "||) In case of tax invoice, "
    #                        "1) Not mandatory for export invoices. "
    #                        "2) Not Mandatory for internal supplies")
    # bt_46-1 (BR-KSA-14)
    buyer_identification = fields.Selection([('NAT', 'National ID'), ('IQA', 'Iqama Number'),
                                             ('PAS', 'Passport ID'),
                                             ('CRN', 'Commercial Registration number'),
                                             ('MOM', 'Momra license'), ('MLS', 'MLSD license'),
                                             ('SAG', 'Sagia license'), ('GCC', 'GCC ID'),
                                             ('OTH', 'Other OD'),
                                             ('TIN', 'Tax Identification Number'), ('700', '700 Number')],
                                            string="Buyer Identification",
                                            help="|) In case multiple IDs exist then one of the above must be entered,"
                                                 "||) In case of tax invoice, "
                                                 "      1) Not mandatory for export invoices.")
    # bt_46 (BR-KSA-14)
    buyer_identification_no = fields.Char(string="Buyer Identification Number (Other buyer ID)",
                                          help=" |) In case multiple IDs exist then one of the above must be entered,"
                                               "||) In case of tax invoice, "
                                               "      1) Not mandatory for export invoices.")

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        # BR-KSA-40
        for record in self:
            if record.vat:
                if len(str(record.vat)) != 15:
                    raise exceptions.ValidationError('Vat must be exactly 15 digits')
                if str(record.vat)[0] != '3' or str(record.vat)[-1] != '3':
                    raise exceptions.ValidationError('Vat must start/end with 3')
            # BR-KSA-65
            if record.additional_no:
                if len(str(record.additional_no)) != 4:
                    raise exceptions.ValidationError('Additional Number must be exactly 4 digits')
            # BR-KSA-67
            if record.country_id.id and record.country_id_name == 'SA' and len(str(record.zip)) != 5:
                raise exceptions.ValidationError('zip must be exactly 5 digits in case of SA')
        return res
