odoo.define('dps_pos_hide_cash_control.MaiClosePopup', function(require) {
	"use strict";

	const { Printer } = require('point_of_sale.Printer');
	const HeaderButton = require('point_of_sale.HeaderButton');
	const Registries = require('point_of_sale.Registries');

	const MaiHeaderButton = HeaderButton => 
		class extends HeaderButton {
			constructor() {
				super(...arguments);
			}

			async onClick() {
	            const info = await this.env.pos.getClosePosInfo();
	            let response;
	            if(!this.env.pos.config.allow_show_popup){
	                if (info.cashControl) {
	                     response = await this.rpc({
	                        model: 'pos.session',
	                        method: 'post_closing_cash_details',
	                        args: [this.env.pos.pos_session.id],
	                        kwargs: {
	                            counted_cash: info.paymentsAmount,
	                        }
	                    })
	                    if (!response.successful) {
	                        return this.handleClosingError(response);
	                    }
	                }

	                await this.rpc({
	                    model: 'pos.session',
	                    method: 'update_closing_control_state_session',
	                    args: [this.env.pos.pos_session.id,'']
	                })

	                try {
	                    const bankPaymentMethodDiffPairs = info.otherPaymentMethods
	                        .filter((pm) => pm.type == 'bank')
	                        .map((pm) => [pm.id, info.state.payments[pm.id].difference]);
	                    response = await this.rpc({
	                        model: 'pos.session',
	                        method: 'close_session_from_ui',
	                        args: [this.env.pos.pos_session.id, bankPaymentMethodDiffPairs],
	                        context: this.env.session.user_context,
	                    });
	                    if (!response.successful) {
	                        return this.handleClosingError(response);
	                    }
	                    window.location = '/web#action=point_of_sale.action_client_pos_menu';
	                } catch (error) {
	                    const iError = identifyError(error);
	                    if (iError instanceof ConnectionLostError || iError instanceof ConnectionAbortedError) {
	                        await this.showPopup('ErrorPopup', {
	                            title: this.env._t('Network Error'),
	                            body: this.env._t('Cannot close the session when offline.'),
	                        });
	                    } else {
	                        await this.showPopup('ErrorPopup', {
	                            title: this.env._t('Closing session error'),
	                            body: this.env._t(
	                                'An error has occurred when trying to close the session.\n' +
	                                'You will be redirected to the back-end to manually close the session.')
	                        })
	                        window.location = '/web#action=point_of_sale.action_client_pos_menu';
	                    }
	                }
	            }else{
	                this.showPopup('ClosePosPopup', { info: info });
	            }
	        }

	};

	Registries.Component.extend(HeaderButton, MaiHeaderButton);
	return HeaderButton;
});