/** @odoo-module **/
import { MenuDropdown, MenuItem, NavBar } from '@web/webclient/navbar/navbar';

import { patch } from 'web.utils';
// import { ProfileSection } from "@sh_backmate_theme/js/profilesection";
import { ErrorHandler, NotUpdatable } from "@web/core/utils/components";

const components = { NavBar };
var rpc = require("web.rpc");
var app_icon_style = 'style_1';
var backend_all_icon_style = 'backend_fontawesome_icon';

var config = require("web.config");
rpc.query({
    model: 'sh.ent.theme.config.settings',
    method: 'search_read',
    domain: [['id', '=', 1]],
    fields: ['app_icon_style', 'backend_all_icon_style']
}).then(function (data) {
    if (data) {
       
        if (data[0]['app_icon_style']) {
            app_icon_style = data[0]['app_icon_style'];
        }
        if (data[0]['backend_all_icon_style']) {
            backend_all_icon_style = data[0]['backend_all_icon_style'];
        }
    }
});

// console.log(" NavBar.components", NavBar.components)

// NavBar.components = { MenuDropdown, MenuItem, NotUpdatable, ErrorHandler, ProfileSection };
// console.log(" NavBar.components", NavBar.components)
patch(components.NavBar.prototype, 'sh_entmate_theme/static/src/js/navbar.js', {

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     */

    // mobileNavbarTabs(...args) {
    //     return [...this._super(...args), {
    //         icon: 'fa fa-comments',
    //         id: 'livechat',
    //         label: this.env._t("Livechat"),
    //     }];
    // }

    onNavBarDropdownItemSelection(menu) {
        if(window.event.shiftKey){
            localStorage.setItem("sh_add_tab",1)
        }else{
            localStorage.setItem("sh_add_tab",0)
        }
        if(this.websiteCustomMenus){
            const websiteMenu = this.websiteCustomMenus.get(menu.xmlid);
            if (websiteMenu) {
                return this.websiteCustomMenus.open(menu);
            }
        }
       
        if (menu) {
            this.menuService.selectMenu(menu);
            // setTimeout(() => {
            //         $("body").removeClass("sh_sidebar_background_enterprise");
            //         $(".sh_search_container").css("display", "none");
            //         $(".sh_entmate_theme_appmenu_div").removeClass("show")
            //         $(".o_action_manager").removeClass("d-none");
            //         $(".o_menu_brand").css("display", "block");
            //         $(".full").removeClass("sidebar_arrow");
            //         $(".o_menu_sections").css("display", "flex");
            // }, 500);
            return this._super(menu);
           

        }
    },
    onNavBarDropdownItemClick(ev) {
        if(ev.shiftKey){
            localStorage.setItem("sh_add_tab",1)
        }else{
            localStorage.setItem("sh_add_tab",0)
        }
    },
    getAppClassName(app){
        var app_name = app.xmlid
        return app_name.replaceAll('.', '_')
    },
    getIconStyle() {
        return app_icon_style;
    },
    getBackend_icon(){
        return backend_all_icon_style;
    },
    // getThemeStyle(ev) {
    //     return theme_style;
    // },
    isMobile(ev) {
        return config.device.isMobile;
    },
    click_secondary_submenu(ev) {
        if (config.device.isMobile) {
            $(".sh_sub_menu_div").addClass("o_hidden");
        }

        $(".o_menu_sections").removeClass("show")
    },
    click_close_submenu(ev) {

        $(".sh_sub_menu_div").addClass("o_hidden");
        $(".o_menu_sections").removeClass("show")
    },
    click_mobile_toggle(ev) {
        $(".sh_sub_menu_div").removeClass("o_hidden");

    },
    click_app_toggle(ev) {
        console.log(">>>>>>>>>>>>h_backmate_theme_appmenu_div", $(".sh_entmate_theme_appmenu_div"))
        if($(".sh_entmate_theme_appmenu_div").hasClass("sh_first_load")){
            $(".sh_entmate_theme_appmenu_div").removeClass("show")
            $(".sh_entmate_theme_appmenu_div").removeClass("sh_first_load")
        }
        if ($(".sh_entmate_theme_appmenu_div").hasClass("show")) {
            $("body").removeClass("sh_sidebar_background_enterprise");
            $(".sh_search_container").css("display", "none");

            $(".sh_entmate_theme_appmenu_div").removeClass("show")
            $(".o_action_manager").removeClass("d-none");
            $(".o_menu_brand").css("display", "block");
            $(".full").removeClass("sidebar_arrow");
            $(".o_menu_sections").css("display", "flex");
        } else {
            console.log("else....................")
            $(".sh_entmate_theme_appmenu_div").addClass("show")
            $("body").addClass("sh_sidebar_background_enterprise");
            $(".sh_entmate_theme_appmenu_div").css("opacity", "1");
            // 24-3-2023 // 
            // to fix issue of list view column width//
            // $(".o_action_manager").addClass("d-none");
            $(".full").addClass("sidebar_arrow");
            $(".o_menu_brand").css("display", "none");
            $(".o_menu_sections").css("display", "none");
        }


    },


});


