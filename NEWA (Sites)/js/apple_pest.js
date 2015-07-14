function update_help() {
	var params = {type: 'apple_pest'};
	$('select[name=pest]').each(function () { params[this.name] = this.value; });
	$.get('http://newa.nrcc.cornell.edu/newaModel/process_help',params,function(data) { $('#third').html(data); });
	return false;
  }

function getresults(bfcnt) {
	var params = {type: 'apple_pest'};
	$('select[name=pest], select[name=stn], input[name=accend], input[name=output]').each(function () { params[this.name] = this.value; });
	if (bfcnt >= 1) {
		$('input[name=bf_date]').each(function () { params[this.name] = this.value; }); }
	if (bfcnt >= 2) {
		$('input[name=bf2_date]').each(function () { params[this.name] = this.value; }); }
	if (bfcnt >= 3) {
		$('input[name=bf3_date]').each(function () { params[this.name] = this.value; }); }
	$.get('http://newa.nrcc.cornell.edu/newaModel/process_input',params,function(data) {
		$("#second").html(data);
		$("#bfdpick").datepicker({ minDate: new Date(2000, 0, 1), maxDate: "+7d", changeMonth: true, changeYear: true });
		$("#bf2dpick").datepicker({ minDate: new Date(2000, 0, 1), maxDate: "+7d", changeMonth: true, changeYear: true });
		$("#bf3dpick").datepicker({ minDate: new Date(2000, 0, 1), maxDate: "+7d", changeMonth: true, changeYear: true });
		$('#righttabs').tabs('select',1);
		});
	return false;
	}

 $(document).ready(function() {
	$("#enddpick").datepicker({ minDate: new Date(2000, 0, 1), maxDate: "", changeMonth: true, changeYear: true });
	var myDate = new Date();
	var todayDate = (myDate.getMonth()+1) + "/" + myDate.getDate() + "/" + myDate.getFullYear();
	$("#enddpick").val(todayDate);
	$("#righttabs").tabs();
	$("form .button").click(function (evt) { getresults(0); });
	stationMap('all','select_station');
  });
