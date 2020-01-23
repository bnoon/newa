var map;

function setSelectValue(clickedStn) {
	var stnList = $("select[name=stn] option");
	for (var i = 0; i < stnList.length; i += 1) {
		if (stnList[i].value === clickedStn) {
			stnList[i].selected = true;
			$.jStorage.set("stn", stnList[i].value);
			localStorage.setItem("station", JSON.stringify({"id": stnList[i].value}));
			break;
		}
	}
}

function setupNav(triggerClick) {
	var i, navItems = {},
		stateList = $("select[name=stabb] option")
	$('input[name=requestedState], input[name=requestedStation]').each(function () { navItems[this.name] = this.value; });	
	if (navItems.requestedState !== "") {
		for (i = 1; i < stateList.length; i += 1) {
			if (stateList[i].value === navItems.requestedState.toUpperCase()) {
				stateList[i].selected = true;
				$("select[name=stabb]").trigger("change");
				break;
			}
		}
		if (navItems.requestedStation !== "") {
			setTimeout(function() {
				var stnList = $("select[name=stn] option");
				for (i = 1; i < stnList.length; i += 1) {
					if (stnList[i].value === navItems.requestedStation) {
						stnList[i].selected = true;
						$("select[name=stn]").trigger("change");
						break;
					}
				}
			}, 300);
			if (triggerClick) {
				setTimeout(function() {
					$("form .button").trigger("click");
				}, 500);
			}
		}
	}
}

function centerMap (latlngCoords) {
	var center = new google.maps.LatLng(latlngCoords.latitude,latlngCoords.longitude);
	google.maps.event.trigger(map, 'resize');
	map.setCenter(center);
}

//function centerMap (latlngCoords) {
//	var center;
//	latlngCoords.longitude = Math.max(latlngCoords.longitude, -100.0);
//	latlngCoords.longitude = Math.min(latlngCoords.longitude, -71.5);
//	latlngCoords.latitude = Math.max(latlngCoords.latitude, 35.5);
//	latlngCoords.latitude = Math.min(latlngCoords.latitude, 46.3);
//	center = new google.maps.LatLng(latlngCoords.latitude,latlngCoords.longitude);
//	map.setCenter(center);
//	$("#msg").empty().text('Click here to save location')
//		 .click(function() {
//			$("#msg").empty().hide(); 
//			center = map.getCenter();
//			$.cookie("mlocation", JSON.stringify({latitude:center.lat(), longitude:center.lng()}), {expires:180, path:"/", domain:"newa.nrcc.cornell.edu"});
//		 }); 
//}

//function loadLocation () {
//	var defLocation = {latitude:42.95, longitude:-76.35},
//		position = google.loader.ClientLocation;
//	if (position) {
//		centerMap(position);
//	} else {
//		centerMap(defLocation);
//	}
//}

//function getLocation() {
//	$('<div id="msg" style="border:1px solid black; padding:0.25em; position:absolute; left:168px; bottom:0px; width:225px; height:3em; z-index:1; font-size:0.9em; text-align:center; background-color:red; color:white;"></div>').appendTo($("#map"));
//	$("#msg").text('Trying to determine location...'); 
//	if (navigator.geolocation) {
//		navigator.geolocation.getCurrentPosition( 
//			function(position) {
//				centerMap(position.coords);
//			}, 
//			loadLocation, 
//			{timeout:5000} 
//		);
//	} else {
//		loadLocation();
//	}
//}

//function findCenter() {
//	var mc,
//		center = {lat: 42.5, lon: -75.7, zoom: 6},
//		myCookie = $.cookie("mlocation");
//	if (myCookie) { 
//		mc = JSON.parse(myCookie);
//		center = {lat: mc.latitude, lon: mc.longitude, zoom: 6};
//	}
//	return center;
//}

