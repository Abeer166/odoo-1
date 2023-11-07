odoo.define('pos_auto_register.ClosePosPopup', function (require) {
    "use strict";

    const ClosePosPopup = require('point_of_sale.ClosePosPopup');
    const Registries = require("point_of_sale.Registries");


    const ClosePosPopupAuto = (ClosePosPopup) =>
        class extends ClosePosPopup {
            //@override
            async confirm() {
                console.log('limit control2');
                if (this.env.pos.config.hide_closing) {
                    if (this.cashControl) {
                        this.state.payments[this.defaultCashDetails.id] = { counted: this.env.pos.round_decimals_currency(this.defaultCashDetails.amount), difference: 0, number: this.defaultCashDetails.amount };
                    }
                    this.closeSession();
                } else{
                    super.confirm();
                }
            }
        };

    Registries.Component.extend(ClosePosPopup, ClosePosPopupAuto);

    return ClosePosPopup
});
