newaLister_estimates_togo = null;	// ***** GLOBAL *****

function postSuccess(results, callback, cb_args) {
	if (!results.error) {
		callback(results, cb_args);
	} else {
		$("#newaListerResults").empty().append("Error obtaining data");
	}
}

function postContinue(results, callback, cb_args) {
	// any results.error handling within callback
	callback(results, cb_args);
}

function postError() {
	$("#newaListerResults").empty().append("Ajax error obtaining data");
}

// calculate dewpoint from temp and rh
function calc_dewpoint(data) {
	var tempc, sat, vp, logvp, dewptc, dewpt,
		dewptr = "-",
		temp = (data[23] || data[126]).replace(/s|e/, ""),
		rhum =( data[24] || data[143]).replace(/s|e/, "");
	if (temp !== "M" && rhum !== "M" && rhum > 0) {
		tempc = (5.0 / 9.0) * (temp - 32.0);
		sat = 6.11 * Math.pow(10.0, (7.5 * tempc/(237.7 + tempc)));
		vp = (rhum * sat) / 100.0;
		logvp = Math.log(vp);
		dewptc = (-430.22+237.7 * logvp) / (-logvp + 19.08);
		dewpt = ((9.0 / 5.0) * dewptc) + 32.0;
		dewptr = Number(Math.round(dewpt + 'e0') + 'e-0');
	}
	return dewptr;
}

// add footer to bottom of output with logos and text message between
function addFooter(message) {
	var imgsrc = "http://newa.nrcc.cornell.edu/gifs/";
	$("#newaListerResults").append('<div id="newaListerFooter"></div>');
	$("#newaListerFooter").append('<a class="newalogo" href="http://newa.cornell.edu" target="_blank"></a>' +
		'<div class="fd-center"></div>' +
		'<a class="acislogo" href="http://www.nrcc.cornell.edu" target="_blank"></a>');
	$("#newaListerFooter a.newalogo").append('<img src="' + imgsrc + 'newa_logo.jpg" alt="NEWA" />');
	$("#newaListerFooter a.acislogo").append('<img src="' + imgsrc + 'PoweredbyACIS_NRCC.jpg" alt="NRCC" />');
	$("#newaListerFooter div.fd-center").append(message);
}

// remove hours that aren't in requested month and missing data at end of current month
function trimResults(input_params, serialized_array) {
	var i, this_ymd,
		ymd = input_params.edate.split("-"),
		requested_month = parseInt(ymd[1]),
		foundobs = false;
	// if it is the current month, remove all non-observed data at end of month
	if (moment(input_params.edate, "YYYY-MM-DD").isSame(moment.now(), 'month')) {
		for (i = serialized_array.length - 1; i >= 0; i -= 1) {
			$.each(serialized_array[i], function(index, value) {
				if (index !== 'date' && value !== "M" && value.search(/e|s|f/) < 0 && !foundobs) {
					foundobs = true;
				} 
			});
			if (!foundobs) {
				serialized_array.splice(i, 1);
			} else {
				break;
			}
		}
	}
	// remove any data not in requested month
	for (i = serialized_array.length - 1; i >= 0; i -= 1) {
		this_ymd = moment(serialized_array[i].date, 'MM/DD/YYYY HH:00 z');
		if (parseInt(this_ymd.month() + 1) !== requested_month) {
			serialized_array.splice(i, 1);
		}
	}	
	return serialized_array;
}

