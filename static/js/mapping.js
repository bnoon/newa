		var cur_data = null;
		var mMgr = null;

		function set_up () {
          if (GBrowserIsCompatible()) {
            var map = new GMap2(document.getElementById("map"));
            map.setMapType(G_PHYSICAL_MAP);
            map.addMapType(G_PHYSICAL_MAP)
			map.addControl(new GLargeMapControl());
			map.addControl (new GHierarchicalMapTypeControl());
			map.setCenter(new GLatLng(42.9, -75.85), 7);
            mMgr = new MarkerManager(map);
            $('<div id="msg" style="border:1px solid black; padding:0.25em; position:absolute; left:200px; bottom:0px; width:225px; z-index:1; font-size:0.7em; text-align:center; background-color:white; color:black;"></div>').appendTo($("#map"));
          }
		}
        
		function updateLatLon (list_type) {
			$.getJSON("/newaUtil/stationList/"+list_type, function(result){
			 if (result.error) {
				$("#msg").show().text(result.error); }
			  else {
				$("#msg").show().text('Obtained '+result.stations.length+' stations');
				cur_data = result;
				setTimeout(updateStations,0); }
			});
		}

		function updateStations () {
		  var newaIcon = new GIcon();
		  newaIcon.image = '../gifs/newa_small.png';
		  newaIcon.shadow = '../gifs/newa_small_shdw.png';
		  newaIcon.iconSize = new GSize(16,16);
		  newaIcon.shadowSize = new GSize(24,16);
		  newaIcon.iconAnchor = new GPoint(8,8);
		  newaIcon.imageMap = [7,0,9,1,10,2,11,3,12,4,12,5,12,6,12,7,12,8,12,9,11,10,11,11,10,12,9,13,
							   8,14,2,14,2,13,1,12,1,11,1,10,1,9,1,8,2,7,2,6,3,5,3,4,4,3,6,2,5,1,5,0];
  	   	  var airportIcon = new GIcon();   
   		  airportIcon.image = '../gifs/airport.png';
		  airportIcon.shadow = '../gifs/airport_shdw.png';
		  airportIcon.iconSize = new GSize(15,15);
		  airportIcon.shadowSize = new GSize(23,15);
		  airportIcon.iconAnchor = new GPoint(8,8);
		  airportIcon.imageMap = [8,0,8,1,8,2,8,3,8,4,8,5,10,6,12,7,13,8,14,9,14,10,8,11,9,12,9,13,9,14,5,
		  				      14,5,13,5,12,6,11,0,10,0,9,1,8,2,7,4,6,6,5,6,4,6,3,6,2,6,1,6,0];
		  var culogIcon = new GIcon();
		  culogIcon.image = '../gifs/culog.png';
		  culogIcon.shadow = '../gifs/culog_shdw.png';
		  culogIcon.iconSize = new GSize(14,14);
		  culogIcon.shadowSize = new GSize(21,14);
		  culogIcon.iconAnchor = new GPoint(7,7);
		  culogIcon.imageMap = [9,0,11,1,12,2,12,3,13,4,13,5,13,6,13,7,13,8,13,9,12,10,11,11,10,12,9,13,
		  					4,13,2,12,2,11,1,10,0,9,0,8,0,7,0,6,0,5,0,4,1,3,1,2,3,1,4,0];

		  if (cur_data == null) return;
		  mMgr.clearMarkers();
		  var markers = [];
		  var point, distance, marker;
		  $.each(cur_data.stations, function (i,stn) {
			  point = new GLatLng(stn.lat, stn.lon);
			  if (stn.network == "newa" || (stn.state == "MA" && stn.network == "cu_log")) { marker = new GMarker(point,newaIcon); }
	 		  else if (stn.network == "cu_log")    { marker = new GMarker(point,culogIcon); }
			  else                                 { marker = new GMarker(point,airportIcon); }
			  markers.push(marker);
			  GEvent.addListener(marker,'click', function () {
				$("#msg").show().text("Selected station: "+stn.name);
				setSelectValue(stn.id);
			  });
			  GEvent.addListener(marker, "mouseover", function() {
				$("#msg").show().text(stn.name);
			  });
			  GEvent.addListener(marker, "mouseout", function() {
				$("#msg").empty().hide();
			  });
		  });
		  mMgr.addMarkers(markers, 6);
		  mMgr.refresh();
		}
