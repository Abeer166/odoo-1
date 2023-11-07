odoo.define('pos_address_map_app.init', function (require) {
	"use strict";
	var rpc = require('web.rpc');
	// var ajax = require('web.ajax');
	const { loadJS } = require("@web/core/assets");
	rpc.query({
		model: 'pos.config',
		method: 'get_api_key',
		args: [1]
	}).then(async function (key) {
		await loadJS(`https://maps.googleapis.com/maps/api/js?v=3.exp&libraries=places&key=${key}`);
	});
});