// display hourly data lister table
function hourlyLister(cb_args) {
	var hrly_data = cb_args.hrly_data,
		input_params = cb_args.input_params,
		stnName = cb_args.stnName,
		stnid = input_params.sid.split(" "),
		ymd = input_params.edate.split("-"),
		serialized_array = Object.values(hrly_data),	// convert serialized results object into array of objects (formatted for DataTables)
		eVx = ['date'].concat(input_params.elems.map(function(elem){return elem.vX;})),
		calcDewpt = !eVx.includes(22) && (eVx.includes(23) || eVx.includes(126)) && (eVx.includes(24) || eVx.includes(143)),
		elem_info = {
			date:   {title: 'Date/Time'},
			5:   {title: 'Precip (inches)'},
			22:  {title: 'Dewpoint (&#8457;)'},
			23:  {title: 'Air Temp (&#8457;)'},
			24:  {title: 'RH (%)'},
			27:  {title: 'Wind Dir (degrees)'},
			28:  {title: 'Wind Spd (mph)'},
			65:  {title: 'Soil Tension (kPa)'},
			118: {title: 'Leaf Wetness (minutes)'},
			120: {title: 'Soil Temp (&#8457;)'},
			126: {title: 'Temperature (&#8457;)'},
			128: {title: 'Wind Spd (mph)'},
			130: {title: 'Wind Dir (degrees)'},
			132: {title: 'Solar Rad (langleys)'},
			143: {title: 'RH (percent)'},
			149: {title: 'Solar Rad (watts/m2)'},
		},
		dt_options = {
			searching: false,
			paging: false,
			info: false,
			scrollX: true,
			scrollY: 530,
			order: [[ 0, 'dsc' ]],
			data: serialized_array,
			columns: eVx.map(function(vx) {
				return { data: vx, title: elem_info[vx].title };
			}),
			rowCallback: function(row, data, index) {
				eVx.forEach(function(vx, i) {
					if (data[vx].search(/e|s|f/) >= 0) {
						$('td:eq(' + i + ')', row).addClass('newaListerEstimated').html(data[vx].replace(/e|f|s/, ''));
//						$('td:eq(' + i + ')', row).addClass('newaListerEstimated').html(data[vx]);	// replaces above for testing
					} else if (data[vx] === 'M') {
						$('td:eq(' + i + ')', row).html("-");
					}
				});
			}
		},
		footer_message = '<div><span>Values in </span><span class="newaListerEstimated">brown italics </span>' +
			'<span>were estimated from adjacent hours or a nearby location. ' +
			'<a href="http://newa.nrcc.cornell.edu/newaLister/est_info/' + 
			stnid[0] + '/' + ymd[0] + '/' +  ymd[1] + '">' + 
			'More information</a> is available on the estimation technique.</span></div>';		
	// remove unwanted results	
	serialized_array = trimResults(input_params, serialized_array);
	// table element
	$("#newaListerResults").empty().append('<table id="dtable" class="stripe compact hover cell-border"></table>');
	// table caption is station name
	$("#dtable").append('<caption>' + stnName + ' - Hourly Data Summary</caption>');
	// if dewpt is not in dataset, have dataTables compute and insert it
	if (calcDewpt) {
		dt_options.columns.push({
			data:  null,
			title: elem_info[22].title,
			render: calc_dewpoint
		});
	}
	// load data into DataTable
	$('#dtable').DataTable(dt_options);
	// add page footer with text and logos
	addFooter(footer_message);
	$("div.dataTables_scrollBody").one("scroll", function() {
		$("table.dataTable caption").remove();
	});
}

// convert time in local standard time to local time (based on time zone and dst)
function formatTime (day, hour, tzo) {
	var time_zone_name = {
		5: 'America/New_York',
		6: 'America/Chicago',
		7: 'America/Denver',
		8: 'America/Los_Angeles'
	};
	return moment.utc(day).hour(hour).add(tzo, "hours").tz(time_zone_name[tzo]).format('MM/DD/YYYY HH:00 z');
}

// convert from ACIS results object to new object keyed on date/time (i.e. one record per hour)
function serializeObject(results, input_params) {
	var hlydate, dt_key, hrly_data = {},
		data = results.data,
		tzo = -results.meta.tzo,
		elems = typeof input_params === 'string' ? [input_params] : input_params.elems.map(function(elem){return elem.vX;});
	if (data && data.length > 0) {
		data.forEach(function(dlyrec) {
			hlydate = dlyrec[0];
			for (var h = 1; h <= 24; h += 1) {
				dt_key = [hlydate, h].join("-");
				hrly_data[dt_key] = {};
				hrly_data[dt_key].date = formatTime(hlydate, h, tzo);
				dlyrec.slice(1).forEach(function(elval, ie) {
					hrly_data[dt_key][elems[ie]] = elval[h - 1];
				});
			}
		});
	}
	return hrly_data;
}

