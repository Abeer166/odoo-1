odoo.define('pos_customer_order_history.PartnerLine', function(require) {
    'use strict';

    const PartnerLine = require('point_of_sale.PartnerLine');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");
    var core = require('web.core');
    var QWeb = core.qweb;


    const ShowHistoryPartnerLine = (PartnerLine) =>
        class ShowHistoryPartnerLine extends PartnerLine {
            setup () {
                super.setup();
                useListener('click-client-details', this.onClickShow);
            }

            async onClickShow() {
                let partner = this.props.partner;
                var symbol = this.env.pos.getCurrencySymbol();
                var fields = [];
                var domain = [
                    ['partner_id', '=', partner.id],
                    ['partner_id', '!=', false]
                ];
                let partner_orders = await this.env.services.rpc({
                    model: 'pos.order',
                    method: 'search_read',
                    args: [domain],
                    limit: 5
                });
                var order_list = [];
                var order_line = [];
                _.each(partner_orders, function(order, index) {
                    order_list.push(order.id);
                });
                domain = [
                    ['order_id.partner_id', '=', partner.id],
                    ['order_id', 'in', order_list]
                ];
                fields = [];
                let partner_order_lines = await this.env.services.rpc({
                        model: 'pos.order.line',
                        method: 'search_read',
                        args: [domain],
                    });
                var line_name = [];
                _.each(partner_order_lines, function(line) {
                    if (line_name.indexOf(line.order_id[1]) > -1) {
                        var rec_line = {
                            'product': line.display_name,
                            'qty': line.qty,
                            'amount': symbol + ' ' + line.price_subtotal_incl,
                        }
                        order_line.push(rec_line);
                    } else {
                        line_name.push(line.order_id[1]);
                        var line_heading = {
                            'no': line_name.length,
                            'order_name': line.order_id[1],
                            'order_time': line.write_date,
                            'line_heading': true
                        }
                        order_line.push(line_heading);
                        var rec_line = {
                            'product': line.display_name,
                            'qty': line.qty,
                            'amount': symbol + ' ' + line.price_subtotal_incl,
                        }
                        order_line.push(rec_line);
                    }
                });
                partner['lines'] = order_line;
                $('.client_details_container').remove();
                $('.full-content').removeAttr('style');
                $('.full-content').attr('style', 'top:215px;');
                $('.full-content').before($(QWeb.render('ClientDetails', { widget: this, partner: partner })));

            }
        }

    Registries.Component.extend(PartnerLine, ShowHistoryPartnerLine);

});