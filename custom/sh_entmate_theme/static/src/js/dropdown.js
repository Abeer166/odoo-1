/** @odoo-module **/
import { Dropdown } from '@web/core/dropdown/dropdown';

import { patch } from 'web.utils';
import { useBus, useService } from "@web/core/utils/hooks";
import { usePosition } from "@web/core/position_hook";
import { useDropdownNavigation } from "@web/core/dropdown/dropdown_navigation_hook";
import { localization } from "@web/core/l10n/localization";
const components = { Dropdown };
import {
    EventBus,
    onWillStart,
    useEffect,
    useExternalListener,
    useRef,
    useState,
    useChildSubEnv,
} from "@odoo/owl";

var rpc = require("web.rpc");
var config = require("web.config");
var theme_style = 'enterprise';
const DIRECTION_CARET_CLASS = {
    bottom: "dropdown",
    top: "dropup",
    left: "dropleft",
    right: "dropright",
};

export const DROPDOWN = Symbol("Dropdown");


if(config.device.isMobile){
  
    return; 
}


patch(components.Dropdown.prototype, 'sh_entmate_theme/static/src/js/dropdown.js', {

    setup() {

            this._super()
        console.log("this.props.class",this.props.class)
        if(this.props.class == 'o_navbar_apps_menu sh_first_load sh_entmate_theme_appmenu_div' && !config.device.isMobile){
                this.state = useState({
                    open: true,
                    groupIsOpen: this.props.startOpen,
                });
           
        }else{
            this.state = useState({
                open: this.props.startOpen,
                groupIsOpen: this.props.startOpen,
            });
        }
    
    },
    /**
     * Toggles the dropdown open state.
     *
     * @returns {Promise<void>}
     */
    toggle() {
console.log('.....................toggle',this.props.class)
        if (this.props.class == 'o_navbar_apps_menu sh_first_load sh_entmate_theme_appmenu_div' && !config.device.isMobile) {
            return this.changeStateAndNotify({ open: true, groupIsOpen: true });
        } else {
            const toggled = !this.state.open;
            return this.changeStateAndNotify({ open: toggled, groupIsOpen: toggled });
        }


    },
    onDropdownStateChanged(args) {
        // NProgress.configure({ showSpinner: false });
        // NProgress.start();
        console.log('this.props.title onDropdownStateChanged ',this.props.class, theme_style, config.device.isMobile )
        if(this.props.class == 'o_navbar_apps_menu sh_first_load sh_entmate_theme_appmenu_div'  && !config.device.isMobile){
            this.state.open = true;
        }
       
        if (this.rootRef.el.contains(args.emitter.rootRef.el)) {
            // Do not listen to events emitted by self or children
            return;
        }

        // Emitted by direct siblings ?
        if (args.emitter.rootRef.el.parentElement === this.rootRef.el.parentElement) {
            // Sync the group status
            this.state.groupIsOpen = args.newState.groupIsOpen;

            // Another dropdown is now open ? Close myself without notifying siblings.
            if (this.state.open && args.newState.open) {
                this.state.open = false;
            }
        } else {
            // Another dropdown is now open ? Close myself and notify the world (i.e. siblings).
            if (this.state.open && args.newState.open) {
                this.close();
            }
        }
    }

});