#!/usr/local/bin/python

import sys, copy
from print_exception import print_exception
import newaUtil_io
from newaCommon import newaCommon_io

try :
    import json
except ImportError :
    import simplejson as json
    
class program_exit (Exception):
	pass
class gridSoilTempsException(Exception):
		pass

			
def NameAny_to_dict(na) :
	ret = {}
	for a in na:
		ret[a.name] = a.value.value()
	return ret

def getForecastUrl(stn):
	forecastUrl = ""
	try:
		from newaCommon.stn_info import stn_info
		if not stn_info.has_key(stn):
			from newaCommon.stn_info_ma import stn_info
		lat = stn_info[stn]['lat']
		lon = stn_info[stn]['lon']
		forecastUrl = 'http://forecast.weather.gov/MapClick.php?textField1=%s&textField2=%s' % (lat,lon)
		return forecastUrl
	except:
		return newaCommon_io.errmsg('Error processing request')
	return forecastUrl

# obtain stations in state that report any variable in a list
def get_stations_with_var (state,varMajors=None,start=None,end=None) :
	import Meta
	from omniORB import CORBA
	import ucanCallMethods
	any = CORBA.Any
	tc = CORBA.TypeCode
	tc_short = CORBA.TC_short
	tc_long = CORBA.TC_long
	tc_string = CORBA.TC_string
	tc_nativeId = CORBA.TypeCode(Meta.MetaQuery.NativeId)
	tc_shortSeq = tc(Meta.ShortSeq)
	tc_floatSeq = tc(Meta.FloatSeq)
	NativeId = Meta.MetaQuery.NativeId
	NameAny = Meta.MetaQuery.NameAnyPair
	# set up ucan
	ucan = ucanCallMethods.general_ucan()

	dictionary = {}
	try:
		postal = state.upper()
		if varMajors == None:
			varMajors = [1,2,4]
		if start == None:
			start = (0001,1,1)
		if end == None :
			end = (9999,12,31)
		query = ucan.get_query()
		qualifier =      [ NameAny ('postal',      any(tc_string,postal) )]
		qualifier.append ( NameAny ('var_major_id',any(tc_shortSeq,varMajors) ) )
		qualifier.append ( NameAny ('begin_date',  any(tc_shortSeq,start) )  ) 
		qualifier.append ( NameAny ('end_date',    any(tc_shortSeq,end) )  ) 
		results = query.getStnInfoAsSeq(qualifier,())
		query.release()
		if len(results) == 0:
			return {}
		else:
			dictionary = {}
			for item in results :
				r = NameAny_to_dict(item)
				dictionary[r['ucan_id']] = r
	except:
		print_exception()
	return dictionary 

