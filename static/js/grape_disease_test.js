function update_page() {
	if (document.stationLister.pest.value == "") {
		document.stationLister.pest.value = 'grape_dis';
	}
	window.location = '/newaTester/'+document.stationLister.pest.value;
}

function update_help() {
	var params = {type: 'grape_disease'};
	$('select[name=pest]').each(function () { params[this.name] = this.value; });
	$.get('/newaTester/process_help',params,function(data) { $('#third').html(data); });
	return false;
  }

function getberrymoth(selopt) {
	var req_stn;
	var params = {type: 'grape_disease'};
	$('select[name=stn], input[name=accend], select[name=pest]').each(function () { params[this.name] = this.value; });
	if (selopt === 1) {
		$('input[name=bf_date]').each(function () { params[this.name] = this.value; }); }
	$('#second').empty().html('<img src="/gifs/ajax-loader.gif" alt="Processing" id="loading" />');
	$('#righttabs').tabs('select',1);
	$.get('/newaTester/process_input',params,function(data) {
		$('#loading').fadeOut(500, function() {
			$(this).remove();
		});
		$("#second").html(data);
		$('#bfdpick').datepicker({ minDate: new Date(2000, 0, 1), maxDate: "", changeMonth: true, changeYear: true });
		$('#forecast').click(function() {
			req_stn = $('select[name=stn] option:selected').val();
			$.get('/newaUtil/getForecastUrl/'+req_stn, function(data) { 
				window.open(data);
			});
		});
		$("#moreinfo").dialog({
			show: 'blind',
			hide: 'blind',
			height: 400,
			width: 500,
			modal: true,
			autoOpen: false,
			buttons: { Close: function() { $(this).dialog('close'); } }
		});
	});
	return false;
	}

function getdmcast() {
	var params = {type: 'dmcast'};
	$('select[name=stn], input[name=accend], select[name=cultivar]').each(function () { params[this.name] = this.value; });
	$('#second').empty().html('<img src="/gifs/ajax-loader.gif" alt="Processing" id="loading" /> Loading');
	$('#righttabs').tabs('select',1);
	$.get('/newaTester/process_input',params,function(data) {
		$('#loading').fadeOut(500, function() { $(this).remove(); });
		$("#second").html(data);
	});
	return false;
}

function getgrapedis() {
	var params = {type: 'grape_dis'};
	$('select[name=stn], input[name=accend]').each(function () { params[this.name] = this.value; });
	$('#second').empty().html('<img src="/gifs/ajax-loader.gif" alt="Processing" id="loading" /> Loading');
	$('#righttabs').tabs('select',1);
	$.get('/newaTester/process_input',params,function(data) {
		$('#loading').fadeOut(500, function() { $(this).remove(); });
		$("#second").html(data);
		$('#data').fixedHeader({ width: "100%",height: 490 });
	});
	return false;
}

$(document).ready(function() {
	var myDate = new Date();
	var todayDate = (myDate.getMonth()+1) + "/" + myDate.getDate() + "/" + myDate.getFullYear();
	$("#enddpick").datepicker({ minDate: new Date(2000, 0, 1), maxDate: "", changeMonth: true, changeYear: true });
	$("#enddpick").val(todayDate);
	$("#righttabs").tabs();
	$("form .button").click(function (evt) {
		if (document.stationLister.pest.value == 'berry_moth') {
			getberrymoth(0);
		} else if (document.stationLister.pest.value == 'dmcast') {
			getdmcast();
		} else if (document.stationLister.pest.value == 'grape_dis') {
			getgrapedis();
		}
	});
	if (document.stationLister.pest.value == 'dmcast') {
		stationMap('lwrh','select_station');
	} else if (document.stationLister.pest.value == 'grape_dis') {
		stationMap('eslw','select_station');
	} else {
		stationMap('all','select_station');
	}
});