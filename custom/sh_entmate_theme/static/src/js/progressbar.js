/** @odoo-module **/


import { BlockUI } from "@web/core/ui/block_ui";


import { patch } from 'web.utils';

const components = { BlockUI };


import { xml } from "@odoo/owl";

var rpc = require("web.rpc");

var progress_style = 'default';


rpc.query({
    model: 'sh.ent.theme.config.settings',
    method: 'search_read',
    domain: [['id', '=', 1]],
    fields: ['progress_style']
}).then(function (data) {
    if (data) {
        if (data[0]['progress_style'] == 'style_1') {
            progress_style = 'style_1';
        } else {
            progress_style = 'default';
        }
    }
});

patch(components.BlockUI.prototype, 'sh_entmate_theme/static/src/js/progressbar.js', {
    setup(...args) {

        this._super(...args)
    },
    block() {
        if (progress_style == 'style_1') {
            NProgress.configure({ showSpinner: false });
            NProgress.start();
        }
        this.state.blockUI = true;
        this.replaceMessage(0);

    },
   
    unblock() {
        NProgress.done();
        this.state.blockUI = false;
        clearTimeout(this.msgTimer);
        this.state.line1 = "";
        this.state.line2 = "";
    }



});

BlockUI.template = xml`
    <div t-att-class="state.blockUI ? 'o_blockUI fixed-top d-flex justify-content-center align-items-center flex-column vh-100 bg-black-50' : ''">
      <t t-if="state.blockUI">
        <div class="o_spinner mb-4">
            <img src="/web/static/img/spin.svg" alt="Loading..."/>
        </div>
        <div class="o_message text-center px-4">
            <t t-esc="state.line1"/> <br/>
            <t t-esc="state.line2"/>
        </div>
      </t>
    </div>`;
// odoo.define("sh_backmate_theme.Loading", function (require) {
//     "use strict";


//     var Loading = require('web.Loading');
//     var config = require('web.config');
//     var core = require('web.core');
//     var framework = require('web.framework');
//     var Widget = require('web.Widget');
//     var rpc = require('web.rpc');

//     var progress_style = 'none';


//     rpc.query({
//         model: 'sh.back.theme.config.settings',
//         method: 'search_read',
//         domain: [['id', '=', 1]],
//         fields: ['progress_style']
//     }).then(function (data) {
//         if (data) {
//             if (data[0]['progress_style'] == 'style_1') {
//                 progress_style = 'style_1';
//             }
//         }
//     });

//     var _t = core._t;

//     Loading.include({

//         on_rpc_event: function (increment) {

//             var self = this;
//             if (!this.count && increment === 1) {
//                 // Block UI after 3s
//                 if (progress_style == 'style_1') {
//                     NProgress.configure({ showSpinner: false });
//                     NProgress.start();
//                 }

//                 this.long_running_timer = setTimeout(function () {
//                     self.blocked_ui = true;
//                     framework.blockUI();
//                 }, 3000);
//             }

//             this.count += increment;
//             if (this.count > 0) {
//                 if (progress_style == 'none') {
//                     if (config.isDebug()) {
//                         this.$el.text(_.str.sprintf(_t("Loading (%d)"), this.count));
//                     } else {
//                         this.$el.text(_t("Loading"));
//                     }
//                     this.$el.show();
//                 }

//                 this.getParent().$el.addClass('oe_wait');
//             } else {
//                 this.count = 0;
//                 clearTimeout(this.long_running_timer);
//                 // Don't unblock if blocked by somebody else
//                 if (progress_style == 'style_1') {
//                     NProgress.done();
//                 }


//                 if (self.blocked_ui) {
//                     this.blocked_ui = false;
//                     framework.unblockUI();
//                 }
//                 this.$el.fadeOut();
//                 this.getParent().$el.removeClass('oe_wait');
//             }
//         },
//     });

// });
