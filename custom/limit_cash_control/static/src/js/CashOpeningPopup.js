odoo.define('limit_cash_control.CashOpeningPopup', function (require) {
    "use strict";
    const { useState } = owl;
    const CashOpeningPopup = require('point_of_sale.CashOpeningPopup');
    const Registries = require("point_of_sale.Registries")

    const CashOpeningZero = (CashOpeningPopup) =>
        class extends CashOpeningPopup {
            setup() {
                super.setup();
                if (this.env.pos.config.allow_default_cash) {
                    this.state = useState({
                        notes: "",
                        openingCash: this.env.pos.config.default_opening,
                    });
                }
            }
        };

    Registries.Component.extend(CashOpeningPopup, CashOpeningZero);

    return CashOpeningZero
});