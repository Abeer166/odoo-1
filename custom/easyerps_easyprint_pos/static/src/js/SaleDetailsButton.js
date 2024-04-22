odoo.define('point_of_sale.customSaleDetailsButton', function (require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const {Printer} = require('point_of_sale.Printer');
    const SaleDetailsButton = require('point_of_sale.SaleDetailsButton');
    const {renderToString} = require('@web/core/utils/render');
    const {Gui} = require('point_of_sale.Gui');

    const customSaleDetailsButton = (SaleDetailsButton) => {
        class customSaleDetailsButton extends SaleDetailsButton {

            async onClick() {
                // IMPROVEMENT: Perhaps put this logic in a parent component
                // so that for unit testing, we can check if this simple
                // component correctly triggers an event.
                const saleDetails = await this.rpc({
                    model: 'report.point_of_sale.report_saledetails',
                    method: 'get_sale_details',
                    args: [false, false, false, [this.env.pos.pos_session.id]],
                });
                const report = renderToString(
                    'SaleDetailsReport',
                    Object.assign({}, saleDetails, {
                        date: new Date().toLocaleString(),
                        pos: this.env.pos,
                    })
                );
                if (this.env.pos.config.pos_bluetooth_printer) {
                    const printer = new Printer(null, this.env.pos);
                    const ticketImage = await printer.htmlToImg(report);
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
                } else {
                    const printResult = await this.env.pos.proxy.printer.print_receipt(report);
                    if (!printResult.successful) {
                        await this.showPopup('ErrorPopup', {
                            title: printResult.message.title,
                            body: printResult.message.body,
                        });
                    }
                }
            }

        }

        return customSaleDetailsButton;
    };
    Registries.Component.extend(SaleDetailsButton, customSaleDetailsButton);

});
