odoo.define('point_of_sale.customReprintReceiptScreen', function (require) {
    'use strict';
    const {Printer} = require('point_of_sale.Printer');
    const ReprintReceiptScreen = require('point_of_sale.ReprintReceiptScreen');
    const Registries = require('point_of_sale.Registries');
    const {Gui} = require('point_of_sale.Gui');

    const customReprintReceiptScreen = (ReprintReceiptScreen) => {
        class customReprintReceiptScreen extends ReprintReceiptScreen {

            get compute_product() {
                var add = [];
                var product = this.props.order.get_orderlines();
                if (product.length > 0) {
                    if (this.env.pos.config.receipt_types_views === "labelReceipt") {
                        for (var n = 0; n < product.length; n++) {
                            for (var nq = 0; nq < product[n].quantity; nq++) {
                                add.push(product[n])
                            }
                        }
                    }
                }
                return {
                    'products': add,

                };
            }

            async printReceiptAndLabel() {
                if (this.env.pos.config.pos_bluetooth_printer) {
                    const printer = new Printer(null, this.env.pos);
                    var xhttp = new XMLHttpRequest();
                    const timer = ms => new Promise(res => setTimeout(res, ms))
                    for (var i = 0; i < $(".pos-receipt").length; i++) {
                        const receiptString = $(".pos-receipt")[i].outerHTML;
                        const ticketImage = await printer.htmlToImg(receiptString);
                        if (window.PrintImage) {
                            if (window.EasyLoading) {
                                EasyLoading.postMessage("");
                            }
                            // console.log(image_64);
                            var message = JSON.stringify({
                                'data': ticketImage,
                                'cutter': true,
                                "method": "PrintImage",
                                "printerNo": "printer_01",
                            });
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

                    }

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
                } else if (this.env.pos.proxy.printer && this.env.pos.config.iface_print_skip_screen) {
                    let result = await this._printReceipt();
                    if (result)
                        this.showScreen('TicketScreen', {reuseSavedUIState: true});
                }
            }

            async printLabel() {
                if (this.env.pos.config.pos_bluetooth_printer) {
                    const printer = new Printer(null, this.env.pos);
                    var xhttp = new XMLHttpRequest();
                    let i = 1;
                    const timer = ms => new Promise(res => setTimeout(res, ms))
                    while (i < $(".pos-receipt").length) {
                        const receiptString = $(".pos-receipt")[i].outerHTML;
                        const ticketImage = await printer.htmlToImg(receiptString);
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
                        i++;
                    }

                }

            }

        }

        return customReprintReceiptScreen;
    };
    Registries.Component.extend(ReprintReceiptScreen, customReprintReceiptScreen);

});
