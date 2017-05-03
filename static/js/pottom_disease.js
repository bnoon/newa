function getresults() {
	var pest = $("#pest").val(),
		params = {
			type: pest,
			subtype: $('select[name=cultivar]').length ? 'simcast' : 'blitecast',
			crop: pest === 'tomato_for' ? 'tomato' : 'potato'
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
	$('#second').empty().html('<img src="/gifs/ajax-loader.gif" alt="Processing" id="loading" />');
	$('#righttabs').tabs('option', 'active', 1);
	$.get('/newaDisease/process_input', params, function (data) {
		$('#loading').fadeOut(500, function () {
			$(this).remove();
		});
		$("#second").html(data);
		
		$(".getReport").prop("disabled", false).on("click", getresults);
		
		$("#forecast").on("click", function() {
			$.get("/newaUtil/getForecastUrl/"+params.stn, function(fcst) { 
					var popup_window = window.open(fcst);
					try {
						popup_window.focus();
					} catch (e) {
						alert('Popup windows are blocked. Unblock popup windows to see forecast.');
					}
			});
			return false;
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
		$("#showPotLog").on("click", function() {
			var btntext = $("#showPotLog").text(),
				sh = btntext.indexOf("Hide") >= 0;
			if (sh) {
				$("#showPotLog").text("Show p-day log");
			} else {
				$("#showPotLog").text("Hide p-day log");
			}
			$("#pdayTable").toggle();
		});
		$("#closePotLog").on("click", function() {
			$('#showPotLog').trigger('click');
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

function checkFungicide(where, pest) {
	var yr, dy, cnt = 0,
		pottom = pest === 'tomato_for' ? 'Tomato' : 'Potato',
		now = new Date();
	$(where).empty().append('<p style="margin-bottom:3px;">Have you applied a fungicide yet?<\/p>'+
		'<input type="button" id="fungyes" value="Yes" \/><input type="button" id="fungno" value="No" \/>');
	$("#cultivar_link").remove();
	$("#fungyes").on("click", function () {
		$(where).empty();
		if (pottom === "Potato") {
			dateMenu(where, "Crop emergence date:", "emonth", "eday", 4, 9); //default May 10
		}
		dateMenu(where, "Last fungicide application:", "month", "day", now.getMonth(), now.getDate() - 2);
		// cultivar menu, stored in json file in Sites
		$(where).append('<p style="margin-bottom:3px;">Cultivar:<\/p><select name="cultivar" id="cultivar"><\/select>');
		$('select[name=cultivar]').append('<option value="" selected>Select cultivar<\/option>');
		$.getJSON('/' + pottom.toLowerCase() + '_cultivars.json', function (results) {
			$.each(results, function(key, val) {
				if (key.search("---") >= 0) {
					$('select[name=cultivar]').append('<optgroup label="' + key + '"><\/optgroup>');
				} else {
					$("select[name=cultivar]").find("optgroup").last().append('<option value="' + key + '">' + key + '<\/option>');
				}
			});
		}).fail(function (d, textStatus, error) {
			console.log("getJSON failed, status: " + textStatus + ", error: " + error);
		});
		$('.getReport').after('<p id="cultivar_link" style="text-align:center;font-weight:normal;"><a href="/' + pottom + 'CultivarsPop.html" target="_blank">' + pottom + ' Cultivar Susceptibility</a></p>');
		$(".getReport").show();
		$("#reset_link").show();
	});
	$("#fungno").on("click", function () {
		$(where).empty();
		if (pottom === "Tomato") {
			dateMenu(where, "Transplant date:", "month", "day", 4, 14); //default May 15
			dateMenu(where, "Date of potato cull sprouting or volunteer emergence:", "emonth", "eday", 4, 0); //default May 1
		} else {
			dateMenu(where, "Crop emergence date:", "emonth", "eday", 4, 9); //default May 10
			dateMenu(where, "Date of potato cull sprouting or volunteer emergence:", "month", "day", 4, 0); //default May 1
		}
		if (pottom === "Tomato") {
			$("#useEffBox").css("border-width", "3px");
			$("#useEffBox p").show();
		}
		$(".getReport").show();
		$("#reset_link").show();
	});
}

$(document).ready(function () {
	var myDate = new Date(),
		pest = $("#pest").val(),
		todayDate = (myDate.getMonth()+1) + "/" + myDate.getDate() + "/" + myDate.getFullYear();
	$("#righttabs").tabs();
	$("#leftbox").prepend("<div id='station_area'><\/div><div id='disease_inputs'><\/div>");
	if (pest === 'potato_simcast' || pest === 'potato_lb') {
		stationMap('rhum', 'select_station');
	} else if (pest === 'tomato_for' || pest === 'potato_for') {
		stateStationMapList({
			reqvar: 'eslw',
			event_type: 'select_station',
			where: '#station_area'
		});
		checkFungicide("#disease_inputs", pest);
	} else {
		stationMap('all', 'select_station');
	}
	$("#dpick").datepicker({ minDate: new Date(2000, 0, 1), maxDate: "", changeMonth: true, changeYear: true }).val(todayDate);
	$(".getReport").on("click", getresults);
	$("#third a").on('click', function(e) {
  		e.preventDefault();
  		putItHere($(this));
  		$(this).hide();
  	}).trigger("click");
	$("#usepotatoeffectively").on('click', function(e) {
		e.preventDefault();
		$('#righttabs').tabs('option', 'active', 2);
	});
  	$("#reset_link").on('click', function(e) {
  		e.preventDefault();
  		checkFungicide("#disease_inputs", pest);
		$(".getReport").hide();
  		$(this).hide();
  	});
});