# return list of tuples containing stations that report all variables needed for given disease
def run_diseaseStations (disease):
	from newaUtil.disease_vars_dict import disease_vars
	# var majors for disease variables
	majors = {'temp': [23,126], 'prcp': [5], 'lwet': [118], 'rhum': [24], 'wspd': [28,128], 'srad': [119,132] }
	# variables recorded at all airports
	airport_vars = ['prcp','temp','rhum','wspd','wdir']
	# airports in and around NY
	airports = [("kalb", "Albany Airport"), ("kbgm", "Binghamton Airport"), ("kbfd", "Bradford, PA Airport"),
			    ("khwv", "Brookhaven Airport"), ("kbuf", "Buffalo Airport"), ("kbtv", "Burlington, VT Airport"),
			    ("kdsv", "Dansville Airport"), ("kdkk", "Dunkirk Airport"), ("kelm", "Elmira Airport"),
			    ("keri", "Erie, PA Airport"), ("kfrg", "Farmingdale Airport"), ("kfzy", "Fulton Airport"),
			    ("kgfl", "Glens Falls Airport"), ("krme", "Griffiss Airport"), ("kisp", "Islip Airport"), 
			    ("kith", "Ithaca Airport"), ("kjhw", "Jamestown Airport"), ("kmss", "Massena Airport"), 
			    ("kmgj", "Montgomery Airport"), ("kmtp", "Montauk Airport"), ("kmsv", "Monticello Airport"), 
			    ("knyc", "New York - Central Park"), ("kjfk", "New York - JFK Airport"), ("klga", "New York - LGA Airport"), 
			    ("kiag", "Niagara Falls Airport"), ("kpeo", "Penn Yan Airport"), ("kpou", "Poughkeepsie Airport"), 
			    ("kroc", "Rochester Airport"), ("kslk", "Saranac Lake Airport"), ("kswf", "Newburgh Stewart Field"), 
			    ("ksyr", "Syracuse Airport"), ("kfok", "Westhampton Beach Airport"), ("kart", "Watertown Airport"), 
			    ("kgtb", "Wheeler Sack Field"), ("khpn", "White Plains Airport"), ("kelz", "Wellsville Airport"),
			    ("krut", "Rutland, VT Airport"), ("kddh", "Bennington, VT Airport"), ("kaqw", "North Adams, MA Airport"),
			    ("kpsf", "Pittsfield, MA Airport"), ("kdxr", "Danbury, CT Airport"), ("kbdr", "Bridgeport, CT Airport"),
			    ("kfwn", "Sussex, NJ Airport"), ("kcdw", "Fairfield, NJ Airport"), ("kteb", "Teterboro, NJ Airport"),
				("kmpv", "Montpelier, VT Airport"),  ("kmvl", "Morrisville, VT Airport"),  ("kvsf", "Springfield, VT Airport"),  
				("k12n", "Andover, NJ Airport"),  ("kacy", "Atlantic City, NJ Airport"), ("kblm", "Farmingdale, NJ Airport"),  
				("kmiv", "Millville, NJ Airport"),  ("kmmu", "Morristown, NJ Airport"),  ("knel", "Lakehurst NAS, NJ"),  
				("ksmq", "Somerville, NJ Airport"),  ("kttn", "Trenton, NJ Airport"),  ("kvay", "Mount Holly, NJ Airport"),  
				("kwri", "McGuire AFB, NJ Airport"),  ("kwwd", "Wildwood, NJ Airport"),  ("kphl", "Philadelphia, PA Airport"),  
				("kpne", "NE Philadelphia, PA Airport"),  ("kpit", "Pittsburgh, PA Airport"),  ("kmdt", "Middletown Harrisburg, PA Airport"),  
				("kipt", "Williamsport, PA Airport"),  ("kavp", "Wilkes-Barre, PA Airport"),  ("kabe", "Allentown, PA Airport"),  
				("kaoo", "Altoona, PA Airport"),  ("krdg", "Reading, PA Airport"),  ("kjst", "Johnstown, PA Airport"),  
				("kduj", "DuBois, PA Airport"),  ("kilg", "Wilmington, DE Airport"),  ("korh", "Worcester, MA Airport"),  
				("kore", "Orange, MA Airport"),  ("kpym", "Plymouth, MA Airport"),  ("kbvy", "Beverly, MA Airport"),  
				("khya", "Hyannis, MA Airport"),  ("kbos", "Boston Logan, MA Airport"),  ("kack", "Nantucket, MA Airport"),  
				("kcef", "Chicopee Falls, MA Airport"),  ("klwm", "Lawrence, MA Airport"),  ("kbaf", "Westfield, MA Airport"),  
				("kmqe", "E Milton Blue Hill, MA"),  ("kbed", "Bedford, MA Airport"),  ("kpvc", "Provincetown, MA Airport"),  
				("ktan", "Taunton, MA Airport"),  ("kowd", "Norwood, MA Airport"),  ("kfmh", "Falmouth Otis AFB, MA"),  
				("kfit", "Fitchburg, MA Airport"),  ("kmvy", "Vineyard Haven, MA Airport"),  ("kewb", "New Bedford, MA Airport"),  
				("kcqx", "Chatham, MA Airport"),  ("kuuu", "Newport, RI Airport"),  ("kpvd", "Providence, RI Airport"),  
				("kbdl", "Hartford (Bradley AP), CT"),  ("kstl", "St. Louis, MO Airport"), ("kgpz", "Grand Rapids, MN Airport"),
  			    ("kewr", "Newark, NJ Airport"), ("kovs", "Boscobel, WI Airport"), ("kcid", "Cedar Rapids, IA Airport"), 
			    ("kiow", "Iowa City, IA Airport"), ("koma", "Omaha, NE Airport"), ("klnk", "Lincoln, NE Airport"),
			    ("kcon", "Concord, NH Airport"), ("kash", "Nashua, NH Airport"), ("kmht", "Manchester, NH Airport"),
			    ("kdlh", "Diluth, MN Airport"), ("kmsp", "Minneapolis, MN Airport"), ("krst", "Rochester, MN Airport"),
			    ("kstc", "St Cloud, MN Airport"), ("kdca", "Washington, DC Airport"), ("kged", "Georgetown, DE Airport"),
			    ("kbwi", "Baltimore, MD Airport"), ("ksby", "Salisbury, MD Airport"), ("kavl", "Asheville, NC Airport"),
			    ("kclt", "Charlotte, NC Airport"), ("kfsd", "Sioux Falls, SD Airport"), ("klse", "La Crosse, WI Airport"),
			    ("krfd", "Rockford, IL Airport"), ("karr", "Aurora, IL Airport")]
	# network codes
	station_type = {57: 'newa', 58: 'cu_log', 7: 'icao', 28: 'njwx'}

	good_stations = []
	try:
		# check for valid disease
		if disease_vars.has_key(disease): 
			# build list of desired variables
			vmaj = []
			for v in disease_vars[disease]: vmaj = vmaj + majors[v]
			
			# obtain stations that report any of these variables
			results_dict = get_stations_with_var ('NY',vmaj,(2008,1,1),(9999,12,31))
			
			# remove stations that don't report a variable
			for k in results_dict.keys():
				for v in disease_vars[disease]:
					for m in majors[v]:
						if m in results_dict[k]['var_major_id']: break
					else:
						##del results_dict[k]
						break		#don't use station
				else:
					rdk = results_dict[k]
					for i in range(len(rdk['ids'])):
						net = rdk['ids'][i].network
						id =  rdk['ids'][i].id
						if station_type.has_key(net):
							stanet = station_type[net]
							staid = id
							break
					else:
						stanet = ''
						staid = id
					good_stations.append(staid)
			
			# add airports if they have necessary variables
			for v in disease_vars[disease]:
				if v not in airport_vars: break		#can't use airports
			else:
				for ap in airports:
					good_stations.append(ap[0])
				
		station_dict = {"stations": good_stations}
		json_return = json.dumps(station_dict)
	except:
		print_exception()
	return json_return