function forecastEstimates(results, cb_args) {
	var meta = {meta: {tzo: -cb_args.tzo}},
		hrly_data = cb_args.hrly_data,
		forecast_data = (results.data && results.data.length) ? serializeObject($.extend(results, meta), cb_args.est_for_elem) : null;
	// fill in forecast data for missing values
	if (forecast_data) {
		$.each(hrly_data, function(key, record) {
			var elem_val = record[cb_args.est_for_elem];
			if (elem_val === "M") {
				var estimate = forecast_data[key][cb_args.est_for_elem];
				if (estimate !== "M") {
					hrly_data[key][cb_args.est_for_elem] = estimate + "f";
				}
			}
		});
	}
	newaLister_estimates_togo -= 1;								// ***** GLOBAL *****
	if (newaLister_estimates_togo === 0) {
		cb_args.productCallback($.extend(cb_args, { hrly_data: hrly_data }));
//		hourlyLister( $.extend(cb_args, { hrly_data: hrly_data }));
	}
}

// get forecast data
function getForecastData(cb_args) {
	var vx_abbr = {
			23:  'temp',
			24:  'rhum',
			28:  'wspd',
			126: 'temp',
			128: 'wspd',
			143: 'rhum'
		},
		est_for_elem = cb_args.est_for_elem,
		url = 'http://newa.nrcc.cornell.edu/newaUtil/getFcstData/' + cb_args.input_params.sid.replace(' ', '/') + '/' + vx_abbr[cb_args.est_for_elem] + '/' + cb_args.input_params.sdate + '/' + cb_args.input_params.edate;
	$.ajax(url, {
		type: 'POST',
		dataType: 'json',
		crossDamain: true,
		success: function (results) {
			postContinue(results, forecastEstimates, $.extend(cb_args, {"est_for_elem": est_for_elem}) ); 
		},
		error:  function (err) {
			postContinue({}, forecastEstimates, $.extend(cb_args, {"est_for_elem": est_for_elem}));
		}
	});
}

// sister estimates
function sisterEstimates(results, cb_args) {
	var est_for_elem = cb_args.est_for_elem,
		hrly_data = cb_args.hrly_data,
		sister_data = (results.data && results.data.length) ? serializeObject(results, est_for_elem) : null,	// serialize sister station data for easier access
		moreMissing = sister_data ? false : true;
	// fill in sister station data for missing values
	if (sister_data) {
		$.each(hrly_data, function(key, record) {
			var elem_val = record[est_for_elem];
			if (elem_val === "M") {
				var estimate = sister_data[key][est_for_elem];
				if (estimate !== "M") {
					hrly_data[key][est_for_elem] = estimate + "s";
				} else {
					moreMissing = true;
				}
			}
		});
	}
	if (moreMissing && ['23','126','24','143','28','128'].includes(est_for_elem)) {
		getForecastData($.extend(cb_args, { hrly_data: hrly_data }));
		return false;
	}
	newaLister_estimates_togo -= 1;								// ***** GLOBAL *****
	// all sister data processed; produce table
	if (newaLister_estimates_togo === 0) {
		cb_args.productCallback($.extend(cb_args, { hrly_data: hrly_data }));
//		hourlyLister( $.extend(cb_args, { hrly_data: hrly_data }));
	}
}

