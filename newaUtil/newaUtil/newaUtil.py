#!/usr/local/bin/python

import sys, copy
from print_exception import print_exception
import newaUtil_io
if '/Users/keith/kleWeb/newaCommon' not in sys.path: sys.path.insert(1,'/Users/keith/kleWeb/newaCommon')
import newaCommon_io

try :
    import json
except ImportError :
    import simplejson as json
    
class program_exit (Exception):
	pass
			
def NameAny_to_dict(na) :
	ret = {}
	for a in na:
		ret[a.name] = a.value.value()
	return ret

def getForecastUrl(stn):
	forecastUrl = ""
	try:
		from stn_info import stn_info
		if not stn_info.has_key(stn):
			from stn_info_ma import stn_info
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
	from disease_vars_dict import disease_vars
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
		from stn_info import stn_info
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
					whole_url = "http://newa.nrcc.cornell.edu/"+murl+"/"+stn
					if murl == "newaDisease/onion_dis" or murl == "newaDisease/onion_onlog" or murl == "newaDisease/onion_smbalog" or murl == "newaDisease/onion_sbalog":
						whole_url = whole_url+"/9999"
					elif murl == "newaDisease/tomato_for":
						whole_url = whole_url+"/9999/5"
					elif murl == "newaDisease/potato_pdays" or murl == "newaDisease/potato_lb":
						whole_url = whole_url+"/9999/5/1"
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
		from stn_info import stn_info
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
		for state in ['NY','VT','MA','NH','CT','RI','NJ','PA','DE','MD','ME','DC','WI','IA','NE','MN','NC','IL','SD','MO']:
			for usk in unsortedKeys:
				if state == unsortedDict[usk]['state']:
					station_dict['stations'].append(unsortedDict[usk])
					json_return = json.dumps(station_dict)
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
			exec("from stn_info_" + state.lower() + " import stn_info")
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
			exec("from stn_info_" + state.lower() + "_inactive import stn_info")
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
		from stn_info import stn_info
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
			
#--------------------------------------------------------------------------------------------					
def process_input (request,path):
	try:
#	 	retrieve input
		if path[0] in ['stationList','stateStationList','stateInactiveStationList','diseaseStations','getForecastUrl','stationInfo','stationModels']:
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
		else:
			return program_exit('Error processing request')
	except program_exit,msg:
		print msg
		return newaCommon_io.errmsg('Error processing request')
	except:
		print_exception()
		return newaCommon_io.errmsg('Unexpected error')