function statePlaceMarkers (cur_data, event_type, state) {
	var stateCenters = {
		'CT': {lat: 41.6220, lon: -72.7272, zoom: 8, name: 'Connecticut'},
		'DE': {lat: 38.9895, lon: -75.5051, zoom: 8, name: 'Delaware'},
		'DC': {lat: 38.9101, lon: -77.0147, zoom: 8, name: 'DC'},
		'ID': {lat: 45.4946, lon: -114.1433, zoom: 6, name: 'Idaho'},
		'IL': {lat: 40.0411, lon: -89.1965, zoom: 6, name: 'Illinois'},
		'IA': {lat: 42.0753, lon: -93.4959, zoom: 6, name: 'Iowa'},
		'KY': {lat: 37.5347, lon: -85.3021, zoom: 6, name: 'Kentucky'},
		'ME': {lat: 45.3702, lon: -69.2438, zoom: 7, name: 'Maine'}, //no stations
		'MD': {lat: 39.0550, lon: -76.7909, zoom: 7, name: 'Maryland'},
		'MA': {lat: 42.2596, lon: -71.8083, zoom: 7, name: 'Massachusetts'},
		'MI': {lat: 44.3461, lon: -85.4114, zoom: 6, name: 'Michigan'},
		'MN': {lat: 46.2810, lon: -94.3046, zoom: 6, name: 'Minnesota'},
		'MO': {lat: 38.3568, lon: -92.4571, zoom: 6, name: 'Missouri'},
		'NE': {lat: 41.5392, lon: -99.7968, zoom: 6, name: 'Nebraska'},
		'NH': {lat: 43.6805, lon: -71.5818, zoom: 7, name: 'New Hampshire'},
		'NJ': {lat: 40.1907, lon: -74.6733, zoom: 7, name: 'New Jersey'},
		'NY': {lat: 42.9543, lon: -75.5262, zoom: 6, name: 'New York'},
		'NC': {lat: 35.5579, lon: -79.3856, zoom: 6, name: 'North Carolina'},
		'OH': {lat: 40.1905, lon: -82.6707, zoom: 7, name: 'Ohio'},
		'PA': {lat: 40.8786, lon: -77.7985, zoom: 7, name: 'Pennsylvania'},
		'RI': {lat: 41.6762, lon: -71.5562, zoom: 9, name: 'Rhode Island'},
		'SC': {lat: 33.6290, lon: -80.9500, zoom: 6, name: 'South Carolina'},
		'SD': {lat: 43.9169, lon: -100.2282, zoom: 6, name: 'South Dakota'},
		'UT': {lat: 39.4998, lon: -111.5470, zoom: 6, name: 'Utah'},
		'VT': {lat: 44.0688, lon: -72.6663, zoom: 7, name: 'Vermont'},
		'VA': {lat: 37.5229, lon: -78.8531, zoom: 7, name: 'Virginia'},
		'WV': {lat: 38.6409, lon: -80.6230, zoom: 7, name: 'West Virginia'},
		'WI': {lat: 44.6243, lon: -89.9941, zoom: 6, name: 'Wisconsin'},
		'AL': {lat: 32.6174, lon: -86.6795, zoom: 7, name:' Alabama'},
		'ALL':{lat: 42.5000, lon: -75.7000, zoom: 6, name: 'All'},
	};
	var stateInfo = stateCenters.hasOwnProperty(state) ? stateCenters[state] : {lat: 42.5, lon: -75.7, zoom: 6, name: 'All'};
	var newaIcon = new google.maps.MarkerImage(
		'/gifs/newa_small.png',
		new google.maps.Size(14,14),
		new google.maps.Point(0,0),
		new google.maps.Point(8,8));
	var newaIconRed = new google.maps.MarkerImage(
		'/gifs/newa_small_red.png',
		new google.maps.Size(14,14),
		new google.maps.Point(0,0),
		new google.maps.Point(8,8));
	var airportIcon = new google.maps.MarkerImage(
		'/gifs/airport.png',
		new google.maps.Size(15,15),
		new google.maps.Point(0,0),
		new google.maps.Point(8,8));
	var culogIcon = new google.maps.MarkerImage(
		'/gifs/culog.png',
		new google.maps.Size(14,14),
		new google.maps.Point(0,0),
		new google.maps.Point(7,7));
	var newaIconGray = new google.maps.MarkerImage(
		'/gifs/newa_smallGray.png',
		new google.maps.Size(14,14),
		new google.maps.Point(0,0),
		new google.maps.Point(8,8));
	var airportIconGray = new google.maps.MarkerImage(
		'/gifs/airportGray.png',
		new google.maps.Size(15,15),
		new google.maps.Point(0,0),
		new google.maps.Point(8,8));
	var culogIconGray = new google.maps.MarkerImage(
		'/gifs/culogGray.png',
		new google.maps.Size(14,14),
		new google.maps.Point(0,0),
		new google.maps.Point(7,7));
	var newaShadow = new google.maps.MarkerImage(
		'/gifs/newa_small_shdw.png',
		new google.maps.Size(24,16),
		new google.maps.Point(0,0),
		new google.maps.Point(8,8));
	var airportShadow = new google.maps.MarkerImage(
		'/gifs/airport_shdw.png',
		new google.maps.Size(23,15),
		new google.maps.Point(0,0),
		new google.maps.Point(8,8));
	var culogShadow = new google.maps.MarkerImage(
		'/gifs/culog_shdw.png',
		new google.maps.Size(21,14),
		new google.maps.Point(0,0),
		new google.maps.Point(7,7));
	var circleIcon = {
		path: google.maps.SymbolPath.CIRCLE,
		scale: 2.5,
		strokeColor: "gray",
		strokeWeight: 5
	};
	var marker,
		markerOptions = {},
		mapOptions = {
			zoom: stateInfo.zoom,
			center: new google.maps.LatLng(stateInfo.lat, stateInfo.lon),
			mapTypeId: google.maps.MapTypeId.TERRAIN,
			mapTypeControl: true,
			mapTypeControlOptions: {
				style: google.maps.MapTypeControlStyle.DROPDOWN_MENU 
			},
			streetViewControl: false,
			scaleControl: true,
			gestureHandling: 'greedy'
		};
	map = new google.maps.Map(document.getElementById("map"), mapOptions);
	markerOptions.map = map;
	$.each(cur_data.stations, function (i,stn) {
		markerOptions.position = new google.maps.LatLng(stn.lat, stn.lon);
		markerOptions.title = stn.name;
		if (stn.network === "newa" || stn.network === "njwx" || stn.network === "miwx" || stn.network === "ucc" || stn.network === "oardc" || stn.network === "nysm" || stn.network === "nwon" || (stn.network === "cu_log" && stn.state !== "NY")) { /////
			markerOptions.icon = stn.state === state || state === "ALL" ? newaIcon : newaIconGray;
		} else if (stn.network === "cu_log") { 
			markerOptions.icon = stn.state === state || state === "ALL" ? culogIcon : culogIconGray; 
		} else if (stn.network === "icao") { 
			markerOptions.icon = stn.state === state || state === "ALL" ? airportIcon : airportIconGray; 
		}
		marker = new google.maps.Marker(markerOptions);
		
		if (stn.state === state || state === 'ALL') {
			if (event_type === "station_page") {
				google.maps.event.addListener(marker, "click", function() {
					top.location.href="http://newa.cornell.edu/index.php?page=weather-station-page&WeatherStation="+stn.id;
					$.jStorage.set("stn", stn.id);
					localStorage.setItem("station", JSON.stringify({"id": stn.id}));
				});
			} else if (event_type === "select_station") {
				google.maps.event.addListener(marker, "click", function() {
					setSelectValue(stn.id);
				});
			}
		} else {
			google.maps.event.addListener(marker, "click", function() {
				alert("Select " + stateCenters[stn.state].name + " from the State menu to access this station.");
			});
		}

	});
//	if (! $.cookie("mlocation")) { 
//		getLocation();
//	}
}