function getSisterData(sister_station, cb_args) {
	var url = "http://data.nrcc.rcc-acis.org/StnData",
		input_params = cb_args.input_params,
		missing_elems = cb_args.missing_elems,
		vx_abbr = {
			5:   'prcp',	//sister station abbreviation for precipitation
			23:  'temp',
			24:  'rhum',
			27:  'wdir',
			28:  'wspd',
			65:  'sm4i',
			118: 'lwet',
			120: 'st4i',
			126: 'temp',
			128: 'wspd',
			130: 'wdir',
			132: 'srad',
			143: 'rhum',
			149: 'srad'
		},
		vx_defs = {
			'newa':  {'pcpn': 5, 'temp':  23, 'rhum':  24, 'lwet': 118, 'wspd': 128, 'wdir': 130, 'srad': 132, 'st4i': 120, 'sm4i': 65 },
			'icao':  {'pcpn': 5, 'temp':  23, 'rhum':  24, 'wspd':  28, 'wdir':  27, 'dwpt':  22 },
			'cu_log':{'pcpn': 5, 'temp': 126, 'rhum':  24, 'lwet': 118, 'wspd': 128, 'wdir': 130, 'srad': 132 },
			'culog': {'pcpn': 5, 'temp': 126, 'rhum':  24, 'lwet': 118, 'wspd': 128, 'wdir': 130, 'srad': 132 },
			'njwx':  {'pcpn': 5, 'temp':  23, 'rhum':  24, 'wspd':  28, 'wdir':  27, 'srad': 149 },
			'miwx':  {'pcpn': 5, 'temp': 126, 'rhum': 143, 'lwet': 118, 'srad': 132 },
			'oardc': {'pcpn': 5, 'temp':  23, 'rhum':  24, 'lwet': 118, 'wspd':  28, 'wdir':  27, 'srad': 132 }
		};
	newaLister_estimates_togo = missing_elems.length;		// ***** GLOBAL *****
	missing_elems.forEach(function(vx) {
		var esister = sister_station[vx_abbr[vx]],
			sister_sid_type = esister ? esister.split(" ")[1] : null,
			est_input_params = {
				sid: esister,
				sdate: input_params.sdate,
				edate: input_params.edate,
				elems: [],
				meta: "tzo"
			};	
		if (sister_sid_type) {
			est_input_params.elems = [{vX: vx_defs[sister_sid_type][vx_abbr[vx].replace('prcp','pcpn')]}];
			if (['temp','wspd'].includes(vx_abbr[vx])) {
				$.extend(est_input_params.elems[0], {"prec":1});
			}
			$.ajax(url, {
				type: 'POST',
				data: JSON.stringify({params:est_input_params}),
				dataType: 'json',
				contentType: 'application/json',
				crossDamain: true,
				success: function (estresults) {
					postContinue(estresults, sisterEstimates, $.extend(cb_args, {"est_for_elem": vx}));
				},
				error: function (err) {
					postContinue({}, sisterEstimates, $.extend(cb_args, {"est_for_elem": vx}));
				}
			});
		} else {
			sisterEstimates({}, $.extend(cb_args, {"est_for_elem": vx}));
			return false;
		}
	});
}

