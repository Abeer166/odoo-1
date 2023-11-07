odoo.define("sh_electronic_pos_qr_saudi.ReceiptScreen", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const ReceiptScreen = require("point_of_sale.ReceiptScreen");
    // const { useRef, useContext } = owl.hooks;
    const { useRef } = owl;
    const { onMounted } = owl;
    var core = require('web.core');
    var _t = core._t;

    const PosResOrderReceipt = (ReceiptScreen) =>
    class extends ReceiptScreen {
        setup() {
            super.setup();
            this.shorderReceipt = useRef('order-receipt');
            onMounted(this.onMounted);
        }
        compute_sa_qr_code(name, vat, date_isostring, amount_total, amount_tax) {
            /* Generate the qr code for Saudi e-invoicing. Specs are available at the following link at page 23
            https://zatca.gov.sa/ar/E-Invoicing/SystemsDevelopers/Documents/20210528_ZATCA_Electronic_Invoice_Security_Features_Implementation_Standards_vShared.pdf
            */
            const seller_name_enc = this._compute_qr_code_field(1, name);
            const company_vat_enc = this._compute_qr_code_field(2, vat);
            const timestamp_enc = this._compute_qr_code_field(3, date_isostring);
            const invoice_total_enc = this._compute_qr_code_field(4, amount_total.toString());
            const total_vat_enc = this._compute_qr_code_field(5, amount_tax.toString());

            const str_to_encode = seller_name_enc.concat(company_vat_enc, timestamp_enc, invoice_total_enc, total_vat_enc);

            let binary = '';
            for (let i = 0; i < str_to_encode.length; i++) {
                binary += String.fromCharCode(str_to_encode[i]);
            }
            return btoa(binary);
        }

        _compute_qr_code_field(tag, field) {
            const textEncoder = new TextEncoder();
            const name_byte_array = Array.from(textEncoder.encode(field));
            const name_tag_encoding = [tag];
            const name_length_encoding = [name_byte_array.length];
            return name_tag_encoding.concat(name_length_encoding, name_byte_array);
        }
        onMounted() {
            var self = this;
            var dic = {}
            var is_gcc_country = ['SA', 'AE', 'BH', 'OM', 'QA', 'KW'].includes(self.env.pos.company.country.code);
            if (self.env.pos.config.display_qr_code && is_gcc_country) {
                $('.pos-receipt-container').addClass('sh_receipt_content')
            }
            if (_t.database.parameters.direction) {
                $('.sh_receipt_content').css('direction', 'ltr')
            }
            var qr_code = this.compute_sa_qr_code(self.env.pos.company.name, self.env.pos.company.vat, self.env.pos.get_order().export_for_printing().date.isostring, self.env.pos.get_order().export_for_printing().total_with_tax, self.env.pos.get_order().export_for_printing().total_tax);
            if ($('#qr_image') && $('#qr_image').length > 0) {
                // Create QRCode Object

                var div = document.createElement('div')
                new QRCode(div, { text: qr_code });

                var can = $(div).find('canvas')[0]
                var img = new Image();
                img.src = can.toDataURL();

                $(img).css({ 'height': self.env.pos.config.qr_code_height, 'width': self.env.pos.config.qr_code_width })
                $('#qr_image').append(img)

            }
        }
        async _sendReceiptToCustomer() {
            super._sendReceiptToCustomer(this, arguments)
            const receiptString = this.shorderReceipt.comp.el.outerHTML;
        }
    };
    Registries.Component.extend(ReceiptScreen, PosResOrderReceipt);

});
