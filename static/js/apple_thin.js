/*global $, document, stationMap */
function update_help() {
	var params = {type: 'apple_thin'};
	$.get('/newaTools/process_help', params, function (data) { $('#third').html(data); });
	return false;
}

function recommendation (dy4_thin) {
	var recommend, miss = -999;
	if (dy4_thin === miss) {
		recommend = "-";
	} else if (dy4_thin > 20 {
		recommend = "Increase chemical thinner rate by 30%";
	} else if (dy4_thin > 0) {
		recommend = "Increase chemical thinner rate by 15%";
	} else if (dy4_thin > -20) {
		recommend = "Apply standard chemical thinner rate";
	} else if (dy4_thin > -40) {
		recommend = "Decrease chemical thinner rate by 15%";
	} else if (dy4_thin > -60) {
		recommend = "Decrease chemical thinner rate by 30%";
	} else if (dy4_thin > -80) {
		recommend = "Decrease chemical thinner rate by 50%";
	} else {
		recommend = "Do not thin (many fruits will fall off naturally)";
	}
	return recommend
}

function add_4dy_thin() {
	var i, j, dy4_thin, dy4_sum,
		miss = -999,
		dly_thin = [];
	for (i = 0; i < $("#results_table td.dly_thin").length; i += 1) {
		dly_thin.push(parseFloat($("#results_table").find("td.dly_thin").eq(i).text()));
	}
	if (dly_thin.length >= 4) {
		for (i = 0; i <= dly_thin.length - 4; i += 1) {
			dy4_sum = 0;
			for (j = i; j <= i + 3; j += 1) {
				if (dy4_sum !== miss && dly_thin[j] !== miss) {
					dy4_sum += dly_thin[j];
				} else {
					dy4_sum = miss;
				}
			}
			dy4_thin = dy4_sum !== miss ? dy4_sum / 4.0 : miss;
			$("#results_table").find("td.4dy_thin").eq(i).text(Math.round(dy4_thin * 100) / 100);
			if (!$("#results_table").find("td.recommend").eq(i).hasClass("norecommend")) {
				$("#results_table").find("td.recommend").eq(i).text(recommendation(dy4_thin));
			}
		}
	}
}

function apple_thin() {
	var params = {type: 'apple_thin'},
		oneday = 1000*60*60*24;
	$('select[name=stn], input[name=accend], input[name=greentip], input[name=bloom]').each(function () {
		params[this.name] = this.value;
	});
	$('#results_div').empty().show().html('<img src="/gifs/ajax-loader.gif" alt="Processing" id="loading" />');
	$('#righttabs').tabs('option', 'active',1);
	$("tr.dateMsg").empty();
	dateDiff = (Date.parse(params.bloom) - Date.parse(params.greentip)) / oneday;
	if (! isNaN(dateDiff) && dateDiff < 21) {
		$(".thin_table").append("<tr class='dateMsg'><td colspan=3 style='color:red;'>Difference between Green tip and Bloom is less than 21 days. Results may be unreliable.<\/td><\/tr>");
	}
	$.get('/newaTools/process_input', params, function (data) {
		$('#loading').fadeOut(500, function () {
			$(this).remove();
		});
		$("#results_div").html(data);
		add_4dy_thin();
		$("#results_table td:contains('-999')").text("-");
//		$("#results_table").fixedHeader({width: 630, height: 400});
//		$("#results_table_header_container").css({ height: $("#results_table_header_container").outerHeight() + $("#results_table_header_container").find('caption').outerHeight() });
		displayGraph()
	});
	$("#spec_text").html('Change green tip and/or bloom date and click "Calculate" to recalculate results.');
	return false;
}

function apple_thin_specs() {
	var params = {type: 'apple_thin_specs'};
	$('select[name=stn], input[name=accend]').each(function () { params[this.name] = this.value; });
	$('#second').empty().html('<img src="/gifs/ajax-loader.gif" alt="Processing" id="loading" />');
	$('#righttabs').tabs('option', 'active',1);
	$.get('/newaTools/process_input', params, function (data) {
		$('#loading').fadeOut(500, function () {
			$(this).remove();
		});
		$("#second").html(data);
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