// attempt to estimate missing data
function doEstimation(results, cb_args) {
	var input_params = cb_args.input_params,
		hrly_data = serializeObject(results, input_params),
		moreMissing = [],
		replacements = {},
		now_moment = moment.now();
	// estimate missing values using values before and after. Save to separate object so estimates aren't used in subsequent estimations
	$.each(hrly_data, function(key, record) {
		var key_moment = moment(key, "YYYY-MM-DD-H");
		if (key_moment > now_moment) {
			hrly_data[key] = {};
		} else {
			var ymdh = key.split("-");
			var hour = parseInt(ymdh[3]);
			var next = ymdh.slice(0,3).join("-") + "-" + (hour +  1);
			var prev = hour !== 1 ? key_moment.add(-1, "hours").format("YYYY-MM-DD-H") : key_moment.add(-2, "hours").format("YYYY-MM-DD-24");
			$.each(record, function(elem, elem_val) {
				if (elem_val === "M" && ['22','23','24','28','118','126','128','132','143','149','120','65'].includes(elem)) {
					var next_val = hrly_data.hasOwnProperty(next) ? hrly_data[next][elem] : "M";
					var prev_val = hrly_data.hasOwnProperty(prev) ? hrly_data[prev][elem] : "M";
					var estimate = (prev_val !== "M" && next_val != "M") ? ((parseFloat(prev_val) + parseFloat(next_val)) / 2.0).toFixed(1) : null;
					if (estimate) {
						if (!replacements.hasOwnProperty(key)) {
							replacements[key] = {};
						}
						if (['24', '118', '143'].includes(elem)) {	//round leaf wetness and RH
							estimate = Math.round(estimate);
						}
						replacements[key][elem] = estimate + "e";
					} else if (!moreMissing.includes(elem) && elem !== '65') {
						moreMissing.push(elem);
					}
				} else if (elem_val === "M") {
					if (!moreMissing.includes(elem)) {
						moreMissing.push(elem);
					}
				}
			});
		}
	});
	// add all these estimates to the results object now
	$.extend(true, hrly_data, replacements);	// "true" for recursive extend
	cb_args = $.extend(cb_args, { hrly_data: hrly_data, missing_elems: moreMissing });
	if (moreMissing.length) {
		// sister station estimation begins; first get sister stations
		var url = 'http://newa.nrcc.cornell.edu/newaUtil/stationSisterInfo/' + input_params.sid.replace(' ', '/');
		$("#newaListerResults").append("<br/>...Attempting to fill missing data");
		$.ajax(url, {
			type: 'POST',
			dataType: 'json',
			crossDamain: true,
			success: function (sister_results) {
				postContinue(sister_results, getSisterData, cb_args); 
			},
			error: function (err) {
				console.log('Error obtaining sister station data for ' + input_params.sid + '; continuing with no filling');
				cb_args.productCallback(cb_args);
//				hourlyLister(cb_args);
				return false;
			}
		});
	} else {
		cb_args.productCallback(cb_args);
//		hourlyLister(cb_args);
	}
}

// obtain requested data and pass to estimation routine
function getHourlyData(cb_args) {
	var url = "http://data.nrcc.rcc-acis.org/StnData",
		rinput = cb_args.input_params,
		input_params = {
			sid: rinput.sids,
			sdate: rinput.sdate,
			edate: rinput.edate,
			elems: [],
			meta: "tzo"
		},
		tempAndWspd = [23, 126, 28, 128];
	rinput.elems.forEach(function(elem) {
		var addElem = {vX: elem};
		if (tempAndWspd.includes(elem)) {
			$.extend(addElem, {"prec":1});
		}
		input_params.elems.push(addElem);
	});
	$("#newaListerResults").append("<br/>...Obtaining station data");
	$.ajax(url, {
		type: 'POST',
		data: JSON.stringify({params:input_params}),
		dataType: 'json',
		contentType: 'application/json',
		crossDamain: true,
		success: function (results) { postSuccess(results, doEstimation, $.extend(cb_args, {"input_params": input_params})); },
		error: postError
	});
}

