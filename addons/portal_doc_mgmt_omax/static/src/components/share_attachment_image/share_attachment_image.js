/** @odoo-module **/

import {AttachmentCard} from "@mail/components/attachment_card/attachment_card";
import {AttachmentImage} from "@mail/components/attachment_image/attachment_image";

const components = {AttachmentCard};
const component = {AttachmentImage};

import buildQuery from "web.rpc";
import {patch} from "@web/core/utils/patch";

patch(
    components.AttachmentCard.prototype,
    "portal_doc_mgmt_omax/static/src/components/share_attachment_image/share_attachment_image.js",
    {
        _onClickShare: function(ev) {
            ev.stopPropagation();
            var attachmentId = $(ev.currentTarget).data('id');
            var self = this;
            buildQuery.query({
                model: 'ir.attachment',
                method: "action_share_doc_portal",
                args: [[]],
                kwargs: {
                    attach_id: attachmentId,
                },
                context: {},
            }).then(function (res) {
                if(res){
                    var res_model = 'ir.attachment';
                    if (res_model && attachmentId) {
                        const action = {
                                type: 'ir.actions.act_window',
                                res_model: res_model,
                                res_id: attachmentId,
                                views: [[false, 'form']],
                                target: 'current'
                            };
                        const options = {};
                        self.env.services.action.doAction(action, options);
                    }
                }
                else {
                    alert("You can't share the document which are not owned by you.");
                }
            });
        }
    }
);

patch(   
    component.AttachmentImage.prototype,
    "portal_doc_mgmt_omax/static/src/components/share_attachment_image/share_attachment_image.js",
    {
        _onClickShare: function(ev) {
            ev.stopPropagation();
            var attachmentId = $(ev.currentTarget).data('id');
            var self = this;
            buildQuery.query({
                model: 'ir.attachment',
                method: "action_share_doc_portal",
                args: [[]],
                kwargs: {
                    attach_id: attachmentId,
                },
                context: {},
            }).then(function (res) {
                if(res){
                    var res_model = 'ir.attachment';
                    if (res_model && attachmentId) {
                        const action = {
                                type: 'ir.actions.act_window',
                                res_model: res_model,
                                res_id: attachmentId,
                                views: [[false, 'form']],
                                target: 'current'
                            };
                        const options = {};
                        self.env.services.action.doAction(action, options);
                    }
                }
                else {
                    alert("You can't share the document which are not owned by you.");
                }
            });
        }
    }
);