# convert order of list (l) from column to row major order for a matrix with specified number of columns (cols)
def row_major_list (l,cols):
	import math
	newl = []
	n = len(l)
	rows = int(math.ceil(n/float(cols)))
	remain = int(n%float(cols))
	if remain == 0:
		nrows = rows
	else:
		nrows = rows - 1
	for i in range(1,rows+1):
		if i == rows and remain > 0:
			ncols = remain
		else:
			ncols = cols
		for j in range(0,ncols):
			ind = i+j*nrows+(min(remain,j))
			if ind <= n: newl.append(l[ind-1])
	return newl

# get a list of models that can be run for this station	
def run_stationModels(stn):
	station_dict = {}
	model_list = []
	try:
		from newaCommon.stn_info import stn_info
		from pest_models import pest_models
		stn = stn.lower()
		if stn_info.has_key(stn):
			stn_vars = copy.deepcopy(stn_info[stn]['vars'])
			if 'lwet' in stn_info[stn]['vars'] or 'rhum' in stn_info[stn]['vars']:
				stn_vars.append('eslw')
			for mdl in pest_models:
				mtitle,murl,mvars = mdl
				for model_var in mvars:
					if not model_var in stn_vars: break
				else:
					if murl != "newaDisease/onion_dis":
						whole_url = "http://newa.nrcc.cornell.edu/"+murl+"/"+stn
					else:
						whole_url = "http://newa.nrcc.cornell.edu/"+murl
					model_list.append([mtitle,whole_url])
	except:
		print 'Error processing request for',stn
		print_exception()
#	station_dict['models'] = model_list
	sorted_model_list = row_major_list(model_list,3)
	station_dict['models'] = sorted_model_list
	json_return = json.dumps(station_dict)
	return json_return
	
# get stations that report element specified in list_options and return list in alpha order by station name
def run_stationList(list_options='all'):
	try:
		from newaCommon.stn_info import stn_info
		station_dict = {}
		station_dict['stations'] = []
		unsortedDict = {}
		for stn in stn_info.keys():
			if (list_options == 'lwrh' and 'lwet' in stn_info[stn]['vars'] and 'rhum' in stn_info[stn]['vars']) \
				or (list_options == 'eslw' and ('lwet' in stn_info[stn]['vars'] or 'rhum' in stn_info[stn]['vars'])) \
				or list_options == 'all' or list_options in stn_info[stn]['vars']\
				or (list_options == 'goodsr' and stn_info[stn].has_key('srqual') and stn_info[stn]['srqual'] == 'ok')\
				or (list_options == 'srad' and stn_info[stn]['network'] == 'icao'):
				sdict = {}
				sdict['id'] = stn
				for item in ['lat','lon','elev','name','network','state']:
					sdict[item] = stn_info[stn][item]
				unsortedDict[stn_info[stn]['name']] = sdict
		
		unsortedKeys = unsortedDict.keys()
		unsortedKeys.sort()
		for state in ['NY','VT','MA','NH','CT','RI','NJ','PA','DE','MD','ME','DC','WI','IA','NE','MN','NC','IL','SD','MO','VA','SC','WV','AL']:
			for usk in unsortedKeys:
				if state == unsortedDict[usk]['state']:
					station_dict['stations'].append(unsortedDict[usk])
					json_return = json.dumps(station_dict)
		return json_return
	except:
		return newaCommon_io.errmsg('Error processing request')

