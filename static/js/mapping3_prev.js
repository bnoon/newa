var newaIcon = new google.maps.MarkerImage(
	'../gifs/newa_small.png',
	new google.maps.Size(16,16),
	new google.maps.Point(0,0),
	new google.maps.Point(8,8));
var airportIcon = new google.maps.MarkerImage(
	'../gifs/airport.png',
	new google.maps.Size(15,15),
	new google.maps.Point(0,0),
	new google.maps.Point(8,8));
var culogIcon = new google.maps.MarkerImage(
	'../gifs/culog.png',
	new google.maps.Size(14,14),
	new google.maps.Point(0,0),
	new google.maps.Point(7,7));
var newaShadow = new google.maps.MarkerImage(
	'../gifs/newa_small_shdw.png',
	new google.maps.Size(24,16),
	new google.maps.Point(0,0),
	new google.maps.Point(8,8));
var airportShadow = new google.maps.MarkerImage(
	'../gifs/airport_shdw.png',
	new google.maps.Size(23,15),
	new google.maps.Point(0,0),
	new google.maps.Point(8,8));
var culogShadow = new google.maps.MarkerImage(
	'../gifs/culog_shdw.png',
	new google.maps.Size(21,14),
	new google.maps.Point(0,0),
	new google.maps.Point(7,7));
//var newaShape = {
//	coords : [7,0,9,1,10,2,11,3,12,4,12,5,12,6,12,7,12,8,12,9,11,10,11,11,10,12,9,13,
//			 8,14,2,14,2,13,1,12,1,11,1,10,1,9,1,8,2,7,2,6,3,5,3,4,4,3,6,2,5,1,5,0],
//	type : 'poly'
//};
//var airportShape = {
//	coords : [8,0,8,1,8,2,8,3,8,4,8,5,10,6,12,7,13,8,14,9,14,10,8,11,9,12,9,13,9,14,5,
//			 14,5,13,5,12,6,11,0,10,0,9,1,8,2,7,4,6,6,5,6,4,6,3,6,2,6,1,6,0],
//	type : 'poly'
//};
//var culogShape = {
//	coords : [9,0,11,1,12,2,12,3,13,4,13,5,13,6,13,7,13,8,13,9,12,10,11,11,10,12,9,13,
//			  4,13,2,12,2,11,1,10,0,9,0,8,0,7,0,6,0,5,0,4,1,3,1,2,3,1,4,0],
//	type: 'poly'
//};


function placeMarkers (cur_data, event_type) {
	var marker;
	var markerOptions = {};
	var myLatlng = new google.maps.LatLng(42.95, -76.35);
	var mapOptions = {
		zoom: 7,
		center: myLatlng,
		mapTypeId: google.maps.MapTypeId.TERRAIN,
		mapTypeControl: true,
		mapTypeControlOptions: {
			style: google.maps.MapTypeControlStyle.DROPDOWN_MENU 
		},
		streetViewControl: false,
		scaleControl: true
	};
	var map = new google.maps.Map(document.getElementById("map"), mapOptions);
	markerOptions.map = map;
	$.each(cur_data.stations, function (i,stn) {
		markerOptions.position = new google.maps.LatLng(stn.lat, stn.lon);
		markerOptions.title = stn.name;
		if (stn.network === "newa" || (stn.state === "MA" && stn.network === "cu_log")) { 
			markerOptions.icon = newaIcon; 
			markerOptions.shadow = newaShadow;
		} else if (stn.network === "cu_log") { 
			markerOptions.icon = culogIcon; 
			markerOptions.shadow = culogShadow;
		} else if (stn.network === "icao") { 
			markerOptions.icon = airportIcon; 
			markerOptions.shadow = airportShadow;
		}
		marker = new google.maps.Marker(markerOptions);
		
		if (event_type === "station_page") {
			google.maps.event.addListener(marker, "click", function() {
				top.location.href="http://newa.cornell.edu/index.php?page=weather-station-page&WeatherStation="+stn.id;
			});
		} else if (event_type === "select_station") {
			google.maps.event.addListener(marker, "click", function() {
				setSelectValue(stn.id);
			});
		}
	});
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

function stationMap (list_type,event_type) {
	list_type = list_type || 'all';
	event_type = event_type || 'station_page';
	$.getJSON("/newaUtil/stationList/"+list_type)
		.success( function(results) { placeMarkers(results,event_type); } )
		.error( function() {
			$('<div id="msg" style="border:1px solid black; padding:0.25em; position:absolute; left:168px; bottom:0px; width:225px; z-index:1; font-size:0.9em; text-align:center; background-color:red; color:white;"></div>').appendTo($("#map"));
			$("#msg").text('Error retrieving station list'); 
		} 
	);
}

function zoomStation (reqstn) {
	$.getJSON("/newaUtil/stationInfo/"+reqstn)
		.success( zoomMarkCenter )  
		.error( function() { 
			return false;
		} 
	);
}
