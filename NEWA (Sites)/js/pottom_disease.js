function getresults() {
	var params = {
			type: $("#pest").val(),
			subtype: $('select[name=tomato_cultivar]').length ? 'simcast' : 'blitecast',
			crop: 'tomato'
		},
		myDate = new Date(),
		todayDate = (myDate.getMonth()+1) + "/" + myDate.getDate() + "/" + myDate.getFullYear();
	$('#leftbox select').each(function () {
		params[this.name] = this.value;
	});
	if ($("#dpick").length) {
		params.accend = $("#dpick").val();
		params.year = params.accend.split("/")[2];
	} else {
		params.accend = null;
		params.year = myDate.getFullYear();
	}
	$('#second').empty().html('<img src="http://newatest.nrcc.cornell.edu/gifs/ajax-loader.gif" alt="Processing" id="loading" />');
	$('#righttabs').tabs('option', 'active', 1);
	$.get('http://newatest.nrcc.cornell.edu/newaDisease/process_input', params, function (data) {
		$('#loading').fadeOut(500, function () {
			$(this).remove();
		});
		$("#second").html(data);
		
		$(".getReport").prop("disabled", false).on("click", getresults);
		
		$("#forecast").on("click", function() {
			$.get("http://newatest.nrcc.cornell.edu/newaUtil/getForecastUrl/"+params.stn, function(fcst) { 
				window.open(fcst);
			});
		});
		$("#showTomLog").on("click", function() {
			var btntext = $("#showTomLog").text(),
				sh = btntext.indexOf("Hide") >= 0;
			if (sh) {
				$("#showTomLog").text("Show Tomcast log");
			} else {
				$("#showTomLog").text("Hide Tomcast log");
			}
			$("#tomcastTable").toggle();
		});
		$("#closeTomLog").on("click", function() {
			$('#showTomLog').trigger('click');
		});
		$("#showBliteLog").on("click", function() {
			var btntext = $("#showBliteLog").text(),
				sh = btntext.indexOf("Hide") >= 0;
			if (sh) {
				$("#showBliteLog").text("Show severity value log");
			} else {
				$("#showBliteLog").text("Hide severity value log");
			}
			$("#blitecastTable").toggle();
		});
		$("#closeBliteLog").on("click", function() {
			$('#showBliteLog').trigger('click');
		});
	});
	return false;
}

function showit() {
	$("#moreInfo").toggle();
}

function putItHere(al) {
	var url = al.attr('href');
	if ($('div.target').length == 0) {
    	al.parent().html("<div class='target'></div>");
	}
	$(".target").empty().load(url);
}

function yearMenu(where) {
	var yr, now = new Date();
	if (!where) {
		where = "#disease_inputs";
	}
	$(where).empty().append('<p style="margin-bottom:3px;">Year:<\/p><select name="year"><\/select>');
	for (yr = now.getFullYear(); yr >= 1995; yr -= 1) {
		$('select[name=year]').append('<option value="' + yr + '">' + yr + '</option>');
	}
	$('select[name=year] option:first').attr("selected", "selected");
}

function dateMenu(where, prompt, smname, sdname, defmon, defday) {
	var dy,
		month_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
	if (!where) {
		where = "#disease_inputs";
	}
	$(where).append('<p style="margin-bottom:3px;">' + prompt + '<\/p>' +
		'<select name="' + smname + '"><\/select><select name="' + sdname + '"><\/select>');
	$.each(month_list, function(mon_num, mon_name) {
		$('select[name=' + smname+ ']').append('<option value="' + (mon_num + 1) + '">' + mon_name + '</option>');
	});
	for (dy = 1; dy <= 31; dy += 1) {
		$('select[name=' + sdname + ']').append('<option value="' + dy + '">' + dy + '</option>');
	}
	$('select[name=' + smname + ']').prop('selectedIndex', defmon);
	$('select[name=' + sdname + ']').prop('selectedIndex', defday);
}

function checkFungicide(where) {
	var yr, dy, now = new Date();
	$(where).empty().append('<p style="margin-bottom:3px;">Have you applied a fungicide yet?<\/p>'+
		'<input type="button" id="fungyes" value="Yes" \/><input type="button" id="fungno" value="No" \/>');
	$("#fungyes").on("click", function () {
		$(where).empty();
//		yearMenu(where);
		dateMenu(where, "Last fungicide application:", "month", "day", now.getMonth(), now.getDate() - 2);
		// cultivar menu, stored in json file in Sites
		$(where).append('<p style="margin-bottom:3px;">Cultivar:<\/p><select name="tomato_cultivar" id="tomato_cultivar"><\/select>');
		$('select[name=tomato_cultivar]').append('<option value="" selected>Select tomato cultivar<\/option>');
		$.getJSON('http://newatest.nrcc.cornell.edu/tomato_cultivars.json', function (results) {
			$.each(results, function(key, val) {
				$('select[name=tomato_cultivar]').append('<option value="' + key + '">' + key + '<\/option>');
			});
		}).fail(function (d, textStatus, error) {
			console.log("getJSON failed, status: " + textStatus + ", error: " + error);
		});
		$('.getReport').after('<p style="text-align:center;font-weight:normal;"><a href="http://newatest.nrcc.cornell.edu/TomatoCultivarsPop.html" target="_blank">Tomato Cultivar Susceptibility</a></p>');
		$(".getReport").show();
	});
	$("#fungno").on("click", function () {
		$(where).empty();
//		yearMenu(where);
		dateMenu(where, "Transplant date:", "month", "day", 4, 14); //default May 15
		dateMenu(where, "First potato tissue emergence:", "emonth", "eday", 4, 0); //default May 1
		$("#useEffBox").css("border-width", "3px");
		$("#useEffBox p").show();
		$(".getReport").show();
	});
}

$(document).ready(function () {
	var myDate = new Date(),
		todayDate = (myDate.getMonth()+1) + "/" + myDate.getDate() + "/" + myDate.getFullYear();
	$("#righttabs").tabs();
	$("#leftbox").prepend("<div id='station_area'><\/div><div id='disease_inputs'><\/div>");
	if ($("#pest").val() === 'potato_simcast' || $("#pest").val() === 'potato_lb') {
		stationMap('rhum', 'select_station');
	} else if ($("#pest").val() === 'tomato_for') {
		stateStationMapList({
			reqval: 'eslw',
			event_type: 'select_station',
			where: '#station_area'
		});
		checkFungicide("#disease_inputs");
	} else {
		stationMap('all', 'select_station');
	}
	$("#dpick").datepicker({ minDate: new Date(2000, 0, 1), maxDate: "", changeMonth: true, changeYear: true }).val(todayDate);
	$(".getReport").on("click", getresults);
	$("#third a").click(function( event ) {
  		event.preventDefault();
  		putItHere($(this));
  		$(this).hide();
  	}).trigger("click");
});