# FOR A GIVEN STATION and NETWORK, return sister station info
def run_stationSisterInfo(options):
	from newaCommon.sister_info import sister_info
	try:
		stn = options['station']
		network = options['network']
		sister_dict = {}
		if network == 'miwx' and stn[0:3] != 'ew_':
			stn = "ew_%s" % stn
		if sister_info.has_key(stn):
			sister = sister_info[stn]
			for var in sister.keys():
				if sister[var][0:1] >= '1' and sister[var][0:1] <= '9' and sister[var][1:2] >= '0' and sister[var][1:2] <= '9':
					station_id = sister[var]
					station_type = 'njwx'
				elif len(sister[var]) == 4:
					station_id = sister[var]
					station_type = "icao"
				elif sister[var][0:3] == "cu_" or sister[var][0:3] == "um_" or sister[var][0:3] == "uc_" or sister[var][0:3] == "un_":
					station_id = sister[var]
					station_type = "culog"
				elif sister[var][0:3] == "ew_":
					station_id = sister[var][3:]
					station_type = 'miwx'
				else:
					station_id = sister[var]
					station_type = "newa"
				sister_dict[var] = "%s %s" % (station_id, station_type)
		json_return = json.dumps(sister_dict)
		return json_return
	except:
		return newaCommon_io.errmsg('Error processing request')

# FOR A GIVEN STATE, get stations that report element specified in list_options and return list in alpha order by station name
def run_stateStationList(options):
	try:
		reqvar = options['reqvar']
		state = options['state']
		if state == '':
			state = 'ALL'
		station_dict = {}
		station_dict['stations'] = []
		unsortedDict = {}
		try:
			exec("from newaCommon.stn_info_" + state.lower() + " import stn_info")
		except:
			pass
		for stn in stn_info.keys():
			if (reqvar == 'lwrh' and 'lwet' in stn_info[stn]['vars'] and 'rhum' in stn_info[stn]['vars']) \
				or (reqvar == 'eslw' and ('lwet' in stn_info[stn]['vars'] or 'rhum' in stn_info[stn]['vars'])) \
				or reqvar == 'all' or reqvar in stn_info[stn]['vars']\
				or (reqvar == 'goodsr' and stn_info[stn].has_key('srqual') and stn_info[stn]['srqual'] == 'ok')\
				or (reqvar == 'srad' and stn_info[stn]['network'] == 'icao'):
				sdict = {}
				sdict['id'] = stn
				for item in ['lat','lon','elev','name','network','state']:
					sdict[item] = stn_info[stn][item]
				uskey = "%s_%s" % (stn_info[stn]['name'], stn_info[stn]['state'])
				unsortedDict[uskey] = sdict
		
		sortedKeys = unsortedDict.keys()
		sortedKeys.sort()
		#return alphabetized list
		for usk in sortedKeys:
			station_dict['stations'].append(unsortedDict[usk])
		json_return = json.dumps(station_dict)
		return json_return
	except:
		return newaCommon_io.errmsg('Error processing request')

# FOR A GIVEN STATE, get INACTIVE stations that report element specified in list_options and return list in alpha order by station name
def run_stateInactiveStationList(options):
	try:
		reqvar = options['reqvar']
		state = options['state']
		if state == '':
			state = 'ALL'
		station_dict = {}
		station_dict['stations'] = []
		unsortedDict = {}
		try:
			# only line that's different from stateStationList
			exec("from newaCommon.stn_info_" + state.lower() + "_inactive import stn_info")
		except:
			pass
		for stn in stn_info.keys():
			if (reqvar == 'lwrh' and 'lwet' in stn_info[stn]['vars'] and 'rhum' in stn_info[stn]['vars']) \
				or (reqvar == 'eslw' and ('lwet' in stn_info[stn]['vars'] or 'rhum' in stn_info[stn]['vars'])) \
				or reqvar == 'all' or reqvar in stn_info[stn]['vars']\
				or (reqvar == 'goodsr' and stn_info[stn].has_key('srqual') and stn_info[stn]['srqual'] == 'ok')\
				or (reqvar == 'srad' and stn_info[stn]['network'] == 'icao'):
				sdict = {}
				sdict['id'] = stn
				for item in ['lat','lon','elev','name','network','state']:
					sdict[item] = stn_info[stn][item]
				unsortedDict[stn_info[stn]['name']] = sdict
		
		sortedKeys = unsortedDict.keys()
		sortedKeys.sort()
		#return alphabetized list
		for usk in sortedKeys:
			station_dict['stations'].append(unsortedDict[usk])
		json_return = json.dumps(station_dict)
		return json_return
	except:
		return newaCommon_io.errmsg('Error processing request')

