var map;

function setSelectValue(oVal) {
	var oSel = document.stationLister.stn;
	for (var i = 0; i < oSel.options.length; i += 1) {
		if (oSel.options[i].value === oVal) {
			oSel.options[i].selected = true;
		}
	}
}

function centerMap (latlngCoords) {
	var center;
	latlngCoords.longitude = Math.max(latlngCoords.longitude,-78.0);
	latlngCoords.longitude = Math.min(latlngCoords.longitude,-71.5);
	latlngCoords.latitude = Math.max(latlngCoords.latitude,40.5);
	latlngCoords.latitude = Math.min(latlngCoords.latitude,44.0);
	center = new google.maps.LatLng(latlngCoords.latitude,latlngCoords.longitude);
	map.setCenter(center);
	$("#msg").empty().text('Click here to save location')
			 .click(function() {
				$("#msg").empty().hide(); 
				center = map.getCenter();
				$.cookie("mlocation", JSON.stringify({latitude:center.lat(), longitude:center.lng()}), {expires:180, path:"/", domain:"newa.nrcc.cornell.edu"});
			 } ); 
}

function loadLocation () {
	var defLocation = {latitude:42.95, longitude:-76.35},
		position = google.loader.ClientLocation;
	if (position) {
		centerMap(position);
	} else {
		centerMap(defLocation);
	}
}

function getLocation() {
	$('<div id="msg" style="border:1px solid black; padding:0.25em; position:absolute; left:168px; bottom:0px; width:225px; z-index:1; font-size:0.9em; text-align:center; background-color:red; color:white;"></div>').appendTo($("#map"));
	$("#msg").text('Trying to determine location...'); 
	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition( 
			function(position) {
				centerMap(position.coords);
			}, 
			loadLocation, 
			{timeout:5000} 
		);
	} else {
		loadLocation();
	}
}

function placeMarkers (cur_data, event_type) {
	var newaIcon = new google.maps.MarkerImage(
		'/gifs/newa_small.png',
		new google.maps.Size(16,16),
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
	var marker,
		markerOptions = {},
		mapOptions = {
			zoom: 7,
			center: new google.maps.LatLng(42.95, -76.35),
			mapTypeId: google.maps.MapTypeId.TERRAIN,
			mapTypeControl: true,
			mapTypeControlOptions: {
				style: google.maps.MapTypeControlStyle.DROPDOWN_MENU 
			},
			streetViewControl: false,
			scaleControl: true
		},
		myCookie = $.cookie("mlocation");
	if (myCookie) { 
		var mc = JSON.parse(myCookie);
		mapOptions.center = new google.maps.LatLng(mc.latitude,mc.longitude); 
	}
	map = new google.maps.Map(document.getElementById("map"), mapOptions);
	markerOptions.map = map;
	$.each(cur_data.stations, function (i,stn) {
		markerOptions.position = new google.maps.LatLng(stn.lat, stn.lon);
		markerOptions.title = stn.name;
		if (stn.network === "newa" || stn.network === "njwx" || (stn.network === "cu_log" && stn.state !== "NY")) { 
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
	if (!myCookie) { getLocation(); }
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
