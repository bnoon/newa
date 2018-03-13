import urllib, urllib2, json
from mx import DateTime

miss = -999

# get hourly data for date range
def get_HourlyData(stn, id_type, data_start, data_end):
	temp_major = {'newa':'23', 'icao':'23','njwx':'23', 'cu_log':'126', 'miwx':'126', 'oardc':'23', 'nysm':'23'}
	if not temp_major.has_key(id_type): return None
	try:
		# build input dict		
		sid = " ".join([stn, id_type])
		sdate = "%d-%d-%d" % (data_start.year,data_start.month,data_start.day)
		edate = "%d-%d-%d" % (data_end.year,data_end.month,data_end.day)
		input_dict = {"sid":sid,"sdate":sdate,"edate":edate,"elems":temp_major[id_type],"meta":""}
		# get data
		params = urllib.urlencode({'params':json.dumps(input_dict)})
		req = urllib2.Request('http://data.nrcc.rcc-acis.org/StnData', params, {'Accept':'application/json'})
		response = urllib2.urlopen(req)
		results = json.loads(response.read())
		# check for error returned from web services
		if results.has_key("error"):
#			print "Error returned from web service call:",results["error"]
			return None
		return results
	except Exception, e:
		print "Problem with station data call ... ",e
		return None

#--------------------------------------------------------------------------------------------	
def get_downloadtime (stn,station_type):
	download_time_dt = miss
	try:
		if station_type == 'icao': 
			staid = stn.upper()
		else:
			if stn[0:3] == "ew_":
				stn = stn[3:]
		end_date_dt = DateTime.now()
#		adjust for DST if necessary (don't worry about this for start_date)
		if end_date_dt.dst == 1: end_date_dt = end_date_dt + DateTime.RelativeDate(hours=-1)
		start_date_dt = end_date_dt + DateTime.RelativeDate(months=-12, hour=0, minute=0, second=0)
#	 	make first chunk just 2 days, 30 days in successive calls as far back as a year
		start_period_dt = end_date_dt + DateTime.RelativeDate(days=-2)
		end_period_dt = end_date_dt
		while end_period_dt >= start_date_dt:
			results = get_HourlyData(stn, station_type, start_period_dt, end_period_dt)
#	 		process data 
			if results and len(results["data"]) > 0:
				temp = results["data"]
				for i in range(len(temp)-1,-1,-1):	# loop back through days
					hlydate, hlytemps = temp[i]
					for h in range(len(hlytemps)-1,-1,-1):	# loop back through hours (h 23 to 0 is hours 24 to 1)
						if hlytemps[h] != "M":
							hyr, hmn, hdy = hlydate.split("-")
							# add one to hour to go from index (23:0) to actual (24:1)
							theDate = DateTime.DateTime(int(hyr),int(hmn),int(hdy),h) + DateTime.RelativeDate(hours=+1)
							download_time_dt = theDate + DateTime.RelativeDate(hours=+theDate.dst)
							return download_time_dt
#			reset for previous 30-day chunk
			start_period_dt = start_period_dt + DateTime.RelativeDate(days=-30)
			end_period_dt = start_period_dt + DateTime.RelativeDate(days=+30)
	except Exception, e:
		print e
	return download_time_dt

#Tests
#for id,type in [('KALB','icao'),('gen','newa'),('cu_gfr','cu_log'),('ew_ith','miwx'),('pav','newa'),('xxx','newa'),('zzz','bogus')]:
#	result = get_downloadtime(id,type)
#	print 'Result for ',id,type,result