# get basic info for a given station
def run_stationInfo(stn):
	from get_downloadtime import get_downloadtime
	station_dict = {}
	try:
		from newaCommon.stn_info import stn_info
		stn = stn.lower()
		sdict = {}
		if stn_info.has_key(stn):
			sdict['id'] = stn
			for item in ['lat','lon','elev','name','network','vars']:
				if stn_info[stn].has_key(item):
					sdict[item] = stn_info[stn][item]

			dt = get_downloadtime(stn,sdict['network'])
			if dt == -999:
				sdict['lasthour'] = "Unknown"
			else:
				if dt.hour < 12:
					hr_str = str(dt.hour)+" AM"
				elif dt.hour == 12:
					hr_str = "12 PM"
				else:
					hr_str = str(dt.hour-12)+" PM"
				sdict['lasthour'] = "%d/%d/%d %s" % (dt.month,dt.day,dt.year,hr_str)

		station_dict['metadata'] = sdict		
	except:
		print 'Error processing request for',stn
		print_exception()
		station_dict['metadata'] = {}
	json_return = json.dumps(station_dict)
	return json_return
			
# FOR A GIVEN STATION, NETWORK, VARIABLE, START AND END DATE - return NDFD 
#  convert from data in db stored as a day consisting of hours 0-23 and time in ET
#  to a day with hours 1-24 and time in EST
def run_getFcstData(options):
	from mx import DateTime
	from bsddb import hashopen
	from cPickle import loads
	miss = -999
	try:
		requested_var = options['variable']
		yyyymmdd = options['startdate'].split("-")
		start_date_dt = DateTime.DateTime(int(yyyymmdd[0]), int(yyyymmdd[1]), int(yyyymmdd[2]), 0, 0, 0)
		yyyymmdd = options['enddate'].split("-")
		end_date_dt = DateTime.DateTime(int(yyyymmdd[0]), int(yyyymmdd[1]), int(yyyymmdd[2]), 0, 0, 0)
		stn = options['station'].upper()
		network = options['network']
		if network == 'miwx' and stn[0:3] != 'EW_':
			stn = "EW_%s" % stn
		hourly_fcst = []
		try:
			forecast_db = hashopen('/ndfd/hourly_forecasts.db','r')
			stn_dict = loads(forecast_db[stn])
			forecast_db.close()
			if stn_dict.has_key(requested_var):
				# put values into dictionary keyed on time in EST; hour 00 changed to hour 24 previous day
				sd = {}
				theDate = start_date_dt
				stopDate = end_date_dt + DateTime.RelativeDate(days=+1)
				while theDate <= stopDate:
					dkey = (theDate.year, theDate.month, theDate.day)
					for h in range(0, 24):
						if stn_dict[requested_var].has_key(dkey):
							hval = stn_dict[requested_var][dkey][h]
						else:
							hval = miss
						est = theDate + DateTime.RelativeDate(hour=h)
						if est.dst == 1:
							est = est + DateTime.RelativeDate(hours=-1)
						if est.hour == 0:
							yest = theDate + DateTime.RelativeDate(days=-1)
							key_est = (yest.year,yest.month,yest.day,24)
						else:
							key_est = (est.year,est.month,est.day,est.hour)		
						if hval == -999:
							sd[key_est] = 'M'
						elif requested_var == 'tsky':
							sd[key_est] = round(hval*10, 0)
						elif requested_var != 'pop12':
							sd[key_est] = hval
						else:
							sd[key_est] = int(hval)	#need this to prevent serialization error for pop12
					theDate = theDate + DateTime.RelativeDate(days=+1)
				# put values into daily arrays (hours 1-24)	
				theDate = start_date_dt
				while theDate <= end_date_dt:
					ymd = "%s-%02d-%02d" % (theDate.year,theDate.month,theDate.day)
					hourly_vals = []
					for h in range(1, 25):
						hkey = (theDate.year,theDate.month,theDate.day,h)
						if sd.has_key(hkey):
							hourly_vals.append(sd[hkey])
						else:
							hourly_vals.append("M")
					hourly_fcst.append([ymd,hourly_vals])
					theDate = theDate + DateTime.RelativeDate(days=+1)
		except:
			print_exception()
		return json.dumps({"data": hourly_fcst})
	except:
		print_exception()
		return json.dumps({"error": "Error in getFcstData"})

