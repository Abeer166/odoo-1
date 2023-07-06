odoo.define('dps_pos_hide_cash_control.chrome', function(require) {
	"use strict";

	const { Printer } = require('point_of_sale.Printer');
	const Chrome = require('point_of_sale.Chrome');
	const Registries = require('point_of_sale.Registries');

	const maiChrome = Chrome => 
		class extends Chrome {
			constructor() {
				super(...arguments);
			}

			openCashControl() {
	            if (this.shouldShowCashControl()) {
	                if(!this.env.pos.config.allow_show_popup){
		                this.env.pos.pos_session.state = 'opened';
		                console.log(this.env.pos,"openCashControl==========",this.env.pos.bank_statement)
		                this.rpc({
		                       model: 'pos.session',
		                        method: 'set_cashbox_pos',
		                        args: [this.env.pos.pos_session.id, this.env.pos.pos_session.cash_register_balance_start, ''],
		                    });
	                }else{
	                	this.showPopup('CashOpeningPopup', { notEscapable: true });
	                }
	            }
	        }

	};

	Registries.Component.extend(Chrome, maiChrome);
	return Chrome;
});