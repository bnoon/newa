function update_page() {
	if (document.stationLister.pest.value == "cruc_zcrmaggot") {
		$("#station_list").show();
	} else {
		$("#station_list").hide();
	}
}

function getresults() {
	var params = {type: 'crucifer_disease'};
	$('select[name=pest], input[name=accend], select[name=stn], input[name=output], input[name=tech_choice]:checked').each(function () { params[this.name] = this.value; });
	$.get('/newaVegModel/process_input',params,function(data) {
		$("#second").html(data);
		$('#righttabs').tabs('select',0);
	});
	$.get('/newaVegModel/process_help',params,function(hdata) { 
		$('#third').html(hdata); 
	});
	return false;
}

function getinfo() {
	var params = {type: 'crucifer_disease', stn: 'xxx'};
	$('input[name=pest], input[name=accend], input[name=output], input[name=tech_choice]:checked').each(function () { params[this.name] = this.value; });
	$.get('/newaVegModel/process_help',params,function(hdata) { 
		$('#third').slideDown('fast').html(hdata); 
	});
	return false;
}

function updateStatus() {
	var params = {type: 'crucifer_disease'};
	$('input[name=pest],select[name=altref],input[name=tech_choice]:checked').each(function () { params[this.name] = this.value; });
	$.get('/newaVegModel/update_status',params,function(data) { 
		$("#manage_status").html(data); 
	});
	$.get('/newaVegModel/process_help',params,function(hdata) { 
		$('#third').html(hdata); 
	});
	return false;
}

 $(document).ready(function() {
 // only do following if using tab interface
	if ($("#enddpick").length > 0) {
		var myDate = new Date();
		var todayDate = (myDate.getMonth()+1) + "/" + myDate.getDate() + "/" + myDate.getFullYear();
		$("#enddpick").datepicker({ minDate: new Date(2000, 0, 1), maxDate: "", changeMonth: true, changeYear: true });
		$("#enddpick").val(todayDate);
		$("#righttabs").tabs();
		$("form .button").click(function (evt) { getresults(); });
//		stationMap('all','select_station');
	}
  });