# used by run_gridSoilTemps to find Northeast standard gridpoint nearest given lat/lon
def findNearestGrid(srch_ll):
	import copy
	ll_dict = {
		"lat": [37.166667, 37.208333, 37.25, 37.291667, 37.333333, 37.375, 37.416667, 37.458333, 37.5, 37.541667, 37.583333, 37.625, 37.666667, 37.708333, 37.75, 37.791667, 37.833333, 37.875, 37.916667, 37.958333, 38, 38.041667, 38.083333, 38.125, 38.166667, 38.208333, 38.25, 38.291667, 38.333333, 38.375, 38.416667, 38.458333, 38.5, 38.541667, 38.583333, 38.625, 38.666667, 38.708333, 38.75, 38.791667, 38.833333, 38.875, 38.916667, 38.958333, 39, 39.041667, 39.083333, 39.125, 39.166667, 39.208333, 39.25, 39.291667, 39.333333, 39.375, 39.416667, 39.458333, 39.5, 39.541667, 39.583333, 39.625, 39.666667, 39.708333, 39.75, 39.791667, 39.833333, 39.875, 39.916667, 39.958333, 40, 40.041667, 40.083333, 40.125, 40.166667, 40.208333, 40.25, 40.291667, 40.333333, 40.375, 40.416667, 40.458333, 40.5, 40.541667, 40.583333, 40.625, 40.666667, 40.708333, 40.75, 40.791667, 40.833333, 40.875, 40.916667, 40.958333, 41, 41.041667, 41.083333, 41.125, 41.166667, 41.208333, 41.25, 41.291667, 41.333333, 41.375, 41.416667, 41.458333, 41.5, 41.541667, 41.583333, 41.625, 41.666667, 41.708333, 41.75, 41.791667, 41.833333, 41.875, 41.916667, 41.958333, 42, 42.041667, 42.083333, 42.125, 42.166667, 42.208333, 42.25, 42.291667, 42.333333, 42.375, 42.416667, 42.458333, 42.5, 42.541667, 42.583333, 42.625, 42.666667, 42.708333, 42.75, 42.791667, 42.833333, 42.875, 42.916667, 42.958333, 43, 43.041667, 43.083333, 43.125, 43.166667, 43.208333, 43.25, 43.291667, 43.333333, 43.375, 43.416667, 43.458333, 43.5, 43.541667, 43.583333, 43.625, 43.666667, 43.708333, 43.75, 43.791667, 43.833333, 43.875, 43.916667, 43.958333, 44, 44.041667, 44.083333, 44.125, 44.166667, 44.208333, 44.25, 44.291667, 44.333333, 44.375, 44.416667, 44.458333, 44.5, 44.541667, 44.583333, 44.625, 44.666667, 44.708333, 44.75, 44.791667, 44.833333, 44.875, 44.916667, 44.958333, 45, 45.041667, 45.083333, 45.125, 45.166667, 45.208333, 45.25, 45.291667, 45.333333, 45.375, 45.416667, 45.458333, 45.5, 45.541667, 45.583333, 45.625, 45.666667, 45.708333, 45.75, 45.791667, 45.833333, 45.875, 45.916667, 45.958333, 46, 46.041667, 46.083333, 46.125, 46.166667, 46.208333, 46.25, 46.291667, 46.333333, 46.375, 46.416667, 46.458333, 46.5, 46.541667, 46.583333, 46.625, 46.666667, 46.708333, 46.75, 46.791667, 46.833333, 46.875, 46.916667, 46.958333, 47, 47.041667, 47.083333, 47.125, 47.166667, 47.208333, 47.25, 47.291667, 47.333333, 47.375, 47.416667, 47.458333, 47.5, 47.541667, 47.583333, 47.625],
		"lon": [-82.708333, -82.666667, -82.625, -82.583333, -82.541667, -82.5, -82.458333, -82.416667, -82.375, -82.333333, -82.291667, -82.25, -82.208333, -82.166667, -82.125, -82.083333, -82.041667, -82, -81.958333, -81.916667, -81.875, -81.833333, -81.791667, -81.75, -81.708333, -81.666667, -81.625, -81.583333, -81.541667, -81.5, -81.458333, -81.416667, -81.375, -81.333333, -81.291667, -81.25, -81.208333, -81.166667, -81.125, -81.083333, -81.041667, -81, -80.958333, -80.916667, -80.875, -80.833333, -80.791667, -80.75, -80.708333, -80.666667, -80.625, -80.583333, -80.541667, -80.5, -80.458333, -80.416667, -80.375, -80.333333, -80.291667, -80.25, -80.208333, -80.166667, -80.125, -80.083333, -80.041667, -80, -79.958333, -79.916667, -79.875, -79.833333, -79.791667, -79.75, -79.708333, -79.666667, -79.625, -79.583333, -79.541667, -79.5, -79.458333, -79.416667, -79.375, -79.333333, -79.291667, -79.25, -79.208333, -79.166667, -79.125, -79.083333, -79.041667, -79, -78.958333, -78.916667, -78.875, -78.833333, -78.791667, -78.75, -78.708333, -78.666667, -78.625, -78.583333, -78.541667, -78.5, -78.458333, -78.416667, -78.375, -78.333333, -78.291667, -78.25, -78.208333, -78.166667, -78.125, -78.083333, -78.041667, -78, -77.958333, -77.916667, -77.875, -77.833333, -77.791667, -77.75, -77.708333, -77.666667, -77.625, -77.583333, -77.541667, -77.5, -77.458333, -77.416667, -77.375, -77.333333, -77.291667, -77.25, -77.208333, -77.166667, -77.125, -77.083333, -77.041667, -77, -76.958333, -76.916667, -76.875, -76.833333, -76.791667, -76.75, -76.708333, -76.666667, -76.625, -76.583333, -76.541667, -76.5, -76.458333, -76.416667, -76.375, -76.333333, -76.291667, -76.25, -76.208333, -76.166667, -76.125, -76.083333, -76.041667, -76, -75.958333, -75.916667, -75.875, -75.833333, -75.791667, -75.75, -75.708333, -75.666667, -75.625, -75.583333, -75.541667, -75.5, -75.458333, -75.416667, -75.375, -75.333333, -75.291667, -75.25, -75.208333, -75.166667, -75.125, -75.083333, -75.041667, -75, -74.958333, -74.916667, -74.875, -74.833333, -74.791667, -74.75, -74.708333, -74.666667, -74.625, -74.583333, -74.541667, -74.5, -74.458333, -74.416667, -74.375, -74.333333, -74.291667, -74.25, -74.208333, -74.166667, -74.125, -74.083333, -74.041667, -74, -73.958333, -73.916667, -73.875, -73.833333, -73.791667, -73.75, -73.708333, -73.666667, -73.625, -73.583333, -73.541667, -73.5, -73.458333, -73.416667, -73.375, -73.333333, -73.291667, -73.25, -73.208333, -73.166667, -73.125, -73.083333, -73.041667, -73, -72.958333, -72.916667, -72.875, -72.833333, -72.791667, -72.75, -72.708333, -72.666667, -72.625, -72.583333, -72.541667, -72.5, -72.458333, -72.416667, -72.375, -72.333333, -72.291667, -72.25, -72.208333, -72.166667, -72.125, -72.083333, -72.041667, -72, -71.958333, -71.916667, -71.875, -71.833333, -71.791667, -71.75, -71.708333, -71.666667, -71.625, -71.583333, -71.541667, -71.5, -71.458333, -71.416667, -71.375, -71.333333, -71.291667, -71.25, -71.208333, -71.166667, -71.125, -71.083333, -71.041667, -71, -70.958333, -70.916667, -70.875, -70.833333, -70.791667, -70.75, -70.708333, -70.666667, -70.625, -70.583333, -70.541667, -70.5, -70.458333, -70.416667, -70.375, -70.333333, -70.291667, -70.25, -70.208333, -70.166667, -70.125, -70.083333, -70.041667, -70, -69.958333, -69.916667, -69.875, -69.833333, -69.791667, -69.75, -69.708333, -69.666667, -69.625, -69.583333, -69.541667, -69.5, -69.458333, -69.416667, -69.375, -69.333333, -69.291667, -69.25, -69.208333, -69.166667, -69.125, -69.083333, -69.041667, -69, -68.958333, -68.916667, -68.875, -68.833333, -68.791667, -68.75, -68.708333, -68.666667, -68.625, -68.583333, -68.541667, -68.5, -68.458333, -68.416667, -68.375, -68.333333, -68.291667, -68.25, -68.208333, -68.166667, -68.125, -68.083333, -68.041667, -68, -67.958333, -67.916667, -67.875, -67.833333, -67.791667, -67.75, -67.708333, -67.666667, -67.625, -67.583333, -67.541667, -67.5, -67.458333, -67.416667, -67.375, -67.333333, -67.291667, -67.25, -67.208333, -67.166667, -67.125, -67.083333, -67.041667, -67, -66.958333, -66.916667, -66.875]
	}
	if srch_ll["lat"] < ll_dict["lat"][0] or srch_ll["lat"] > ll_dict["lat"][-1] or srch_ll["lon"] < ll_dict["lon"][0] or srch_ll["lon"] > ll_dict["lon"][-1]:
		return None
	ll_index = {}
	for ll in ["lat", "lon"]:
		lld = ll_dict[ll]
		small_diff = srch_ll[ll] - lld[0]
		ll_index[ll] = 0
		for i in range(1, len(lld)):
			diff = srch_ll[ll] - lld[i]
			if abs(diff) < small_diff:
				small_diff = copy.deepcopy(abs(diff))
				ll_index[ll] = copy.deepcopy(i)
			if diff < 0:
				break
	return ll_index

