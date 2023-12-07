/** @odoo-module **/

import ActionMenus from 'web.ActionMenus';
import { patch } from 'web.utils';
var rpc = require('web.rpc');
const Context = require('web.Context');
const DropdownMenu = require('web.DropdownMenu');
const Registry = require('web.Registry');


patch(ActionMenus.prototype, 'extend_action_menus/static/src/js/inherit_action_menu.js', {


    _makeReportUrls: function (action, type) {
        let url = `/report/${type}/${action.report_name}`;
        const actionContext = action.context || {};
        if (action.data && JSON.stringify(action.data) !== "{}") {
            // build a query string with `action.data` (it's the place where reports
            // using a wizard to customize the output traditionally put their options)
            const options = encodeURIComponent(JSON.stringify(action.data));
            const context = encodeURIComponent(JSON.stringify(actionContext));
            url += `?options=${options}&context=${context}`;
        } else {
            if (actionContext.active_ids) {
                url += `/${actionContext.active_ids.join(",")}`;
            }
            if (type === "html") {
                const context = encodeURIComponent(JSON.stringify(env.services.user.context));
                url += `?context=${context}`;
            }
        }
        return url;
    },

    find_printer: function(p_name){
        return qz.printers.find(p_name).then(function(found) {
                return true;
            }).catch(function(e){
                return false;
            });
        },
    get_all_printers: function(){
        return qz.printers.find().then(function(data) {
            return data
        });
    },

    get_model_popup: function(cause, list=[]){
        switch(cause){
            case 'error':
                return '<div class="modal fade" id="myModalpopup" role="dialog">'+
                '<div class="modal-dialog modal-sm">'+
                    '<div class="modal-content">'+
                        '<div class="modal-header">'+
                        `<button type="button" class="close myModalpopup-close" data-dismiss="modal" onclick="document.getElementById('myModalpopup').remove()">&times;</button>`+
                        '<h4 class="modal-title">Error</h4>'+
                        '</div>'+
                        '<div class="modal-body">'+
                        'Could Not Connect To QzTray.'+
                        '</div>'+
                        '<div class="modal-footer">'+
                        `<button type="button" class="btn btn-default myModalpopup-close" data-dismiss="modal" onclick="document.getElementById('myModalpopup').remove()">Close</button>`+
                        '</div>'+
                    '</div>'+
                    '</div>'+
                '</div>'+
                '</div>'
            case 'listing':
                var list_templ = '<select class="wk_select_printer">'
                _.each(list, p_name => {
                    list_templ += '<option>' + p_name + '</option>'
                });
                list_templ += '</select>'
            
                return '<div class="modal fade" id="myModalpopup" role="dialog">'+
                '<div class="modal-dialog modal-sm">'+
                    '<div class="modal-content">'+
                        '<div class="modal-header">'+
                        `<button type="button" class="close myModalpopup-close" data-dismiss="modal" data-target="#myModalpopup" onclick="document.getElementById('myModalpopup').remove()">&times;</button>`+
                        '<h4 class="modal-title">Select Printer</h4>'+
                        '</div>'+
                        '<div class="modal-body">'+
                        list_templ +
                        '<br/>'+
                        // '<input class="wk_set_default" type="checkbox"> Set As Default'+
                        '</div>'+
                        '<div class="modal-footer">'+
                        `<button type="button" class="btn btn-default pull-right print_now">Print</button>`+
                        '</div>'+
                    '</div>'+
                    '</div>'+
                '</div>'+
                '</div>'
        }
    },

    async _executeAction(action) {
        var self = this;
        var super_data = this._super;
        let activeIds = self.props.activeIds;
        if (self.props.isDomainSelected) {
            activeIds = await self.rpc({
                model: self.env.action.res_model,
                method: 'search',
                args: [self.props.domain],
                kwargs: {
                    limit: self.env.session.active_ids_limit,
                    context: self.props.context,
                },
            });
        }
        const activeIdsContext = {
            active_id: activeIds[0],
            active_ids: activeIds,
            active_model: self.env.action.res_model,
        };
        if (self.props.domain) {
            // keep active_domain in context for backward compatibility
            // reasons, and to allow actions to bypass the active_ids_limit
            activeIdsContext.active_domain = self.props.domain;
        }

        const context = new Context(self.props.context, activeIdsContext).eval();
        const zpl_context = new Context(self.props.context, activeIdsContext).eval();
        var data = await rpc.query({
            model: 'ir.actions.report',
            method: 'read',
            args: [[action.id]],
        })

        if (data[0]['report_user_action'] == 'send_to_printer'){
            data[0].context = context;
            var reportUrls = self._makeReportUrls(data[0], data[0]['report_type']);
            var printer_name = data[0]['printer_id'] && data[0]['printer_id'] || false;
            var zpl_report = null;
            if (data[0]['report_type'] == 'qweb-text' && data[0]['name'].search('ZPL')){
                zpl_report = true;
            }
            return qz.websocket.connect().then(function(){
                self.find_printer(printer_name[1])
                .then(function(printer_find_opr){
                    if(printer_find_opr && printer_name){
                        rpc.query({
                            model:'ir.actions.report',
                            method:'get_zpl_data',
                            args: [reportUrls, zpl_report]})
                        .then(function(zpl_data){
                            var config = qz.configs.create(printer_name[1], { altPrinting: true });
                            qz.print(config, zpl_data).catch(function(e) { 
                                console.error("--Printing Error---",e); 
                            }).finally(function(){
                                qz.websocket.disconnect();
                            });
                        })
                        .catch(function(){
                            qz.websocket.disconnect();
                        });
                    }else{
                        self.get_all_printers().then(function(get_printers_opr){
                            var model_popup = self.get_model_popup("listing", get_printers_opr)                  
                            $("#myModalpopup").remove();
                            $('body').append(model_popup);
                            $("#myModalpopup").modal('show');
                            $('.print_now').on("click", function(e){
                                var printer_name = $("select.wk_select_printer option").filter(":selected").text();
                                var args = [reportUrls, zpl_report];
                                rpc.query({
                                    model:'ir.actions.report',
                                    method:'get_zpl_data',
                                    args: args})
                                .then(function(zpl_data){
                                    var config = qz.configs.create(printer_name, { altPrinting: true });
                                    qz.print(config, zpl_data).catch(function(e) {
                                        console.error("--Printing Error---",e); 
                                    }).finally(function(){
                                        $("#myModalpopup").find(".close").click()
                                        $("#myModalpopup").remove();
                                        qz.websocket.disconnect();
                                    });
                                })
                                .catch(function(){
                                    console.log("----------6---------");
                                    qz.websocket.disconnect();
                                });
                            });
                        });
                    }
                });
            }).catch(function(e){
                qz.websocket.disconnect();
                var model_popup = self.get_model_popup("error")
                // 
                $('body').append(model_popup);
                $("#myModalpopup").modal("show");
            });
        }else{
            super_data.apply(self, arguments);
        }
    }
});




