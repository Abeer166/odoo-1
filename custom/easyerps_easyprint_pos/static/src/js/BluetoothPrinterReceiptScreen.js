odoo.define('BluetoothPrinterReceiptScreen', function (require) {
    "use strict";

    const {Printer} = require('point_of_sale.Printer');
    const Registries = require('point_of_sale.Registries');
    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const {Gui} = require('point_of_sale.Gui');
    const core = require('web.core');
    var _t = core._t;

    const customReceiptScreen = ReceiptScreen => {
        class customReceiptScreen extends ReceiptScreen {

            get currentOrder() {
                return this.env.pos.get_order();
            }

            get_is_openCashDrawer() {
                return this.currentOrder.is_paid_with_cash() || this.currentOrder.get_change();
            }

            async handleAutoPrint() {
                if (this._shouldAutoPrint()) {
                    if (this.env.pos.config.bluetooth_print_auto) {
                        await this.printReceiptAndLabel();
                        if (this.currentOrder._printed && this._shouldCloseImmediately()) {
                            this.whenClosing();
                        }
                    } else {
                        await this.printReceipt();
                        if (this.currentOrder._printed && this._shouldCloseImmediately()) {
                            this.whenClosing();
                        }
                    }

                }
            }

            async printReceiptAndLabel() {
                var self = this
                if (this.env.pos.config.pos_bluetooth_printer) {
                    this.printReceipt()
                    setTimeout(function () {
                            self.printLabel()
                        }
                        , 500
                    )

                }

            }

            async printReceipt() {
                var self = this;
                if (!self.env.pos.config.pos_bluetooth_printer) {
                    return super.printReceipt()
                }
                if (self.env.pos.config.pos_bluetooth_printer) {
                    const printer = new Printer(null, this.env.pos);
                    const receiptString = this.orderReceipt.el.innerHTML;
                    const ticketImage = await printer.htmlToImg(receiptString);
                    if (window.PrintImage) {
                        if (window.EasyLoading) {
                            EasyLoading.postMessage("");
                        }
                        // console.log(image_64);
                        var message = JSON.stringify({
                            'data': ticketImage, 'cutter': true, "method": "PrintImage",
                            "printerNo": "printer_01",
                        });
                        // if (this.get_is_openCashDrawer) {
                        //     if (window.OpenDrawer) {
                        //         OpenDrawer.postMessage(message);
                        //     }
                        // }
                        await PrintImage.postMessage(message);
                    } else {
                        var socket = new WebSocket("ws://localhost:9200");
                        socket.onopen = function () {
                            socket.send(JSON.stringify({
                                "method": "PrintImage",
                                "printerNo": "printer_01",
                                "data": ticketImage,
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
                    const isPrinted = await this._printReceipt();
                    if (isPrinted) {
                        this.currentOrder._printed = true;
                    }
                }
            }

            async printLabel() {
                if (this.env.pos.config.pos_bluetooth_printer) {
                    const printer = new Printer(null, this.env.pos);
                    let i = 1;
                    const timer = ms => new Promise(res => setTimeout(res, ms))
                    while (i < $(".pos-receipt").length) {
                        const receiptString = $(".pos-receipt")[i].outerHTML;
                        const ticketImage = await printer.htmlToImg(receiptString);
                        if (window.PrintImage) {
                            if (window.EasyLoading) {
                                EasyLoading.postMessage("");
                            }
                            var message = JSON.stringify({
                                'data': ticketImage,
                                'cutter': true,
                                "method": "PrintImage",
                                "printerNo": "printer_01",
                            });
                            // if (this.get_is_openCashDrawer) {
                            //     if (window.OpenDrawer) {
                            //         OpenDrawer.postMessage(message);
                            //     }
                            // }
                            await PrintImage.postMessage(message);
                        } else {
                            const copie = this.env.pos.config.receipt_copies;
                            var socket = new WebSocket("ws://localhost:9200");
                            if (!this.env.pos.config.is_different_printer) {
                                socket.onopen = function () {
                                    socket.send(JSON.stringify({
                                        "method": "PrintImage",
                                        "printerNo": "printer_01",
                                        "data": ticketImage,
                                        // "papercut": "true",
                                    }));
                                    socket.close();
                                };
                            } else {
                                socket.onopen = function () {
                                    socket.send(JSON.stringify({
                                        "method": "PrintImage",
                                        "printerNo": "printer_02",
                                        "data": ticketImage,
                                        // "papercut": "true",
                                    }));
                                    socket.close();
                                };
                            }
                            socket.onerror = function (err) {
                                return Gui.showPopup('ErrorPopup', {
                                    title: _t(''),
                                    body: _t("Can't concat to the Easy Print"),
                                });
                            };
                        }
                        i++;

                    }

                }

            }


        }

        return customReceiptScreen;
    };


    Registries.Component.extend(ReceiptScreen, customReceiptScreen);

});