function buildStationMenu(results, where, state) {
	var sid = JSON.parse(localStorage.getItem("station")) || null,
		saved_stn = sid ? sid.id : null || $.jStorage.get("stn");
	if (!where) {
		where = "#station_area";
	}
	if ($('select[name=stn]').length > 0) {
		$('select[name=stn]').empty();
	} else {
		$(where).append('<p style="margin-bottom:3px;">Weather station:<\/p><select name="stn"><\/select>');
	}
	$('select[name=stn]').append('<option value="" selected>Select a station<\/option>');
	$.each(results.stations, function (i,stn) {
		if (stn.state === state || state === 'ALL') {
			if (state === 'ALL') {
				stn.name = stn.name + ', ' + stn.state;		// add state abbreviation
			}
			$('select[name=stn]').append('<option value="' + stn.id + '">' + stn.name + '<\/option>');
			if (stn.id === saved_stn) {
				$('select[name=stn] option:last-child').prop('selected', true);
			}
		}
	});	
	$('select[name=stn]').on("change", function () {
		localStorage.setItem("station", JSON.stringify({"id": $(this).val()}));
	});
}

function stateStationMap (options) {
	var list_type = options.reqvar || 'all',
		event_type = options.event_type || 'station_page',
		state = options.state || "ALL";
	if (options.state && state.toUpperCase() !== 'ALL') {
		$.jStorage.set("state", state);
		localStorage.setItem("state", JSON.stringify({"postalCode": state}));		
	}
	$.getJSON("/newaUtil/stateStationList/"+list_type+"/"+"ALL")
		.success( function(results) { statePlaceMarkers(results,event_type,state); } )
		.error( function() {
			$('<div id="msg" style="border:1px solid black; padding:0.25em; position:absolute; left:168px; bottom:0px; width:225px; z-index:1; font-size:0.9em; text-align:center; background-color:red; color:white;"></div>').appendTo($("#map"));
			$("#msg").text('Error retrieving station list'); 
		} 
	);
}

