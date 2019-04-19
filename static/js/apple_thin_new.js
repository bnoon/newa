/*global $, document, stationMap */
function update_help() {
	var params = {type: 'apple_thin'};
	$.get('/newaTools/process_help', params, function (data) { $('#third').html(data); });
	return false;
}

function apple_thin() {
	var params = {type: 'apple_thin'},
		oneday = 1000*60*60*24;
	$('select[name=stn], input[name=accend], input[name=greentip], input[name=bloom], select[name=percentflowerspurs]').each(function () {
		params[this.name] = this.value;
	});
	$('#results_div').empty().show().html('<img src="/gifs/ajax-loader.gif" alt="Processing" id="loading" />');
	$('#righttabs').tabs('option', 'active',1);
	$("tr.dateMsg").empty();
	dateDiff = (Date.parse(params.bloom) - Date.parse(params.greentip)) / oneday;
	if (! isNaN(dateDiff) && dateDiff < 21) {
		$(".thin_table").append("<tr class='dateMsg'><td colspan=3 style='color:red;'>Difference between Green tip and Bloom is less than 21 days. Results may be unreliable.<\/td><\/tr>");
	}
	saveAppleinfo(params.stn, params.accend.slice(-4), "thin-greentip", params.greentip);
	saveAppleinfo(params.stn, params.accend.slice(-4), "bloom", params.bloom);
	saveAppleinfo(params.stn, params.accend.slice(-4), "percentflowerspurs", params.percentflowerspurs);
	$.get('/newaTools/process_input_new', params, function (data) {
		$('#loading').fadeOut(500, function () {
			$(this).remove();
		});
		$("#results_div").html(data);
		$("#results_table td:contains('-999')").text("-");
		displayGraph()
	});
	$("#spec_text").html('Change green tip and/or bloom date and click "Calculate" to recalculate results.');
	return false;
}

function updateFromStorage(params) {
	var gtFromStorage = getAppleinfo(params.stn, params.accend.slice(-4), "thin-greentip");
	if (gtFromStorage) {
		$("#greentip").val(gtFromStorage);
	}
	var blFromStorage = getAppleinfo(params.stn, params.accend.slice(-4), "bloom");
	if (blFromStorage) {
		$("#bloom").val(blFromStorage);
	}
	var pfsFromStorage = getAppleinfo(params.stn, params.accend.slice(-4), "percentflowerspurs");
	if (pfsFromStorage) {
		$("#percentflowerspurs").val(pfsFromStorage);
	}
	if (gtFromStorage && blFromStorage) {
		$("#calc_button").show();
	}
}	

function apple_thin_specs_loaded() {
	$("#calc_button").on('click', function () {
		$(this).hide();
		apple_thin();
	});
	$("#greentip").datepicker({ changeMonth: true }).change(function () {
		$("#results_div").empty();
		$("#calc_button").show();
	});
	$("#bloom").datepicker({ changeMonth: true }).change(function () {
		$("#results_div").empty();
		$("#calc_button").show();
	});
	$("#percentflowerspurs").change(function () {
		$("#results_div").empty();
		$("#calc_button").show();
	});
}

function apple_thin_specs() {
	var params = {type: 'apple_thin_specs'};
	$('select[name=stn], input[name=accend]').each(function () { params[this.name] = this.value; });
	$('#second').empty().html('<img src="/gifs/ajax-loader.gif" alt="Processing" id="loading" />');
	$('#righttabs').tabs('option', 'active',1);
	$.get('/newaTools/process_input_new', params, function (data) {
		$('#loading').fadeOut(500, function () {
			$(this).remove();
		});
		$("#second").html(data);
		updateFromStorage(params);
		apple_thin_specs_loaded();
	});
	return false;
}

$(document).ready(function () {
	var myDate = new Date(),
		todayDate = (myDate.getMonth() + 1) + "/" + myDate.getDate() + "/" + myDate.getFullYear();
	$("#enddpick").datepicker({ minDate: new Date(2000, 0, 1), maxDate: "", changeMonth: true, changeYear: true }).val(todayDate);
	$("#righttabs").tabs({
		activate: function () {
			var center = map.getCenter();
			google.maps.event.trigger(map, 'resize');
			map.setCenter(center);
		}
	});
	$("form .button").click(function () {
		apple_thin_specs();
	});
	stateStationMapList({
		reqvar: 'goodsr',
		event_type: 'select_station',
		where: '#station_area'
	});
});