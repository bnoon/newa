var stnmeta = null;
var mMgr = null;
var map = null;
var point = null;
 
function setMaxZoomCenter() {
  point = new GLatLng(stnmeta.lat, stnmeta.lon);
  map.getCurrentMapType().getMaxZoomAtLatLng(point, function(response) {
    if (response && response['status'] == G_GEO_SUCCESS) {
      map.setCenter(point, response['zoom']); }
    else {
      map.setCenter(point, 12); }
    setTimeout(addMarker,0);
  }, 14);
}

function addMarker () {
  var newaIcon = new GIcon();
  newaIcon.image = 'http://newa.nrcc.cornell.edu/gifs/newa_small.png';
  newaIcon.shadow = 'http://newa.nrcc.cornell.edu/gifs/newa_small_shdw.png';
  newaIcon.iconSize = new GSize(16,16);
  newaIcon.shadowSize = new GSize(24,16);
  newaIcon.iconAnchor = new GPoint(8,8);
  newaIcon.imageMap = [7,0,9,1,10,2,11,3,12,4,12,5,12,6,12,7,12,8,12,9,11,10,11,11,10,12,9,13,
					   8,14,2,14,2,13,1,12,1,11,1,10,1,9,1,8,2,7,2,6,3,5,3,4,4,3,6,2,5,1,5,0];
  var airportIcon = new GIcon();   
  airportIcon.image = 'http://newa.nrcc.cornell.edu/gifs/airport.png';
  airportIcon.shadow = 'http://newa.nrcc.cornell.edu/gifs/airport_shdw.png';
  airportIcon.iconSize = new GSize(15,15);
  airportIcon.shadowSize = new GSize(23,15);
  airportIcon.iconAnchor = new GPoint(8,8);
  airportIcon.imageMap = [8,0,8,1,8,2,8,3,8,4,8,5,10,6,12,7,13,8,14,9,14,10,8,11,9,12,9,13,9,14,5,
					  14,5,13,5,12,6,11,0,10,0,9,1,8,2,7,4,6,6,5,6,4,6,3,6,2,6,1,6,0];
  var culogIcon = new GIcon();
  culogIcon.image = 'http://newa.nrcc.cornell.edu/gifs/culog.png';
  culogIcon.shadow = 'http://newa.nrcc.cornell.edu/gifs/culog_shdw.png';
  culogIcon.iconSize = new GSize(14,14);
  culogIcon.shadowSize = new GSize(21,14);
  culogIcon.iconAnchor = new GPoint(7,7);
  culogIcon.imageMap = [9,0,11,1,12,2,12,3,13,4,13,5,13,6,13,7,13,8,13,9,12,10,11,11,10,12,9,13,
					4,13,2,12,2,11,1,10,0,9,0,8,0,7,0,6,0,5,0,4,1,3,1,2,3,1,4,0];
  var marker;
  mMgr = new MarkerManager(map);
  mMgr.clearMarkers();
  if (stnmeta.network == "cu_log")    { marker = new GMarker(point,culogIcon); }
  else if (stnmeta.network == "newa") { marker = new GMarker(point,newaIcon); }
  else if (stnmeta.network == "icao") { marker = new GMarker(point,airportIcon); }
  mMgr.addMarkers([marker], 5);
  mMgr.refresh();
}

function updateLatLon (reqstn) {
	$.getJSON("http://newa.nrcc.cornell.edu/newaUtil/stationInfo/"+reqstn, function(result){
	 if (result.error) {
		return false; }
	  else {
		stnmeta = result.metadata;
		setTimeout(setMaxZoomCenter,0); }
	});
}

function set_up (reqstn) {
 if (GBrowserIsCompatible()) {
	map = new GMap2(document.getElementById("map"));
	map.setMapType(G_SATELLITE_MAP);
//	map.addControl (new GSmallMapControl());
	map.setUIToDefault();
	updateLatLon(reqstn);
  }
}
