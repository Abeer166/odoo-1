odoo.define('sh_signup_email_approval.CodeValidation', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.CodeValidation = publicWidget.Widget.extend({

        selector: '.sh_cls_invalid_code',

        events: {
            'click #button_verify': '_onClickButtonVerify',
        },

        _onClickButtonVerify: function()
        {
            if (!$('#code').val())
            {
                return false
            }

            $.ajax({
                type: "POST",
                dataType: 'json',
                url: '/verify/user/validation',
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'url': window.location.href, 'code': $('#code').val()}}),
                success: function (result) {
                    var result = JSON.parse(result['result'])                
                    if (result['user_found']) {
                        window.location.href = '/web'
                    }

                    else{
                        $('.warnin-cls').text('Verify Code is Invalid.')
                        $('.warnin-cls').removeClass('d-none')
                    }
                }
            })
        }

    })

})    