# return values from gridded soil temperature files for specified grid point and dates. output is json.	
def run_gridSoilTemps(ll,cover,sdate,edate):
	import numpy, urllib2
	from mx import DateTime
	miss = -999
	datasetBeginDate = DateTime.DateTime(2017,3,1)
	soilTempDirectory = "http://newadata.nrcc.cornell.edu/soilTemps/"
	try:
		if cover not in ['bare','grass']:
			raise gridSoilTempsException("bad cover: %s" % cover)
		#allow location provided as comma-separated string
		if isinstance(ll, basestring) and ll.find(",") > 0:
			ll = map(float, ll.split(","))
		if len(ll) == 2:
			loc = {"lon": ll[0], "lat": ll[1]}
		else:
			raise gridSoilTempsException("bad coordinates %s" % str(ll))
		gridpt = findNearestGrid(loc)
		if not gridpt:
			raise gridSoilTempsException("coordinates outside grid")
		else:
			yy,mm,dd = map(int, sdate.split('-'))
			theDate = DateTime.DateTime(yy,mm,dd)
			if theDate < datasetBeginDate:
				raise gridSoilTempsException('invalid sdate; dataset begins %s-%s-%s' % (datasetBeginDate.year,datasetBeginDate.month,datasetBeginDate.day))
			yy,mm,dd = map(int, edate.split('-'))
			edate_dt = DateTime.DateTime(yy,mm,dd)
			results = {"data": []}
			while theDate <= edate_dt:
				datestr = "%d-%02d-%02d" % (theDate.year,theDate.month,theDate.day)
				soilurl = "%ssoil2in_%s_%s.npy" % (soilTempDirectory, cover, datestr)
				try:
					soilfile = urllib2.urlopen(soilurl)
					soilTemps = numpy.loads(soilfile.read())
					dlyval = int(round(soilTemps[gridpt["lat"],gridpt["lon"]], 0))
				except:
					dlyval = miss
				results["data"].append([datestr, dlyval])
				theDate += DateTime.RelativeDate(days=+1)
	except gridSoilTempsException, e:
		results = {"error": str(e)}
	except:
		print_exception()
		results = {"error": str(e)}
	return json.dumps(results)

