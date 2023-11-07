# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "EnterpriseMate Backend Theme [For Community Edition]",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "license": "OPL-1",
    "category": "Themes/Backend",
    "version": "16.0.7",
    "summary": "Enterprise Backend Theme, Enterprise Theme, Backend Enterprise Theme, Flexible Enterprise Theme, Enter prise Theme Odoo",
    "description": """Do you want odoo enterpise look in your community version? Are You looking for modern, creative, clean, clear, materialise odoo enterpise look theme for your backend? So you are at the right place, We have made sure that this theme is highly clean, modern, fully customizable enterprise look theme. Cheers!""",
    "depends":
    [
        "web",
        "mail"
    ],

    "data":
    [
        "data/theme_config_data.xml",
        "data/pwa_configuraion_data.xml",
        "security/base_security.xml",
        "security/ir.model.access.csv",
        "views/views.xml",
        "views/pwa_configuration_view.xml",
        "views/assets.xml",
        "views/login_layout.xml",
        "views/notifications_view.xml",
        "views/send_notifications.xml",
        "views/web_push_notification.xml",
        "views/ent_theme_config_view.xml",
        "views/global_search_view.xml",
        "wizard/theme_preview_wizard.xml", 
    ],

    'assets': {

        'web.assets_backend': [

            'sh_entmate_theme/static/src/scss/fonts.scss',
            'sh_entmate_theme/static/src/scss/switch_button.scss',
            'sh_entmate_theme/static/src/scss/theme.scss',
            'sh_entmate_theme/static/src/scss/font.scss',

            #button_style
            'sh_entmate_theme/static/src/scss/buttons.scss',

            # background type color/image
            'sh_entmate_theme/static/src/scss/background-img.scss',
            'sh_entmate_theme/static/src/scss/background-color.scss',

            # separator
            'sh_entmate_theme/static/src/scss/separtor.scss',

            # navbar
            'sh_entmate_theme/static/src/scss/navbar.scss',

            # form view
            'sh_entmate_theme/static/src/scss/form_view.scss',

            # sidebar
            'sh_entmate_theme/static/src/scss/sidebar.scss',

            # responsive
            'sh_entmate_theme/static/src/scss/responsive.scss',

            # popup animation style
            'sh_entmate_theme/static/src/scss/popup_style.scss',

            # profile menu for mobile view
            'sh_entmate_theme/static/src/scss/menu_mobile.scss',

            # 'sh_entmate_theme/static/src/js/control_panel.js',
            # 'sh_entmate_theme/static/src/js/vertical_pen.js',

            # form element style
            'sh_entmate_theme/static/src/scss/form_element_style.scss',
            # 'sh_entmate_theme/static/src/scss/chatter_position.scss',


            # notification style
            'sh_entmate_theme/static/src/scss/notification.scss',

            # breadcrumb style
            'sh_entmate_theme/static/src/scss/breadcrumb.scss',

            # loader style
            'sh_entmate_theme/static/src/scss/loader.scss',

            # checkbox style 
            'sh_entmate_theme/static/src/scss/checkbox_style/checkbox_style.scss',

            # radio button style
            'sh_entmate_theme/static/src/scss/radio_btn_style/radio_btn_style.scss',

            # scrollbar style
            'sh_entmate_theme/static/src/scss/scrollbar/scrollbar_style.scss',

            # predefined list view style
            'sh_entmate_theme/static/src/scss/predefine_list_view/predefine_list_view.scss',

            # icon_style
            'sh_entmate_theme/static/src/scss/font_awesome_light_icon.scss',
            'sh_entmate_theme/static/src/scss/font_awesome_regular_icon.scss',
            'sh_entmate_theme/static/src/scss/font_awesome_std_icon.scss',
            'sh_entmate_theme/static/src/scss/font_awesome_thin_icon.scss',
            "sh_entmate_theme/static/src/scss/oi_light_icon.scss",
            "sh_entmate_theme/static/src/scss/oi_regular_icon.scss",
            "sh_entmate_theme/static/src/scss/oi_thin_icon.scss",
            'sh_entmate_theme/static/src/scss/style.css',
            'sh_entmate_theme/static/src/scss/icon_style/icon_style.scss',

            # progressbar
            'sh_entmate_theme/static/src/scss/nprogress.scss',
            

            # 'sh_entmate_theme/static/src/js/action_container.js',
            'sh_entmate_theme/static/src/js/menu_service.js',
            # "sh_entmate_theme/static/src/xml/sh_thread.xml",
            # "sh_entmate_theme/static/src/xml/form_view.xml",
            # "sh_entmate_theme/static/src/xml/widget.xml",
            # "sh_entmate_theme/static/src/xml/base.xml",

            # Menu Structure
            "sh_entmate_theme/static/src/xml/menu.xml",
            'sh_entmate_theme/static/src/js/navbar.js',

            # Full form width
            "sh_entmate_theme/static/src/js/FullFormWidth.js",
            'sh_entmate_theme/static/src/scss/form_full_width.scss',

            # Odoo standard js
            'sh_entmate_theme/static/src/js/route_service.js',
            'sh_entmate_theme/static/src/js/action_service.js',
            'sh_entmate_theme/static/src/js/dropdown.js',

            # On refresh custom js
            "sh_entmate_theme/static/src/js/On_refresh.js",

            # Progress bar and loading
            "sh_entmate_theme/static/src/js/nprogress.js",
            'sh_entmate_theme/static/src/js/progressbar.js',

            # Refresh Feature
            "sh_entmate_theme/static/src/js/kanban_controller.js",
            'sh_entmate_theme/static/src/js/list_controller.js',
            'sh_entmate_theme/static/src/js/calendar_controller.js',
            "sh_entmate_theme/static/src/xml/refresh.xml",
            'sh_entmate_theme/static/src/scss/refresh_page.scss',

            # Quick Menu Feature
            'sh_entmate_theme/static/src/js/quick_menu.js',
            "sh_entmate_theme/static/src/xml/web_quick_menu.xml",
            'sh_entmate_theme/static/src/scss/quick_menu.scss',

            # Calculator
            'sh_entmate_theme/static/src/js/calculator.js',
            "sh_entmate_theme/static/src/xml/Calculator.xml",
            'sh_entmate_theme/static/src/scss/calculator.scss',

            # FullScreen
            "sh_entmate_theme/static/src/js/fullscreen.js",
            "sh_entmate_theme/static/src/xml/FullScreen.xml",

            # Language
            'sh_entmate_theme/static/src/js/language_selector.js',
            "sh_entmate_theme/static/src/xml/Language.xml",

            # Todo feature
            "sh_entmate_theme/static/src/js/todo_widget.js",
            'sh_entmate_theme/static/src/js/todo.js',
            "sh_entmate_theme/static/src/xml/todo.xml",
            'sh_entmate_theme/static/src/scss/todo/todo.scss',

            # Global Search
            'sh_entmate_theme/static/src/js/global_search.js',
            'sh_entmate_theme/static/src/scss/global_search.scss',
            "sh_entmate_theme/static/src/xml/global_search.xml",

            # Zoom Widget
            "sh_entmate_theme/static/src/webclient/web_client.js",
            "sh_entmate_theme/static/src/webclient/zoomwidget/zoomwidget.js",
            "sh_entmate_theme/static/src/xml/Zoom.xml",
            'sh_entmate_theme/static/src/scss/zoom_in_out/zoom_in_out.scss',

            # Night Mode
            'sh_entmate_theme/static/src/js/night_mode.js',
            'sh_entmate_theme/static/src/scss/night_mode_user.scss',
            "sh_entmate_theme/static/src/xml/NightMode.xml",

            # Sticky
            'sh_entmate_theme/static/src/scss/sticky/sticky_chatter.scss',
            'sh_entmate_theme/static/src/scss/sticky/sticky_form.scss',
            'sh_entmate_theme/static/src/scss/sticky/sticky_list_inside_form.scss',
            'sh_entmate_theme/static/src/scss/sticky/sticky_list.scss',
            'sh_entmate_theme/static/src/scss/sticky/sticky_pivot.scss',
            'sh_entmate_theme/static/src/js/pivot_view_sticky/pivot_sticky_dropdown.js',

            # Firebase and PWA  and bus Notification
            'sh_entmate_theme/static/index.js',
            "https://www.gstatic.com/firebasejs/8.4.3/firebase-app.js",
            "https://www.gstatic.com/firebasejs/8.4.3/firebase-messaging.js",
            'sh_entmate_theme/static/src/js/firebase.js',
            'sh_entmate_theme/static/src/js/bus_notification.js',

            # Horizontal/vertical Tab
            'sh_entmate_theme/static/src/js/notebook.js',
            'sh_entmate_theme/static/src/scss/tab.scss',

            # Discuss Chatter
            'sh_entmate_theme/static/src/components/message/message.js',
            "sh_entmate_theme/static/src/xml/message.xml",
            'sh_entmate_theme/static/src/scss/discuss_chatter/discuss_chatter.scss',

            # Multi Tab
            'sh_entmate_theme/static/src/webclient/navtab/navtab.js',
            "sh_entmate_theme/static/src/xml/navbar.xml",
            'sh_entmate_theme/static/src/scss/multi_tab_at_control_panel/multi_tab.scss',
            'sh_entmate_theme/static/src/webclient/action_container.js',
            'sh_entmate_theme/static/src/js/owl.carousel.js',

            # Third party


            # Disable Auto edit feature
            "sh_entmate_theme/static/src/js/form_controller.js",
            "sh_entmate_theme/static/src/xml/form_controller.xml",
            "sh_entmate_theme/static/src/scss/form_controller.scss",
        ],

        'web.assets_frontend': [
            'sh_entmate_theme/static/src/scss/login_page_style.scss',
            'sh_entmate_theme/static/src/scss/fonts.scss',
        ],
        'web._assets_primary_variables': [
          ('after', 'web/static/src/scss/primary_variables.scss', '/sh_entmate_theme/static/src/scss/back_theme_config_main_scss.scss'),        
        ],

    },
    'images': [
        'static/description/banner.gif',
        'static/description/splash-screen_screenshot.gif'
    ],
    "live_test_url": "https://softhealer.com/support?ticket_type=demo_request",
    "installable": True,
    "application": True,
    "price": 74,
    "currency": "EUR",
    "bootstrap": True
}
