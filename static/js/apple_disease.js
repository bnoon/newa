function update_help() {
	var params = {type: 'apple_disease', pest: $('select[name=pest]').val()};
	if (params.pest) {
		$.get('/newaModel/process_help', params, function(data) { $('#third').html(data); });
		return false;
	}
  }

function update_page() {
	if (window.location == '/newaModel/sooty_blotch' || document.stationLister.pest.value == 'sooty_blotch') {
		window.location = '/newaModel/'+document.stationLister.pest.value;
	}
	else {
		update_help();
	}
}

function getfireblight(selopt) {
	var req_stn;
	var params = {type: 'apple_disease'};
	$('select[name=stn], input[name=accend], select[name=pest]').each(function () { params[this.name] = this.value; });
	if (selopt === 1 | selopt === 3) {
		params.selbutton = 'biofix';
		$('input[name=firstblossom], select[name=orchard_history]').each(function () { params[this.name] = this.value; });
	} else if (selopt === 2) { 
		params.selbutton = 'strep';
		$('input[name=strep_spray], select[name=orchard_history], input[name=firstblossom]').each(function () { params[this.name] = this.value; });
	} else if (selopt === 4) {
		params.selbutton = 'biofix';
		params.firstblossom = 'noocc';
		$('select[name=orchard_history]').each(function () { params[this.name] = this.value; });
	}
	$('#second').empty().html('<img src="/gifs/ajax-loader.gif" alt="Processing" id="loading" />');
	$('#righttabs').tabs('option', 'active',1);
	$.get('/newaModel/process_input',params,function(data) {
		$('#loading').fadeOut(500, function() {
			$(this).remove();
		});
		$("#second").html(data);
		$('#fbdpick').datepicker({ minDate: new Date(2000, 0, 1), maxDate: "", changeMonth: true, changeYear: true });
		$('#ssdpick').datepicker({ minDate: new Date(2000, 0, 1), maxDate: "", changeMonth: true, changeYear: true });
		$('#iedpick').datepicker({ minDate: new Date(2000, 0, 1), maxDate: "", changeMonth: true, changeYear: true });
		$('#sodpick').datepicker({ minDate: new Date(2000, 0, 1), maxDate: "", changeMonth: true, changeYear: true });
		$('#forecast').click(function() {
			req_stn = $('select[name=stn] option:selected').val();
			$.get('/newaUtil/getForecastUrl/'+req_stn, function(data) { 
					var popup_window = window.open(data);
					try {
						popup_window.focus();
					} catch (e) {
						alert('Popup windows are blocked. Unblock popup windows to see forecast.');
					}
			});
			return false;
		});
		$('#fbgraph').click(function() {
			var paramStr = "type=fire_blight_grf";
			$('select[name=stn], input[name=accend], input[name=firstblossom], select[name=orchard_history]').each(function () { 
				paramStr += "&" + this.name + "=" + this.value.split("/").join("-");
			});
			window.open('/newaGraph/fire_blight_grf?' + paramStr,"fbgraph","resizable=1,scrollbars=1,status=0,toolbar=0,location=0,menubar=0,height=760,width=630");
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

function getshootblight(selopt) {
	var params = {type: 'shoot_blight'};
	$('select[name=stn], input[name=accend]').each(function () { params[this.name] = this.value; });
	if (selopt === 4) { 
		params.selbutton = 'infect'; 
		$('input[name=infection_event]').each(function () { params[this.name] = this.value; }); }
	if (selopt === 5) { 
		params.selbutton = 'symptoms'; 
		$('input[name=symptoms]').each(function () { params[this.name] = this.value; }); }
	$('#sbresults').remove();
	$('#shootblight').prepend('<img src="/gifs/ajax-loader.gif" alt="Processing" id="loading" />');
	$.get('/newaModel/process_input',params,function(data) {
		$('#loading').remove();
		$('#shootblight' + (selopt - 3)).append(data);
	});
	return false;
	}

function getapplescab(selopt) {
	var req_stn = $('select[name=stn] option:selected').val();
	var params = {type: 'apple_disease'};
	$('select[name=stn], input[name=accend], select[name=pest]').each(function () { params[this.name] = this.value; });
	if (selopt === 1) {
		$('input[name=greentip]').each(function () { params[this.name] = this.value; }); 
	} else if (selopt === 4) {
		params.greentip = 'noocc'; 
	}
	$('#second').empty().html('<img src="/gifs/ajax-loader.gif" alt="Processing" id="loading" />');
	$('#righttabs').tabs('option', 'active',1);
	$.get('/newaModel/process_input',params,function(data) {
		$('#loading').fadeOut(500, function() {
			$(this).remove();
		});
		$("#second").html(data);
		$('#dpick').datepicker({ minDate: new Date(2000, 0, 1), maxDate: "", changeMonth: true, changeYear: true });
		$('button.forecast').click(function() {
			$.get('/newaUtil/getForecastUrl/'+req_stn, function(data) { 
					var popup_window = window.open(data);
					try {
						popup_window.focus();
					} catch (e) {
						alert('Popup windows are blocked. Unblock popup windows to see forecast.');
					}
			});
			return false;
		});
		$('#asgraph').click(function() {
			var paramStr = "type=apple_scab_grf&stn=" + req_stn;
			$('input[name=accend], input[name=greentip]').each(function () { 
				paramStr += "&" + this.name + "=" + this.value.split("/").join("-");
			});
			window.open('/newaGraph/apple_scab_grf?' + paramStr,"asgraph","resizable=1,scrollbars=1,status=0,toolbar=0,location=0,menubar=0,height=760,width=630");
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

function getapplescab_estlw(selopt) {
	var req_stn = $('select[name=stn] option:selected').val();
	var params = {type: 'apple_scab_estlw'};
	$('select[name=stn], input[name=accend], select[name=pest]').each(function () { params[this.name] = this.value; });
	if (selopt === 1) {
		$('input[name=greentip]').each(function () { params[this.name] = this.value; }); }
	$('#second').empty().html('<img src="/gifs/ajax-loader.gif" alt="Processing" id="loading" />');
	$('#righttabs').tabs('option', 'active',1);
	$.get('/newaModel/process_input',params,function(data) {
		$('#loading').fadeOut(500, function() {
			$(this).remove();
		});
		$("#second").html(data);
		$('#dpick').datepicker({ minDate: new Date(2000, 0, 1), maxDate: "", changeMonth: true, changeYear: true });
		$('#forecast').click(function() {
			$.get('/newaUtil/getForecastUrl/'+req_stn, function(data) { 
					var popup_window = window.open(data);
					try {
						popup_window.focus();
					} catch (e) {
						alert('Popup windows are blocked. Unblock popup windows to see forecast.');
					}
			});
			return false;
		});
		$('#asgraph').click(function() {
			var paramStr = "type=apple_scab_grf&stn=" + req_stn;
			$('input[name=accend], input[name=greentip]').each(function () { 
				paramStr += "&" + this.name + "=" + this.value.split("/").join("-");
			});
			window.open('/newaGraph/apple_scab_grf?' + paramStr,"asgraph","resizable=1,scrollbars=1,status=0,toolbar=0,location=0,menubar=0,height=760,width=630");
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

function getsootyblotch(selopt) {
	var req_stn;
	var params = {type: 'apple_disease'};
	$('select[name=stn], input[name=accend], select[name=pest]').each(function () { params[this.name] = this.value; });
	if (selopt === 1) {
		params.selbutton = 'biofix';
		$('input[name=petalfall]').each(function () { params[this.name] = this.value; }); }
	if (selopt === 2) { 
		params.selbutton = 'fungicide';
		$('input[name=fungicide], input[name=petalfall]').each(function () { params[this.name] = this.value; }); }
	$('#second').empty().html('<img src="/gifs/ajax-loader.gif" alt="Processing" id="loading" />');
	$('#righttabs').tabs('option', 'active',1);
	$.get('/newaModel/process_input',params,function(data) {
		$('#loading').fadeOut(500, function() {
			$(this).remove();
		});
		$("#second").html(data);
		$('#bfdpick').datepicker({ minDate: new Date(2000, 0, 1), maxDate: "", changeMonth: true, changeYear: true });
		$('#fadpick').datepicker({ minDate: new Date(2000, 0, 1), maxDate: "", changeMonth: true, changeYear: true });
		$('#forecast').click(function() {
			req_stn = $('select[name=stn] option:selected').val();
			$.get('/newaUtil/getForecastUrl/'+req_stn, function(data) { 
					var popup_window = window.open(data);
					try {
						popup_window.focus();
					} catch (e) {
						alert('Popup windows are blocked. Unblock popup windows to see forecast.');
					}
			});
			return false;
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

$(document).ready(function() {
	var myDate = new Date();
	var todayDate = (myDate.getMonth()+1) + "/" + myDate.getDate() + "/" + myDate.getFullYear();
	$("#enddpick").datepicker({ minDate: new Date(2000, 0, 1), maxDate: "", changeMonth: true, changeYear: true });
	$("#enddpick").val(todayDate);
	$("#righttabs").tabs({
		activate: function () {
			var center = map.getCenter();
			google.maps.event.trigger(map, 'resize');
			map.setCenter(center);
		}
	});
	$("form .button").click(function (evt) {
		if (document.stationLister.pest.value == 'fire_blight') {
			getfireblight(0);
		}
		else if (document.stationLister.pest.value == 'sooty_blotch') {
			getsootyblotch(0);
		}
		else if (document.stationLister.pest.value == 'apple_scab_estlw') {
			getapplescab_estlw(0);
		}
		else {
			getapplescab(0);
		}
	});
	stateStationMapList({
		reqvar: document.stationLister.pest.value === 'sooty_blotch' ? 'eslw' : 'all',
		event_type: 'select_station',
		where: '#station_area'
	});
	setupNav();
	update_help();
});