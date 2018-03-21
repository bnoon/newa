function saveAppleinfo(stn, year, event, event_value) {
	var appleinfo, appleinfojson,
		storageKey = "appleinfo";
	if (localStorage) {
		appleinfojson = localStorage.getItem(storageKey);
		if (appleinfojson) {
			appleinfo = JSON.parse(appleinfojson);
		} else {
			appleinfo = {};
		}
		if (!appleinfo.hasOwnProperty(stn)) {
			appleinfo[stn] = {};
		}
		if (!appleinfo[stn].hasOwnProperty(year)) {
			appleinfo[stn][year] = {};
		}
		appleinfo[stn][year][event] = event_value;
		localStorage.setItem(storageKey, JSON.stringify(appleinfo));
	}
}

function getAppleinfo(stn, year, event) {
	var appleinfojson, event_value = null,
		storageKey = "appleinfo";;
	if (localStorage) {
		appleinfojson = localStorage.getItem(storageKey);
		if (appleinfojson) {
			appleinfo = JSON.parse(appleinfojson);
			if (appleinfo.hasOwnProperty(stn) && appleinfo[stn].hasOwnProperty(year) && appleinfo[stn][year].hasOwnProperty(event)) {
				event_value = appleinfo[stn][year][event];
			}
		}
	}
	return event_value;
}