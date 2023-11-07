odoo.define('as_customer_address_from_google_map.partner_select_current_point', function (require) {
 'use strict';
// var basic_fields = require('web.basic_fields');
var core = require('web.core');
var _t = core._t;
var registry = require('web.field_registry');
// var session = require('web.session');
var _lt = core._lt;
var Widget = require('web.Widget');
// var ajax = require('web.ajax');
// var Dialog = require('web.Dialog');
var icon;

// First of all, import the things we need here.
    var AbstractAction = require('web.AbstractAction');
    var QWeb = core.qweb;
    var _t = core._t;
    var rpc = require("web.rpc");

var partner_select_current_point = AbstractAction.extend({
    contentTemplate: 'partner_select_current_point',
    xmlDependencies: ['/as_customer_address_from_google_map/static/src/xml/google_map_template_view.xml'],
    hasControlPanel: true,
    title: core._t("New Dialog"),
    events: {
                'click #save_location': '_onSaveAddress',
    },
    _onSaveAddress: function() {
        var self = this;
        this._rpc({
            'route': '/set_current_location_name_contact/',
            'params': {
                "active_id": this.action.context.active_id,
                "location_name": this.location_name,
                "address": this.address,
                "addres_component_length": this.addres_component_length,
                "latitude": this.latitude,
                "longitude": this.longitude,
            }
        }).then(function (result) {
            self.do_action({type: 'ir.actions.act_window_close'});
        })
    },
    init: function(parent, action, options) {
        this._super.apply(this, arguments);
        var self = this;
        this.action = action;
        this.context = action.context;
        this.actionManager = parent;
        this.options = options || {};
        if (this.action.context.active_model === "res.partner") {
            this._rpc({
                    model: 'res.company',
                    method: 'search_read',
                    args: [[['id', '=', this.action.context.allowed_company_ids[0]]], ['res_partner_use_gmap']],
            })
            .then(function (companies){
                if(companies[0].res_partner_use_gmap){
                    navigator.geolocation.getCurrentPosition(success);
                    function success(position) {
                        const latitude  = position.coords.latitude;
                        const longitude = position.coords.longitude;
                        if (latitude && longitude){
                            self.get_address_location(latitude, longitude, companies[0].res_partner_use_gmap);
                        }else{
                            self.fail()
                        }
                    }
                }
            });
        };
    },

    fail: function() {
        alert('Unable to retrieve your location');
    },

    get_address_location: function(latitude, longitude, res_partner_use_gmap) {
        var self = this;
        $.getScript("https://maps.googleapis.com/maps/api/js?key="+ res_partner_use_gmap + "&libraries=places&signed_in=true", function() {
            self.$("#map-canvas").css({
                'width':  "100%",
                'position' : "absolute",
            });

            $(".modal-content").css({'width': '110%'});
            $(".modal-title").text('Use Selected Location or Pin Anywhere in Map');

            var myOptions = {
                zoom: 17,
            },
            geocoder = new google.maps.Geocoder(),
            map = new google.maps.Map(document.getElementById('map-canvas'), myOptions);
            

            icon = {
                path: "M27.648-41.399q0-3.816-2.7-6.516t-6.516-2.7-6.516 2.7-2.7 6.516 2.7 6.516 6.516 2.7 6.516-2.7 2.7-6.516zm9.216 0q0 3.924-1.188 6.444l-13.104 27.864q-.576 1.188-1.71 1.872t-2.43.684-2.43-.684-1.674-1.872l-13.14-27.864q-1.188-2.52-1.188-6.444 0-7.632 5.4-13.032t13.032-5.4 13.032 5.4 5.4 13.032z",
                fillColor: '#E32831',
                fillOpacity: 1,
                strokeWeight: 0,
                scale: 0.65
            };
            var marker = new google.maps.Marker({
                map: map,
                icon: icon,
                animation: google.maps.Animation.DROP,
                // position: {lat:latitude, lng:longitude};
            });

            map.setCenter(new google.maps.LatLng(latitude, longitude));
            $.when(marker.setPosition(map.getCenter())).then(function () {
                    self.onClickMarker(marker, map.getCenter(), geocoder);
            })
            map.addListener('click', function(e) {
                self.onClickMarker(marker, e.latLng, geocoder);
            });
        });
    },
    onClickMarker: function (marker, latLng, geocoder) {
        if (!marker || !latLng) {
            return
        }
        var self = this;
        function animatedMove(marker, n, current, moveto) {
            var lat = current.lat();
            var lng = current.lng();

            var deltalat = (moveto.lat() - current.lat()) / 100;
            var deltalng = (moveto.lng() - current.lng()) / 100;

            for (var i = 0; i < 100; i++) {
                (function(ind) {
                    setTimeout(function() {
                        var lat = marker.position.lat();
                        var lng = marker.position.lng();

                        lat += deltalat;
                        lng += deltalng;
                        var latlng = new google.maps.LatLng(lat, lng);
                        marker.setPosition(latlng);
                    }, 5 * ind);
                })(i)
            }
        }
        animatedMove(marker, 10, marker.position, latLng);
        geocoder.geocode({
            'latLng': latLng
        }, function(results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                if (results[0]) {
                    var latitude = results[0].geometry.location.lat()
                    var longitude = results[0].geometry.location.lng()
                    if (results[0].address_components && results[0].address_components.length > 1) {
                        var address = results[0];
                        var location_name = results[0].formatted_address;
                    } else {
                        if (results.length > 2) {
                            var address = results[results.length-2];
                            var location_name = results[0].formatted_address + ", " + results[results.length-2].formatted_address;
                        } else {
                            var address = results[0];
                            var location_name = results[0].formatted_address;
                        }
                    }
                    document.getElementById("current_address").textContent = 'Current Address: '+location_name;
                    self.location_name = location_name;
                    self.address = address.address_components;
                    self.addres_component_length = address.address_components.length;
                    self.latitude = latitude
                    self.longitude = longitude
                }
            }
        });
    },
    start: function () {
        this.get_html()
    },
    get_html: function(){
        var self = this;
        self.html = QWeb.render("partner_select_current_point",{});
        return Promise.all([]);
    },

});

core.action_registry.add('partner_select_current_point', partner_select_current_point);
return partner_select_current_point

 });

