function getforecast() {
	var params = {type: document.stationLister.pest.value};
	$('#leftbox select').each(function () {
		params[this.name] = this.value;
	});
	if (!params.year) {
		params.year = $('input[name=year]').val();
	}
	$('#second').empty().html('<img src="/gifs/ajax-loader.gif" alt="Processing" id="loading" />');
	$('#righttabs').tabs('select', 1);
	$.get('/newaDisease/process_input', params, function (data) {
		$('#loading').fadeOut(500, function () {
			$(this).remove();
		});
		$("#second").html(data);
	});
	return false;
}

function showit() {
	$("#moreInfo").toggle();
}

$(document).ready(function () {
	var params;
	$("#righttabs").tabs();
	$("form .button").on("click", function () {
		getforecast();
	});
	if (document.stationLister.pest.value === 'potato_simcast' || document.stationLister.pest.value === 'potato_lb') {
		stationMap('rhum', 'select_station');
	} else if (document.stationLister.pest.value === 'tomato_for') {
		stationMap('eslw', 'select_station');
	} else {
		stationMap('all', 'select_station');
	}
});