#--------------------------------------------------------------------------------------------					
def process_input (request,path):
	try:
#	 	retrieve input
		if path[0] in ['stationList','stateStationList','stateInactiveStationList','stationSisterInfo','diseaseStations','getForecastUrl','stationInfo','stationModels','getFcstData','gridSoilTemps']:
			try:
				smry_type = path[0]
				if len(path) > 1:
					if path[0] == 'stateStationList' or path[0] == 'stateInactiveStationList':
						list_options = {}
						list_options['reqvar'] = path[1]
						if len(path) > 2:
							list_options['state'] = path[2].upper()
						else:
							list_options['state'] = ''
					elif path[0] == 'stationSisterInfo':
						list_options = {}
						list_options['station'] = path[1]
						list_options['network'] = path[2]
					elif path[0] == 'getFcstData':
						list_options = {}
						list_options['station'] = path[1]
						list_options['network'] = path[2]
						list_options['variable'] = path[3]
						list_options['startdate'] = path[4]
						list_options['enddate'] = path[5]
					elif path[0] == 'gridSoilTemps':
						raise program_exit('Unexpected path to gridSoilTemps')
					else:
						list_options = path[1]
						if list_options == 'robots.txt': return newaUtil_io.robots()
				else:
					list_options = None
			except IndexError:
				raise program_exit('Error processing request')
			except:
				print_exception()
				raise program_exit('Error processing request')
		elif path[0] == 'robots.txt':
			return newaUtil_io.robots()
		else:
			return program_exit('Error processing input')
			
# 		send input to appropriate routine
		if smry_type == 'stationList':
			return run_stationList(list_options)
		if smry_type == 'stateStationList':
			return run_stateStationList(list_options)
		if smry_type == 'stationSisterInfo':
			return run_stationSisterInfo(list_options)
		if smry_type == 'stateInactiveStationList':
			return run_stateInactiveStationList(list_options)
		if smry_type == 'stationInfo':
			return run_stationInfo(list_options)
		if smry_type == 'stationModels':
			return run_stationModels(list_options)
		elif smry_type == 'diseaseStations':
			return run_diseaseStations(list_options)
		elif smry_type == 'getForecastUrl':
			return getForecastUrl(list_options)
		elif smry_type == 'getFcstData':
			return run_getFcstData(list_options)
		elif smry_type == 'gridSoilTemps':
			return run_gridSoilTemps(ll,cover,sdate,edate)
		else:
			return program_exit('Error processing request')
	except program_exit,msg:
		print msg
		return newaCommon_io.errmsg('Error processing request')
	except:
		print_exception()
		return newaCommon_io.errmsg('Unexpected error')

#--------------------------------------------------------------------------------------------					
def process_gridSoilTemps(request):
	try:
#	 	retrieve input
		if request and request.form:
			try:
				if request.form.has_key('ll'):
					ll = request.form['ll'].strip()
				if request.form.has_key('sdate'):
					sdate = request.form['sdate'].strip()
				if request.form.has_key('edate'):
					edate = request.form['edate'].strip()
				if request.form.has_key('cover'):
					cover = request.form['cover'].strip()
				else:
					cover = 'bare'
				return run_gridSoilTemps(ll,cover,sdate,edate)
			except:
				raise program_exit('Error processing gridSoilTemps form')
		else:
			return program_exit('Error processing gridSoilTemps; check input')			
	except program_exit,msg:
		print msg
		return newaCommon_io.errmsg('Error processing gridSoilTemps request')
	except:
		print_exception()
		return newaCommon_io.errmsg('Unexpected error')
