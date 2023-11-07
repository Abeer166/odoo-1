odoo.define("sh_electronic_pos_qr_saudi.models", function (require) {
    "use strict";
    
    var core = require('web.core');
    const { PosGlobalState, Order, Orderline, Payment } = require('point_of_sale.models');
    var _t = core._t;
    const Registries = require("point_of_sale.Registries");

    const shSaudiPosGlobalState = (PosGlobalState) => class shSaudiPosGlobalState extends PosGlobalState {

        async _processData(loadedData) {
            await super._processData(...arguments);
            var self = this
            if(loadedData && loadedData['sh.pos.config.qr.elements']){
                self.db.all_qr_elemets = loadedData['sh.pos.config.qr.elements'];
                if (loadedData['sh.pos.config.qr.elements'] && loadedData['sh.pos.config.qr.elements'].length > 0) {
                    _.each(loadedData['sh.pos.config.qr.elements'], function (each_qr_element) {
                        self.db.qr_elemet_by_id[each_qr_element.id] = each_qr_element
                    });
                }
            }
        }
        
    }

    Registries.Model.extend(PosGlobalState, shSaudiPosGlobalState);

    const shSaudiPosOrder = (Order) => class shSaudiPosOrder extends Order {
        constructor(obj, options) {
            super(...arguments);
            this.return_order_ref = [];
        }
        set_refunded_order_ref(return_order_ref_data) {
        	this.return_order_ref.push(return_order_ref_data)
        }
        get_refunded_order_ref () {
            return this.return_order_ref;
        }
    }

    Registries.Model.extend(Order, shSaudiPosOrder);

    const shSaudiPosOrderline = (Orderline) => class shSaudiPosOrderline extends Orderline {
        export_for_printing() {
            var res = super.export_for_printing(...arguments);
            res['sh_arabic_name'] = this.get_product().sh_arabic_name;
            res['line_note'] = this.note;
            return res
        }
    }

    Registries.Model.extend(Orderline, shSaudiPosOrderline);

    const shSaudiPosPaymentline = (Payment) => class shSaudiPosPaymentline extends Payment {
        export_for_printing() {
            var res = super.export_for_printing(...arguments);
            res['sh_payment_method_arabic_name'] = this.payment_method.sh_payment_method_arabic_name
            return res
        }
    }

    Registries.Model.extend(Payment, shSaudiPosPaymentline);
    
});
