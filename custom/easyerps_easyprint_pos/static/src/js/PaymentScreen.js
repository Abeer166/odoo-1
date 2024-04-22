odoo.define('point_of_sale.customPaymentScreen', function (require) {
    'use strict';
    const {Printer} = require('point_of_sale.Printer');
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const {isConnectionError} = require('point_of_sale.utils');
    const {Gui} = require('point_of_sale.Gui');


    const customPaymentScreen = (PaymentScreen) => {
        class customPaymentScreen extends PaymentScreen {

            bluetoothOpenCashbox() {
                var self = this;
                if (self.env.pos.config.pos_bluetooth_printer) {
                    if (window.OpenDrawer) {
                        OpenDrawer.postMessage(message);
                    } else {
                        var socket = new WebSocket("ws://localhost:9200");
                        socket.onopen = function () {
                            socket.send(JSON.stringify({
                                "method": "OpenDrawer",
                                // "papercut": "true",
                            }));
                            socket.close();
                        };
                        socket.onerror = function (err) {
                            return Gui.showPopup('ErrorPopup', {
                                title: _t(''),
                                body: _t("Can't concat to the Easy Print"),
                            });
                        };
                    }
                } else {
                    this.env.pos.proxy.printer.open_cashbox();
                }
            }


        }

        return customPaymentScreen;
    };
    Registries.Component.extend(PaymentScreen, customPaymentScreen);

});
