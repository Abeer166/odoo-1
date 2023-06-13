odoo.define("sh_electronic_pos_qr_saudi.db", function (require) {
    "use strict";

    var DB = require("point_of_sale.DB");

    DB.include({
        init: function (options) {
            this._super.apply(this, arguments);
            this.qr_elemet_by_id = {};
        },
    });
    
});
