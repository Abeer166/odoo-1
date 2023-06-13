$(document).ready(function () {

    $(document).on("click", "#action_preview_theme_style_1", function (ev) {
        console.log("KKKKKKKK",$("input[name=img_src]"))
        var img_src = $("input[name=img_src]").val();
        console.log("..............",$("#js_id_theme_preview_image"))
           $("#js_id_theme_preview_image").attr('src', 'sh_back_theme_config/static/src/img/preview/theme/theme_style_img.png');
 
           });


    $(document).on("click", ".sh_close_notification", function () {
        $("#object").css("display", "none");
        $("#object1").css("display", "none");
    });
   
    $('.o_web_client').on('click', ".o_action_manager", function (ev) {

         //$('.sh_search_results').css("display","none");
         $('.todo_layout').removeClass("sh_theme_model");
         if ($('.sh_calc_util').hasClass('active')) {
             $('.open_calc').click();
         }
         //	$('.o_action_manager').css("margin-right","0px")
         $('.sh_search_results').css("display", "none");

         if($('.sh_user_language_list_cls').css("display") != 'none'){
            $('.sh_user_language_list_cls').css("display","none")
         }
         if($('.sh_wqm_quick_menu_submenu_list_cls').css("display") != 'none'){
            $('.sh_wqm_quick_menu_submenu_list_cls').css("display","none")
         }

         if($('.sh_calc_util').hasClass("active")){
            $('.sh_calc_util').removeClass("active")
         }
         
    });
    
    $(document).on("click", ".sh_close_notification", function () {
        $("#object").css("display", "none");
        $("#object1").css("display", "none");
    });




    $('body').keydown(function (e) {
        if ($("body").hasClass("sh_sidebar_background_enterprise")) {
            $(".sh_search_container").css("display", "block");
            $(".usermenu_search_input").focus();
            $(".sh_entmate_theme_appmenu_div").css("opacity", "0")
            if(!$("body").hasClass("sh_detect_first_keydown")){
                $(".usermenu_search_input").keydown()
            }
         
        }
    });

});