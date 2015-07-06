function update_help() {
	var params = {type: 'apple_et'};
	$.get('http://newa.nrcc.cornell.edu/newaTools/process_help',params,function(data) { $('#third').html(data); });
	return false;
  }

// Following block used on results page
function updateTrees() {
	var trees_per_acre,
		acres_per_sqft = 0.0000229568411;
	if ($.isNumeric($("#inrow").val()) && $.isNumeric($("#betrow").val())) {
		trees_per_acre = 1.0 / ($("#inrow").val() * $("#betrow").val() * acres_per_sqft);
		$("#trees_acre").val(Math.round(trees_per_acre));
		if ($("#greentip").val() !== "mm/dd/yyyy") {
			$("#calc_button").show();
		}
	} else {
		$("#trees_acre").val("");
	}
}
function enterTrees() {
	$("#inrow").val("-");
	$("#betrow").val("-");
	if ($("#greentip").val() !== "mm/dd/yyyy") {
		$("#calc_button").show();
	}
}
function rainChange() {
	var i;
	for (i = 1; i <= 14; i += 1) {
		$("#raing"+i).empty();
		$("#balance"+i).empty();
		$("#cmlbalance"+i).empty();
	}
	$("#calc_button").show();
}
function irrgChange() {
	var i;
	for (i = 1; i <= 14; i += 1) {
		$("#balance"+i).empty();
		$("#cmlbalance"+i).empty();
	}
	$("#calc_button").show();
}
function calculateGallons() {
	var i, gallons_per_acre, gallons_per_tree, rain_per_acre, irrg_per_acre, orchard_et, dlybal,
		cmlbal = 0.0,
		age = $("#orchard_age").val(),
		model_tree_density = 518,			//trees per acre
		gallons_per_liter = 0.264172052,	//gallons of water per liter
		gallons_per_inch = 27154,		 	//gallons of water per acre for 1" precip
		age_factors = {'1': {'scaleEt': 0.10, 'scaleRain': 0.05}, '2': {'scaleEt': 0.30, 'scaleRain': 0.25},
					   '3': {'scaleEt': 0.60, 'scaleRain': 0.35}, '4': {'scaleEt': 0.80, 'scaleRain': 0.50},
					   'mature': {'scaleEt': 1.0, 'scaleRain': 0.70}};
	$("#calc_button").hide();
	$("#results_div").show();
	for (i = 1; i <= 14; i += 1) {
		orchard_et = parseFloat($("#metl"+i).html()) * (1.0 / parseFloat($("#trees_acre").val())) * model_tree_density * age_factors[age]['scaleEt'];
		gallons_per_tree = orchard_et * gallons_per_liter;
		$("#gpt"+i).html((Math.round(gallons_per_tree * 10) / 10).toFixed(1));
		gallons_per_acre = gallons_per_tree * parseFloat($("#trees_acre").val());
		$("#etg"+i).html(Math.round(gallons_per_acre));
		rain_per_acre = parseFloat($("#raini"+i).val()) * gallons_per_inch * age_factors[age]['scaleRain'];
		irrg_per_acre = parseInt($("#irrg"+i).val());
		if ($.isNumeric(rain_per_acre)) {
			$("#raing"+i).html(Math.round(rain_per_acre));
		} else {
			$("#raing"+i).html("-");
			rain_per_acre = 0
		}
		dlybal = rain_per_acre + irrg_per_acre - gallons_per_acre;
		$("#balance"+i).html(Math.round(dlybal));
		cmlbal = Math.min(0.0, (cmlbal +  dlybal));
		$("#cmlbalance"+i).html(Math.round(cmlbal));
	}
//	$("#trees_acre").focus();
	$("#results_table td:nth-child(2)").hide();	//need this for calculations, but users dont' need to see it
}
// end block

function apple_et() {
	var params = {type: 'apple_et'};
	$('select[name=stn], input[name=accend], input[name=greentip]').each(function () { params[this.name] = this.value; });
	$('#results_div').empty().show().html('<img src="http://newa.nrcc.cornell.edu/gifs/ajax-loader.gif" alt="Processing" id="loading" />');
	$('#righttabs').tabs('select',1);
	$.get('http://newa.nrcc.cornell.edu/newaTools/process_input',params,function(data) {
		$('#loading').fadeOut(500, function() {
			$(this).remove();
		});
		$("#results_div").html(data);
		calculateGallons();
		$(".raini").keyup(function () {
			rainChange();
		});
		$(".irrg").keyup(function () {
			irrgChange();
		});
	});
	$('#calc_button').off('click').on('click', function () {
		calculateGallons();
	});
	$('#orchard_age').change(function () {
		calculateGallons();
	});
	$("#spec_text").html('Change green tip date or tree density and click "Calculate" to recalculate results. Changing "Age of Orchard" will ' +
						 'automatically recalculate table.')
	return false;
	}

function apple_et_specs() {
	var params = {type: 'apple_et_specs'};
	$('select[name=stn], input[name=accend]').each(function () { params[this.name] = this.value; });
	$('#second').empty().html('<img src="http://newa.nrcc.cornell.edu/gifs/ajax-loader.gif" alt="Processing" id="loading" />');
	$('#righttabs').tabs('select',1);
	$.get('http://newa.nrcc.cornell.edu/newaTools/process_input',params,function(data) {
		$('#loading').fadeOut(500, function() {
			$(this).remove();
		});
		$("#second").html(data);
	  });
	return false;
	}

$(document).ready(function() {
	var myDate = new Date(),
		todayDate = (myDate.getMonth()+1) + "/" + myDate.getDate() + "/" + myDate.getFullYear();
	$("#enddpick").datepicker({ minDate: new Date(2000, 0, 1), maxDate: "", changeMonth: true, changeYear: true }).val(todayDate);
	$("#righttabs").tabs();
	$("form .button").click(function () {
		apple_et_specs();
	});
	stationMap('goodsr','select_station');
});