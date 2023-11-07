odoo.define('pos_address_map_app.address_map', function(require) {
	"use strict";

	const models = require('point_of_sale.models');
	const { Gui } = require('point_of_sale.Gui');
	const chrome = require('point_of_sale.Chrome');
	const PartnerDetailsEdit = require('point_of_sale.PartnerDetailsEdit');
	const Registries = require('point_of_sale.Registries');
	var core = require('web.core');
	var rpc = require('web.rpc');
	var ajax = require('web.ajax');
	var utils = require('web.utils');
	var round_pr = utils.round_precision;
    const {onMounted} = owl;

	var _t = core._t;
	var geocoder;
	var map;
	var marker;
	var infowindow;
	var self;
	var placeSearch, autocomplete;


	const PosPartnerDetailsEdit = (PartnerDetailsEdit) =>
		class extends PartnerDetailsEdit {
			
			setup() {
				super.setup();
				let self = this;
				var first_partner = self.env.pos.partners[0];
				var section = $('section').find('.edit');
				var section1 = $('.partner-details-contents').find('.div');
				onMounted(() => {
	               self.mounted();
	            });
			}


			mounted() {
				var self = this;
				var first_partner = this.props.partner;
				geocoder = new google.maps.Geocoder();
				var latlng = new google.maps.LatLng(-34.397, 150.644);
				var myOptions = {
					zoom: 14,
					center: latlng,
					mapTypeId: google.maps.MapTypeId.ROADMAP
				};
				var map_view = document.getElementById('geomap')
				map = new google.maps.Map(map_view, myOptions);
				var address = first_partner.address
				this.map_change_address(address);
				var addrs_srch = document.getElementById('address_search');
				this.initAutocomplete(addrs_srch);
				// this.saveChanges();
			}
			display_client_details(event){
				var self = this;
				// this._super(visibility,partner,clickpos);
				// if(visibility === 'edit'){
				// 	$(':input').on('focus', function() {
				// 		initAutocomplete(this);
				// 	})
				// }
			}
			initAutocomplete(element) {
				let self = this;
				element.focus();
				autocomplete = new google.maps.places.Autocomplete(element, {types: ['geocode']});
				autocomplete.bindTo('bounds', map);
				autocomplete.setFields(['address_component', 'geometry', 'icon', 'name','formatted_address']);
				// autocomplete.addListener('place_changed', self.fillInAddress);

				google.maps.event.addListener(autocomplete, 'place_changed', function () {
	            	var place = autocomplete.getPlace();
					if(place){
						self.map_change_address(place.formatted_address);
					}   
	            });
			}

			fillInAddress() {
				var self = this;
				var place = autocomplete.getPlace();
				if(place){
					self.map_change_address(place.formatted_address);
				}
			}
			
			set_address_from_map(pos) {
				var self = this;
				geocoder.geocode({
					latLng: pos
				}, function(responses) {
					var street = '';
					var city = '';
					var country = '';
					var country_id = '';
					var zip = '';
					var state ='';
					var state_id = '';

					if (responses && responses.length > 0) {
					  marker.formatted_address = responses[0].formatted_address;
					} else {
					  marker.formatted_address = 'Cannot determine address at this location.';
					}
					var splitted = marker.formatted_address.split(",");
					street = marker.formatted_address.slice(0, marker.formatted_address.indexOf(','))
					if(splitted.length > 6)
					{
						street = marker.formatted_address.split(",",2); 
					}
					street = street.toString();
					geocoder.geocode({
						'address': marker.formatted_address
					}, function(results, status) {
						if (status == google.maps.GeocoderStatus.OK) {
							var addrs = [];
							for (var i = 0; i < results[0].address_components.length; i++) {
								var addressType =  results[0].address_components[i].types[0];
								if(addressType == "street_number" || addressType == "sublocality_level_1" || addressType == "sublocality_level_2" )
								{
									if(street == '')
									{
										street = street + ' ' + results[0].address_components[i].long_name;
									}
								}
								if(addressType ==  "locality" || addressType == "administrative_area_level_1" || addressType == "administrative_area_level_2")
								{
									if(addressType ==  "locality")
									{
										city = city + ' ' +  results[0].address_components[i].long_name;
									}
								} 
								if(addressType == "country")
								{
									country = results[0].address_components[i].long_name;
									country = country.toLowerCase();
									rpc.query({
										model: 'res.country',
										method: 'search_read',
										domain: [['name', '=', results[0].address_components[i].long_name]],
										fields: ['id', 'name'],
									}, {async: false}).then(function(output1) {
									    console.log("______output1",output1)
										if(output1 && output1[0])
										{
											country_id = output1[0]['id']
											self.changes['country_id'] = country_id;
											$('[name="country_id"]').val(country_id)
										}
										
									});
								}
								if (addressType == "administrative_area_level_1"){
									state = results[0].address_components[i].long_name;
									state = country.toLowerCase();
									rpc.query({
										model: 'res.country.state',
										method: 'search_read',
										domain: [['name', '=', results[0].address_components[i].long_name]],
										fields: ['id', 'name'],
									}, {async: false}).then(function(output1) {
										if(output1 && output1[0])
										{
											state_id = output1[0]['id']
											self.changes['state_id'] = state_id;
											$('[name="state_id"]').val(state_id)
										}
										else{
										    state_id = false
											self.changes['state_id'] = state_id;
											$('[name="state_id"]').val(state_id)
										}
										
									});
								}
								if(addressType == "postal_code")
								{
									zip = results[0].address_components[i].long_name;
								} 
							}
							$('[name="street"]').val(street)
							if (city){
							    $('[name="city"]').val(city)
							}else{
                                city = false
                            }
							$('[name="zip"]').val(zip)
							self.changes['street'] = street;
							self.changes['city'] = city;
							self.changes['zip'] = zip;
						}
					});
					infowindow.setContent(marker.formatted_address + "<br>coordinates: " + marker.getPosition().toUrlValue(6));
					infowindow.open(map, marker);
				});
			}

			map_change_address(address) {
				var self = this;
				geocoder.geocode({
					'address': address
				}, function(results, status) {
					if (status == google.maps.GeocoderStatus.OK) {
						map.setCenter(results[0].geometry.location);
						infowindow = new google.maps.InfoWindow(
						{ 	content: '<b>'+address+'</b>',
							size: new google.maps.Size(150,50)
						});
						if (marker) {
							marker.setMap(null);
							if (infowindow) infowindow.close();
						}
						marker = new google.maps.Marker({
							map: map,
							draggable: true,
							position: results[0].geometry.location
						});
						// self.set_address_from_map(marker.getPosition());
						google.maps.event.addListener(marker, 'dragend', function() {
							self.set_address_from_map(marker.getPosition());
						});
						google.maps.event.addListener(marker, 'click', function() {
							if (marker.formatted_address) {
								infowindow.setContent(marker.formatted_address + "<br>coordinates: " + marker.getPosition().toUrlValue(6));
							} else {
								infowindow.setContent(address + "<br>coordinates: " + marker.getPosition().toUrlValue(6));
							}
							infowindow.open(map, marker);
						});
						google.maps.event.trigger(marker, 'click');
					} else {
					  alert('Geocode was not successful for the following reason: ' + status);
					}
			  });
			}
		};
	Registries.Component.extend(PartnerDetailsEdit, PosPartnerDetailsEdit);

    return {
    	PosPartnerDetailsEdit,
    }
});
