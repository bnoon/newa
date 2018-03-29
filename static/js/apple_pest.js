function update_help() {
	var params = {type: 'apple_pest'};
	$('select[name=pest]').each(function () { params[this.name] = this.value; });
	$.get('/newaModel/process_help',params,function(data) { $('#third').html(data); });
	return false;
  }

function getresults(bfcnt) {
	var params = {type: 'apple_pest', accend: $("#enddpick").val()};
//	$('select[name=pest], select[name=stn], input[name=accend], input[name=output]').each(function () { params[this.name] = this.value; });
	$('select[name=pest], select[name=stn], input[name=output]').each(function () { params[this.name] = this.value; });
	if (bfcnt >= 1) {
		$('input[name=bf_date]').each(function () { params[this.name] = this.value; }); }
	if (bfcnt >= 2) {
		$('input[name=bf2_date]').each(function () { params[this.name] = this.value; }); }
	if (bfcnt >= 3) {
		$('input[name=bf3_date]').each(function () { params[this.name] = this.value; }); }
	$('#second').empty().html('<img src="/gifs/ajax-loader.gif" alt="Processing" id="loading" />');
	$('#righttabs').tabs('option', 'active',1);
	$.get('/newaModel/process_input',params,function(data) {
		$('#loading').fadeOut(500, function() {
			$(this).remove();
		});
		$("#second").html(data);
		$("#bfdpick").datepicker({ minDate: new Date(2000, 0, 1), maxDate: "+7d", changeMonth: true, changeYear: true });
		$("#bf2dpick").datepicker({ minDate: new Date(2000, 0, 1), maxDate: "+7d", changeMonth: true, changeYear: true });
		$("#bf3dpick").datepicker({ minDate: new Date(2000, 0, 1), maxDate: "+7d", changeMonth: true, changeYear: true });
	});
	return false;
	}

 $(document).ready(function() {
 	var triggerClick = true;
	$("#enddpick").datepicker({ minDate: new Date(2000, 0, 1), maxDate: "", changeMonth: true, changeYear: true });
	var myDate = new Date();
	var todayDate = (myDate.getMonth()+1) + "/" + myDate.getDate() + "/" + myDate.getFullYear();
	$("#enddpick").val(todayDate);
	$("#righttabs").tabs({
		activate: function () {
			var center = map.getCenter();
			google.maps.event.trigger(map, 'resize');
			map.setCenter(center);
		}
	});
	$("form .button").click(function (evt) { getresults(0); });
	stateStationMapList({
		reqvar: 'all',
		event_type: 'select_station',
		where: '#station_area'
	});
	setupNav(triggerClick);
	update_help();
  });