function stateStationMapList (options) {
	var i,
		selected_index = 0,
		list_type = options.reqvar || 'all',
		event_type = options.event_type || 'select_station',
		postalCode = JSON.parse(localStorage.getItem("state")) || null,
		state = options.state || postalCode ? postalCode.postalCode : null || $.jStorage.get("state"),
		where = options.where || "#station_area",
		drawmap = options.drawmap || true,
		state_list = [
			['AL', 'Alabama'],
			['CT', 'Connecticut'],
			['DE', 'Delaware'],
			['DC', 'DC'],
			['ID', 'Idaho'],
			['IL', 'Illinois'],
			['IA', 'Iowa'],
			['KY', 'Kentucky'],
			['MD', 'Maryland'],
			['MA', 'Massachusetts'],
			['MI', 'Michigan'],
			['MN', 'Minnesota'],
			['MO', 'Missouri'],
			['NE', 'Nebraska'],
			['NH', 'New Hampshire'],
			['NJ', 'New Jersey'],
			['NY', 'New York'],
			['NC', 'North Carolina'],
			['OH', 'Ohio'],
			['PA', 'Pennsylvania'],
			['RI', 'Rhode Island'],
			['SC', 'South Carolina'],
			['SD', 'South Dakota'],
			['UT', 'Utah'],
			['VT', 'Vermont'],
			['VA', 'Virginia'],
			['WV', 'West Virginia'],
			['WI', 'Wisconsin'],
			['ALL', 'All states']
		],
		showStations = function () {
			$.getJSON("/newaUtil/stateStationList/"+list_type+"/"+"ALL")
				.success( function(results) {
					if (drawmap) {
						statePlaceMarkers(results, event_type, state);
					}
					buildStationMenu(results, where, state);
				})
				.error( function() {
					$('<div id="msg" style="border:1px solid black; padding:0.25em; position:absolute; left:168px; bottom:0px; width:225px; z-index:1; font-size:0.9em; text-align:center; background-color:red; color:white;"></div>').appendTo($("#map"));
					$("#msg").text('Error retrieving station list'); 
				});
		};
	$(where).empty().append('<p style="margin-bottom:3px;">State:<\/p><select name="stabb"><\/select>');
	$.each(state_list, function (i, st) {
		$("select[name=stabb]").append('<option value=' + st[0] + '>' + st[1] + '<\/option>');
		if (st[0] === state) {
			selected_index = i+1;
		}
	});
	$('select[name=stabb]')
		.prepend('<option value="">Select state<\/option>')
		.prop('selectedIndex', selected_index)
		.on("change", function() {
			state = $("select[name=stabb]").val();
			localStorage.setItem("state", JSON.stringify({"postalCode": state}));
			$("#noStateMsg").hide();
			showStations();
		});
	if (! state && $('#first').length > 0) {
		$("#first").prepend('<div id="noStateMsg" style="margin:2em;"><p>Select a state from the menu to the left.</p></div>');
	} else {
		$('select[name=stabb]').trigger("change");
	}
}

function zoomMarkCenter(results) {
	var marker;
	var markerOptions = {};
	var mapOptions = {
		mapTypeId: google.maps.MapTypeId.SATELLITE,
		mapTypeControl: true,
		streetViewControl: false,
		mapTypeControlOptions: { style: google.maps.MapTypeControlStyle.DROPDOWN_MENU }
	};
	var maxZoomService = new google.maps.MaxZoomService();
	mapOptions.center = new google.maps.LatLng(results.metadata.lat, results.metadata.lon);
	maxZoomService.getMaxZoomAtLatLng(mapOptions.center, function(response) {
		mapOptions.zoom = (response && response.status === google.maps.MaxZoomStatus.OK) ? Math.min(response.zoom,16) : 12;
		var map = new google.maps.Map(document.getElementById("map"), mapOptions);
		markerOptions.map = map;
		markerOptions.position = mapOptions.center;
		marker = new google.maps.Marker(markerOptions);
	});
}

function zoomStation (reqstn) {
	$.getJSON("/newaUtil/stationInfo/"+reqstn)
		.success( zoomMarkCenter )  
		.error( function() { 
			return false;
		} 
	);
}
