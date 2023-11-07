odoo.define("sh_electronic_pos_qr_saudi.TicketScreen", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const TicketScreen = require("point_of_sale.TicketScreen");

    const PosTicketScreen = (TicketScreen) =>
    class extends TicketScreen {
    	async _onDoRefund() {
    		super._onDoRefund()
    		var self = this;
    		const order = this.getSelectedSyncedOrder();
    		if(self.env.pos.get_order().getHasRefundLines() && order && self.env.pos.config.show_return_order_ref){
    			self.env.pos.get_order().set_refunded_order_ref(order.name)
    		}
    	}
    };

    Registries.Component.extend(TicketScreen, PosTicketScreen);
});
