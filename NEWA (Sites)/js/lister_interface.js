function buildStationLists(state) {
	$.getJSON("http://newatest.nrcc.cornell.edu/newaUtil/stateStationList/all/ALL")
		.success( function(results) {
			var saved_stn = $.jStorage.get("stn"),
				otype = $("input[name=type]").val(),
				trow = "",
				today = new Date(),
				crntMonth = today.getMonth(),
				crntYear = today.getFullYear(),
				month_list = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
			$('select[name=stn]').empty().append('<option value="" selected>Select a station<\/option>');
			$("#stationListTable").empty();
			$.each(results.stations, function (i,stn) {
				if (stn.state === state || state === 'ALL') {
					if (state === 'ALL') {
						stn.name = stn.name + ', ' + stn.state;		// add state abbreviation
					}
					$('select[name=stn]').append('<option value="' + stn.id + '">' + stn.name + '<\/option>');
					if (stn.id === saved_stn) {
						$('select[name=stn] option:last-child').prop('selected', true);
					}
					trow = "";
					for (m = 0; m < 12; m += 1) {
						if (m <= crntMonth) {
							trow += '<td><A HREF="http://newa.nrcc.cornell.edu/newaLister/' + otype + '/' + stn.id + '/' + crntYear + '/' + (m + 1) + '">' + month_list[m] + '</A> |</td>';
						} else {
							break;
						}
					}
					$("#stationListTable").append('<tr><th style="text-align:left;">' + stn.name + '</th>' + trow + '</tr>');
				}
			});
			// now get inactive stations
			$.getJSON("http://newatest.nrcc.cornell.edu/newaUtil/stateInactiveStationList/all/ALL")
				.success( function(inactive_results) {
					$.each(inactive_results.stations, function (i,stn) {
						if (stn.state === state || state === 'ALL') {
							if (state === 'ALL') {
								stn.name = stn.name + ', ' + stn.state;
							}
							$('select[name=stn]').append('<option value="' + stn.id + '">' + stn.name + ' (inactive)<\/option>');
							if (stn.id === saved_stn) {
								$('select[name=stn] option:last-child').prop('selected', true);
							}
						}
					});
				});
			$('select[name=stn]').on("change", function () {
				$.jStorage.set("stn", $(this).val());		
			});
		})
		.error( function() {
			$('<div id="msg" style="border:1px solid black; padding:0.25em; position:absolute; left:168px; bottom:0px; width:225px; z-index:1; font-size:0.9em; text-align:center; background-color:red; color:white;"></div>').appendTo("#station_area");
			$("#msg").text('Error retrieving station list'); 
		});
}
function buildStateStationMenus() {
	var i,
		state = $.jStorage.get("state"),
		state_list = [
			['CT', 'Connecticut'],
			['DC', 'DC'],
			['DE', 'Delaware'],
			['IA', 'Iowa'],
			['IL', 'Illinois'],
			['MA', 'Massachusetts'],
			['MD', 'Maryland'],
			['MN', 'Minnesota'],
			['MO', 'Missouri'],
			['NC', 'North Carolina'],
			['NE', 'Nebraska'],
			['NH', 'New Hampshire'],
			['NJ', 'New Jersey'],
			['NY', 'New York'],
			['PA', 'Pennsylvania'],
			['RI', 'Rhode Island'],
			['SC', 'South Carolina'],
			['SD', 'South Dakota'],
			['VA', 'Virginia'],
			['VT', 'Vermont'],
			['WI', 'Wisconsin'],
			['ALL', 'All states']
		];
	$.each(state_list, function (i, st) {
		$("select[name=stabb]").append('<option value=' + st[0] + '>' + st[1] + '<\/option>');
	});
	$('select[name=stabb]')
		.prepend('<option value="">Select state<\/option>')
		.prop('selectedIndex', 0)
		.on("change", function() {
			state = $("select[name=stabb]").val();
			$.jStorage.set("state", state);
			buildStationLists(state);
		});
	if (state) {
		for (i = 0; i < state_list.length; i += 1) {
			if (state_list[i][0] === state) {
				$('select[name=stabb]').prop('selectedIndex', i + 1);
				buildStationLists(state);
				break;
			}
		}
	} else {
		if ($('#noStateMsg').length > 0) {
			$("#stationMenu").hide();
			$("#noStateMsg").empty().append('<span style=font-weight:bold;font-size:1.2em;margin-left:3em;">Select a state from the menu to the left.</span>');
			$("select[name=stabb]").one('change', function () {
				$("#noStateMsg").empty();
				$("#stationMenu").show();
				$('#stationTableArea').show();
			});
		}
	}
}