// filter out elements with no data in the requested date range
function filterElems(results, cb_args) {
	var early_date, late_date, data_starts = [], data_ends = [],
		vdr = (results.meta && results.meta.length) ? results.meta[0].valid_daterange : [],
		input_params = cb_args.input_params,
		evx = input_params.elems,
		avail_elems = [],
		elem_info = {
			5:   'Precipitation',
			22:  'Dewpoint',
			23:  'Temperature',
			24:  'Relative Humidity',
			27:  'Wind Direction',
			28:  'Wind Speed',
			65:  'Soil Tension',
			118: 'Leaf Wetness',
			120: 'Soil Temperature',
			126: 'Temperature',
			128: 'Wind Speed',
			130: 'Wind Direction',
			132: 'Solar Radiation',
			143: 'Relative Humidity',
			149: 'Solar Radiation',
		};
	vdr.forEach(function(elemdr, i) {
		if (elemdr.length && input_params.sdate <= elemdr[1] && input_params.edate >= elemdr[0]) {
			avail_elems.push(evx[i]);
			data_starts.push(elemdr[0]);
			data_ends.push(elemdr[1]);
		}
	});
	if (avail_elems.length) {
		$.extend(input_params, {elems:avail_elems});
		early_date = data_starts.sort()[0];
		if (input_params.sdate < early_date) {
			input_params.sdate = early_date;
		}
		late_date = data_ends.sort()[data_ends.length - 1];
		if (input_params.edate > late_date) {
			input_params.edate = late_date;
		}
		getHourlyData($.extend(cb_args, {"input_params":input_params, "stnName": results.meta[0].name, "tzo": -results.meta[0].tzo}));
	} else {
		$("#newaListerResults").empty().append("<p>No data for requested date range for this station. Available date ranges:</p>");
		$("#newaListerResults").append("<ul id='adrs'></ul>");
		vdr.forEach(function(elemdr, i) {
			if (elemdr.length) {
				$("#adrs").append("<li>" + elem_info[evx[i]] + ": " + elemdr[0] + " to " + elemdr[1] + "</li>");
			}
		});
	}
}

// get valid date range for each requested element
function getMeta(rinput) {
	var url = "http://data.nrcc.rcc-acis.org/StnMeta",
		vx_defs = {
			'newa':  {'pcpn': 5, 'temp':  23, 'rhum':  24, 'lwet': 118, 'wspd': 128, 'wdir': 130, 'srad': 132, 'st4i': 120, 'sm4i': 65 },
			'icao':  {'pcpn': 5, 'temp':  23, 'rhum':  24, 'wspd':  28, 'wdir':  27, 'dwpt':  22 },
			'cu_log':{'pcpn': 5, 'temp': 126, 'rhum':  24, 'lwet': 118, 'wspd': 128, 'wdir': 130, 'srad': 132 },
			'culog': {'pcpn': 5, 'temp': 126, 'rhum':  24, 'lwet': 118, 'wspd': 128, 'wdir': 130, 'srad': 132 },
			'njwx':  {'pcpn': 5, 'temp':  23, 'rhum':  24, 'wspd':  28, 'wdir':  27, 'srad': 149 },
			'miwx':  {'pcpn': 5, 'temp': 126, 'rhum': 143, 'lwet': 118, 'srad': 132 },
			'oardc': {'pcpn': 5, 'temp':  23, 'rhum':  24, 'lwet': 118, 'wspd':  28, 'wdir':  27, 'srad': 132, 'st4i': 120 }
		},
		input_params = {
			sids: [rinput.stn_id, rinput.stn_type].join(" "),
			sdate: rinput.sdate,
			edate: rinput.edate,
			meta: "valid_daterange,name,tzo",
			elems:[]
		};
	rinput.requested_elems.forEach(function(elem) {
		if (vx_defs[rinput.stn_type].hasOwnProperty(elem)) {
			input_params.elems.push(vx_defs[rinput.stn_type][elem]);
		}
	});
	$("#newaListerResults").append("<br/>...Determining available data");
	$.ajax(url, {
		type: 'POST',
		data: JSON.stringify({params:input_params}),
		dataType: 'json',
		contentType: 'application/json',
		crossDamain: true,
		success: function (results) { postSuccess(results, filterElems, {input_params: input_params, productCallback: rinput.productCallback}); },
		error: postError
	});
}

function runHourlyLister(stn_id, stn_type, year, month) {
	var rinput = {
			stn_id: stn_id,
			stn_type: stn_type,
			sdate: moment([year, month-1, 1]).subtract(1, 'day').format("YYYY-MM-DD"),
			edate: moment([year, month-1, 1]).endOf('month').format("YYYY-MM-DD"),
			requested_elems: ['temp','dwpt','pcpn','lwet','rhum','wspd','wdir','srad','st4i','sm4i'],
			productCallback: hourlyLister
		};
	getMeta(rinput);
}