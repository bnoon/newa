import sys, copy, math, Data
from mx import DateTime
from print_exception import print_exception
import newaCommon_io
from sister_info import sister_info
import ucanCallMethods
from bsddb import hashopen
from cPickle import loads
from morecs.solar_main_routine import SOLAR_MAIN
from morecs.solar_fcst2 import solar_main_fcst2

sta_por = { "1fr": ('20010323','20100330'),  "1wi": ('19970401','99991231'),  "alb": ('20001224','99991231'),
			"ark": ('19960419','99991231'),  "bat": ('19960402','99991231'),  "bra": ('19960531','99991231'),
			"chz": ('20041022','99991231'),  "cli": ('20040412','99991231'),  "cln": ('20040828','99991231'),  
			"dre": ('20000420','20101213'),  "ede": ('19960623','99991231'),  "elb": ('19960402','99991231'),
			"far": ('20030221','99991231'),  "fre": ('20020523','99991231'),  "fri": ('19960323','99991231'),
			"gai": ('19960402','99991231'),  "gen": ('19960717','99991231'),  "gro": ('19960401','99991231'),
			"gui": ('20070120','99991231'),  "him": ('19960323','99991231'),  "ith": ('20020408','99991231'),
			"kno": ('20010314','20100627'),  "lan": ('20020403','99991231'),  "loc": ('20060530','99991231'),
			"lyn": ('20010315','20101214'),  "mex": ('19970411','20100726'),  "nap": ('20000801','20100324'),
			"noa": ('20010412','99991231'),  "pav": ('20000504','20100627'),  "pot": ('19960530','99991231'),
			"pra": ('19960505','99991231'),  "pul": ('20000602','99991231'),  "red": ('20050404','99991231'),
			"sav": ('19960401','99991231'),  "scr": ('19960331','99991231'),  "soa": ('20010321','99991231'),
			"sod": ('19960418','99991231'),  "val": ('20000420','20101125'),  "wat": ('20010316','20101231'),
			"way": ('19960423','99991231'),  "wgl": ('20070329','99991231'),  "avo": ('19960423','20030713'),
			"bar": ('20010502','99991231'),  "cam": ('19990609','20010809'),  "cat": ('20030708','20060726'),
			"cha": ('19960523','20020809'),  "sci": ('19980409','20041019'),  "por": ('20100406','99991231'),
			"vso": ('20100508','99991231'),  "vsb": ('20100501','99991231'),  "ved": ('20100513','99991231'),
			"vpu": ('20100513','99991231'),  "per": ('20080406','99991231'),  "2wi": ('20100608','99991231'),
			"arm": ('20100608','20101214'),  "1lo": ('20090718','20120707'),  "har": ('20100429','20100927'),
			"vca": ('20100616','99991231'),  "clw": ('20100722','99991231')}

miss = -999
lt_end_hour = 23

class DateMismatch (Exception):
	pass

ucan = ucanCallMethods.general_ucan()

#--------------------------------------------------------------------------------------------	
def get_metadata (station_id,id_type=None):
	ucanid = None
	station_name = station_id
	try:
		if not id_type:
			if station_id[0:1] >= '1' and station_id[0:1] <= '9' and station_id[1:2] >= '0' and station_id[1:2] <= '9':
				id_type = 'njwx'
			elif len(station_id) == 4:
				id_type = 'icao'
			elif station_id[0:3] == "cu_" or station_id[0:3] == "um_" or station_id[0:3] == "uc_" or station_id[0:3] == "un_":
				id_type = 'cu_log'
			elif station_id[0:3] == "ew_":
				station_id = station_id[3:]
				id_type = 'miwx'
			elif len(station_id) == 3 or len(station_id) == 6:
				id_type = 'newa'
			else:
				return newaCommon_io.errmsg('Error processing form; check station input')
		elif id_type == 'miwx' and len(station_id) == 6:
			station_id = station_id[3:]
		query = ucan.get_query()
		r = query.getUcanFromIdAsSeq(str(station_id),str(id_type))
		if len(r) > 0:
			ucanid = r[-1].ucan_id
			info = query.getInfoForUcanIdAsSeq(ucanid,())
			fields = ucanCallMethods.NameAny_to_dict(info[-1].fields)
			station_name = fields['name']
		query.release()
	except:
		print 'Error getting metadata for',station_id,id_type
		print_exception()
		if not query._non_existent(): query.release()
		raise
	return ucanid, station_name

#--------------------------------------------------------------------------------------------	
def initHourlyVar (staid, var, miss, station_type='newa'):
	# var minors from the following dictionary are no longer used anywhere, so do not have to be accurate
	var_dict = {'newa':  {'prcp': [5,6,  'inch','%.2f'],      'temp': [23,6, 'degF',   '%.1f'],
						  'lwet': [118,1,'',    '%3.0f'],     'rhum': [24,5, 'percent','%.1f'],
						  'wspd': [128,5, 'miles/hour','%.1f'],'srad': [132,1,'langley','%.2f'],
						  'st4i': [120,1,'degF','%.1f'],	  'wdir': [130,5,'degrees','%.0f'],
						  'st8i': [120,2,'degF','%.1f'] },
				'icao':  {'prcp': [5,3,  'inch','%.2f'],      'temp': [23,3, 'degF',   '%.0f'],
						  'dwpt': [22,3, 'degF',    '%4.0f'], 'rhum': [24,3, None,'%.0f'],
						  'wspd': [28,3, 'miles/hour','%.1f'],'tsky': [33,3,'count',   '%3.1f'], 
						  'wdir': [27,3, 'degrees', '%.0f'],  'stpr': [18,3,'inch_Hg',   '%6.3f'],
						  'ceil': [35,3,'100 feet','%7.0f'],  'wthr': [20,3,'',       '%{abbr}s'],
						  'ccnd': [30,3,'',     '%{abbr}s'],  'chgt': [31,3,'feet',      '%.0f '],
						  'visi': [26,3,'miles',   '%5.2f']},
				'cu_log':{'prcp': [5,7,  'inch','%.2f'],      'temp': [126,1,'degF',   '%.1f'],
						  'lwet': [118,2,'',    '%3.0f'],     'rhum': [24,6, None,'%.0f'],
						  'wspd': [128,1,'miles/hour','%.1f'],'srad': [132,1,'langley','%.1f'],
						  'wdir': [130,1,'degrees','%.0f'],   'st4i': [121,265,'degF','%.1f'],
						  'st8i': [121,393,'degF','%.1f'] },
				'njwx':  {'prcp': [5,6,  'inch','%.2f'],      'temp': [23,6, 'degF',   '%.1f'],
						  'rhum': [24,5, 'percent','%.1f'],   'lwet': [118,999,'',    '%3.0f'],
						  'wspd': [28,5, 'miles/hour','%.1f'],
						  'srad': [149,1,'watt/meter2','%.2f'],
						  'wdir': [27,5,'degrees','%.0f'] },
				'deos':  {'prcp': [5,11,  'inch', '%.2f'],    'temp': [23,9,  'degF',   '%.1f'],
						  'lwet': [118,4,'',     '%3.0f'],    'rhum': [24,11, 'percent','%.1f'],
						  'wspd': [28,8, 'miles/hour','%.1f'],'srad': [132,7, 'langley','%.2f'],
						  'wdir': [27,8,'degrees','%.0f'] },
				'miwx':  {'prcp': [5,12,  'inch', '%.2f'],    'temp': [126,7, 'degF',   '%.1f'],
						  'lwet': [118,6,'',     '%3.0f'],    'rhum': [143,3, 'percent','%.1f'],
						  'srad': [132,8, 'langley','%.2f'] }
				}
	v = None
	miss_str = "%s" % miss
	if var_dict.has_key(station_type) and var_dict[station_type].has_key(var):
		major,minor,units,format = var_dict[station_type][var]
	else:
		return v
	try:
		data = ucan.get_data()
		if station_type == 'icao':
			v = data.newTSVarNative(major,0,str(staid))
		else:
			v = data.newTSVar(major,0,staid)
		if units: v.setUnits (units)
		v.setDataStringFormat (format)
		v.setMissingDataAsString(miss_str)
		v.setMissingDataAsFloat(miss)
	except Data.TSVarFactory.UnknownUcanId:
#		print 'Unknown ucan id',var
#		old majors for non-ip100 loggers
		if var == 'wspd' and station_type == 'newa':
			try:
				v = data.newTSVar(28,0,staid)
				if units: v.setUnits (units)
				v.setMissingDataAsFloat(miss)
			except:
				pass
		elif var == 'wdir' and station_type == 'newa':
			try:
				v = data.newTSVar(27,0,staid)
				if units: v.setUnits (units)
				v.setMissingDataAsFloat(miss)
			except:
				pass
		elif var == 'srad' and station_type == 'newa':
			try:
				v = data.newTSVar(119,0,staid)
				if units: v.setUnits (units)
				v.setMissingDataAsFloat(miss)
			except:
				pass
		elif var == 'wspd' and station_type == 'njwx':	#IAS stations
			try:
				v = data.newTSVar(128,0,staid)
				if units: v.setUnits (units)
				v.setMissingDataAsFloat(miss)
			except:
				pass
		pass
	except:
#		print "Error initializing:",var
#		print_exception()
		pass
	return v

#--------------------------------------------------------------------------------------------	
def getHourlyVars (var, v, start_date, end_date):
	values = []
	vdates = []
	vflags = []
	if v:
		try:
			v.setDateRange (start_date,end_date)
			vdates = v.getDateArraySeq()
			if var in ['wthr','ccnd','chgt']:
				values = v.getDataSeqAsAny ()
			else:
				values = v.getDataSeqAsFloat ()
			vflags = v.getValidFlagSeq()
#			values,vdates,vflags = trim_missing(values,vdates,vflags)
		except (Data.TSVar.UnavailableDateRange, Data.TSVar.InvalidDateRange):
#			print 'unavailable or invalid data range',start_date,end_date
			pass
		except:
			print "Error processing:",var,v,start_date,end_date
			print_exception()
	return values, vdates, vflags

#--------------------------------------------------------------------------------------------		
def trim_missing (values,vdates,vflags):
#	remove missing values at the end of the list
	try:
		for i in range(len(values)-1,-1,-1):
			if values[i] == miss:
				del values[i]
				del vdates[i]
				del vflags[i]
			else:
				break
	except:
		print_exception()
	return values,vdates,vflags

#--------------------------------------------------------------------------------------------		
def fill_with_missing (start_period_dt,end_period_dt,miss):
	values = []
	vdates = []
	vflags = []
	try:
		fill_time = start_period_dt
		count = 0
		while fill_time < end_period_dt:
			values.append(miss)
			vdates.append([fill_time.year,fill_time.month,fill_time.day,fill_time.hour])
			vflags.append(0)
			count = count + 1
			fill_time = fill_time + DateTime.RelativeDate(hours=+1)
	except:
		print_exception()
	return values,vdates,vflags

#--------------------------------------------------------------------------------------------		
def estmiss (var,hindx,miss):
#	estimate missing values using average of previous and next good value within three hours.
	maxlook = 1    #max number of hours to look backward/forward
	listlen = len(var)
	chk = hindx
	prev = miss
	while prev == miss:
		chk = chk-1
		if chk < hindx-maxlook or chk <0:
			break
		else:
			if len(var) > chk: prev = var[chk]
	chk = hindx
	next = miss
	while next == miss:
		chk = chk+1
		if chk > hindx+maxlook or chk >= listlen:
			break
		else:
			next = var[chk]
#	if next == miss:
#		next = prev
#	elif prev == miss:
#		prev = next
	if next != miss and prev != miss:
		replacement = (next+prev)/2.
	else:
		replacement = miss
	return replacement
	
#--------------------------------------------------------------------------------------------		
def getSR(sid, date) :
	import urllib2, json
	try:
		params = {'sid':sid, 'sdate':date, 'edate':date}
		req = urllib2.Request('http://adhoc.rcc-acis.org/SolarRadiation',
			  json.dumps(params), {'Content-Type':'application/json'})
		response = urllib2.urlopen(req)
		results = json.loads(response.read())
		# check for error returned from web services
		if results.has_key("error"):
			print "Error returned from solar rad web service call:",results["error"]
			return None
	except:
		print "Error returned from solar rad web service call with",params
		return None
	return results

#--------------------------------------------------------------------------------------------		
def sister_est(stn,var,var_date,end_period,tsvars,dataForEst, datesForEst, vflagsForEst, stn_type='newa'):
	replacement = miss
	try:
		if sister_info.has_key(stn) and sister_info[stn].has_key(var):
			if tsvars.has_key(var):
				est0 = tsvars[var]['tsv']
			else:
				sister = sister_info[stn][var]
				if sister[0:1] >= '1' and sister[0:1] <= '9' and sister[1:2] >= '0' and sister[1:2] <= '9':
					station_type = 'njwx'
					est_staid,station_name = get_metadata (sister, station_type)
				elif len(sister) == 4:
					station_type = 'icao'
					est_staid = sister.upper()
				elif sister[0:3] == "cu_" or sister[0:3] == "um_" or sister[0:3] == "uc_" or sister[0:3] == "un_":
					station_type = 'cu_log'
					est_staid,station_name = get_metadata (sister, station_type)
				elif sister[0:3] == "ew_":
					sister = sister[3:]
					station_type = 'miwx'
					est_staid,station_name = get_metadata (sister, station_type)
				elif len(sister) == 3 or len(sister) == 6:
					station_type = 'newa'
					est_staid,station_name = get_metadata (sister, station_type)
				else:
					return replacement
					
				if var == 'srad' and station_type == 'icao':
					estdate = "%04d%02d%02d%02d" % (var_date[0],var_date[1],var_date[2],var_date[3])
					replacement_dict = getSR(est_staid, estdate)
					if not replacement_dict or replacement_dict['data'][0][1] == "M":
						replacement = miss
					else:
						replacement = float(replacement_dict['data'][0][1])
#					print "replacement for",stn,"using",est_staid,"for",estdate,"is",replacement
					return replacement, tsvars, dataForEst, datesForEst, vflagsForEst
				else:
					est0 = initHourlyVar (est_staid, var, miss, station_type)
#					ADDED 5/18/2015 -kle
					if var == 'srad' and (est0.getUnits()).find('langley') < 0:
						est0.setUnits('langley/hour')
					tsvars[var] = {}
					tsvars[var]['tsv'] = est0
					tsvars[var]['ed'] = None
			
			if (not datesForEst.has_key(var) or var_date not in datesForEst[var]) and tsvars[var]['ed'] != end_period:
				the_hr = (var_date[0],var_date[1],var_date[2],var_date[3])
				dataForEst[var],datesForEst[var],vflagsForEst[var] = getHourlyVars(var,est0,the_hr,end_period)
				tsvars[var]['ed'] = end_period
			if var_date in datesForEst[var] and len(dataForEst[var]) > 0:
				dind = datesForEst[var].index(var_date)
				try:
					replacement = dataForEst[var][dind]
				except:
					print 'Error assigning replacement for',stn
					print '   dates:',datesForEst
					print '   values:',dataForEst
					print '   index:',dind
					print_exception()
		else:
#			print 'No sister info for station',stn,'or variable',var,'on',var_date
			pass
	except:
		print_exception()
	return replacement, tsvars, dataForEst, datesForEst, vflagsForEst

#--------------------------------------------------------------------------------------------		
def get_fcst_hour (stn, requested_var, date_dt):
	hourly_fcst = miss
	try:
		if requested_var in ['temp','rhum']:
			stn = stn.upper()
			forecast_db = hashopen('/ndfd/hourly_forecasts.db','r')		
			stn_dict = loads(forecast_db[stn])
			forecast_db.close()
			if stn_dict.has_key(requested_var):					
				dkey = (date_dt.year, date_dt.month, date_dt.day)
				if stn_dict[requested_var].has_key(dkey):
					hourly_fcst = stn_dict[requested_var][dkey][date_dt.hour]
	except:
		print_exception()
		print 'for',stn,requested_var,date_dt
	return hourly_fcst

#--------------------------------------------------------------------------------------------		
def get_newa_data (stn,native_id,start_date_dt,end_date_dt,station_type='newa'):
	hourly_data = []
	daily_data = []
	avail_vars = []
	if station_type == 'miwx' and len(native_id) == 3:
		orig_id = 'ew_%s' % native_id
	else:
		orig_id = native_id
	try:
#		don't try to go into the future
		now = DateTime.now()
		if end_date_dt > now: end_date_dt = now

#		start and end dates are provided in Local Time, adjust for DST if necessary
		if start_date_dt.dst == 1:
			start_date_dt = start_date_dt + DateTime.RelativeDate(hours=-1)
		if end_date_dt.dst == 1:
			end_date_dt = end_date_dt + DateTime.RelativeDate(hours=-1)
			
#		set for non-inclusive end date
		end_date_dt = end_date_dt + DateTime.RelativeDate(hours=+1)

##		avoid problem with starting or ending hour of zero			
##		if start_date_dt.hour == 0:
##			start_date_dt = start_date_dt + DateTime.RelativeDate(hours=-1)
##		if end_date_dt.hour == 0:
##			end_date_dt = end_date_dt + DateTime.RelativeDate(hours=+1)
	
#		setup necessary TSVars
		temp0 = initHourlyVar (stn, 'temp', miss, station_type)
		lwet0 = initHourlyVar (stn, 'lwet', miss, station_type)
		prcp0 = initHourlyVar (stn, 'prcp', miss, station_type)
		rhum0 = initHourlyVar (stn, 'rhum', miss, station_type)
		wspd0 = initHourlyVar (stn, 'wspd', miss, station_type)
		wdir0 = initHourlyVar (stn, 'wdir', miss, station_type)
		srad0 = initHourlyVar (stn, 'srad', miss, station_type)
		st4i0 = initHourlyVar (stn, 'st4i', miss, station_type)
		
#		init counters
		temp_sum = 0.
		temp_cnt = 0.
		temp_max = -9999.
		temp_min = 9999.
		prcp_sum = 0.
		prcp_cnt = 0.
		lwet_sum = 0.
		lwet_cnt = 0.
		rhum_sum = 0.
		rhum_cnt = 0.
		wspd_sum = 0.
		wdir_sum = 0.
		wspd_cnt = 0.
		wdir_cnt = 0.
		srad_sum = 0.
		srad_cnt = 0.
		st4i_sum = 0.
		st4i_cnt = 0.
		st4i_max = -9999.
		st4i_min = 9999.
		temp_dflag = ''
		prcp_dflag = ''
		lwet_dflag = ''
		rhum_dflag = ''
		wspd_dflag = ''
		wdir_dflag = ''
		srad_dflag = ''
		st4i_dflag = ''
		
		est_tsvars = {}
		dataForEst = {}
		datesForEst = {}
		vflagsForEst = {}
		
#	 	break entire period up into chunks no larger than 30-days
		start_period_dt = start_date_dt
		while start_period_dt < end_date_dt:
			end_period_dt = start_period_dt + DateTime.RelativeDate(days=+30)
			if end_period_dt > end_date_dt: end_period_dt = end_date_dt
#			convert dates to tuples for tsvar calls
			start_period = start_period_dt.tuple()[:4]
			end_period = end_period_dt.tuple()[:4]
			
#	 		get necessary hourly data for the period
			temp,temp_dates,temp_vflags = getHourlyVars('temp',temp0,start_period,end_period)
			lwet,lwet_dates,lwet_vflags = getHourlyVars('lwet',lwet0,start_period,end_period)
			rhum,rhum_dates,rhum_vflags = getHourlyVars('rhum',rhum0,start_period,end_period)
			prcp,prcp_dates,prcp_vflags = getHourlyVars('prcp',prcp0,start_period,end_period)
			wspd,wspd_dates,wspd_vflags = getHourlyVars('wspd',wspd0,start_period,end_period)
			wdir,wdir_dates,wdir_vflags = getHourlyVars('wdir',wdir0,start_period,end_period)
			srad,srad_dates,srad_vflags = getHourlyVars('srad',srad0,start_period,end_period)
			st4i,st4i_dates,st4i_vflags = getHourlyVars('st4i',st4i0,start_period,end_period)
			if len(temp) > 0 and 'temp' not in avail_vars: avail_vars.append('temp')
			if len(lwet) > 0 and 'lwet' not in avail_vars: avail_vars.append('lwet')
			if len(prcp) > 0 and 'prcp' not in avail_vars: avail_vars.append('prcp')
			if len(rhum) > 0 and 'rhum' not in avail_vars: 
				avail_vars.append('rhum')
				avail_vars.append('eslw')
				for i in range(0,len(rhum)):
					if rhum[i] == 0: rhum[i] = miss			#occurs occasionally in NEWA data
			if len(wspd) > 0 and 'wspd' not in avail_vars: avail_vars.append('wspd')
			if len(wdir) > 0 and 'wdir' not in avail_vars: avail_vars.append('wdir')
			if len(srad) > 0 and 'srad' not in avail_vars: avail_vars.append('srad')
			if len(st4i) > 0 and 'st4i' not in avail_vars: avail_vars.append('st4i')
			
#			don't try to fill data after end of record			
			if end_date_dt == end_period_dt:
				temp,temp_dates,temp_vflags = trim_missing(temp,temp_dates,temp_vflags)
				lwet,lwet_dates,lwet_vflags = trim_missing(lwet,lwet_dates,lwet_vflags)
				rhum,rhum_dates,rhum_vflags = trim_missing(rhum,rhum_dates,rhum_vflags)
				prcp,prcp_dates,prcp_vflags = trim_missing(prcp,prcp_dates,prcp_vflags)
				wspd,wspd_dates,wspd_vflags = trim_missing(wspd,wspd_dates,wspd_vflags)
				wdir,wdir_dates,wdir_vflags = trim_missing(wdir,wdir_dates,wdir_vflags)
				srad,srad_dates,srad_vflags = trim_missing(srad,srad_dates,srad_vflags)
				st4i,st4i_dates,st4i_vflags = trim_missing(st4i,st4i_dates,st4i_vflags)
				
#	 		check beginning dates of all lists
			if len(temp_dates) > 0 and start_period_dt != DateTime.DateTime(*temp_dates[0]):
				raise DateMismatch('Start of temp data does not match requested start date!')
			if len(lwet_dates) > 0 and start_period_dt != DateTime.DateTime(*lwet_dates[0]):
				raise DateMismatch('Start of lwet data does not match requested start date!')
			if len(rhum_dates) > 0 and start_period_dt != DateTime.DateTime(*rhum_dates[0]):
				raise DateMismatch('Start of rh data does not match requested start date!')
			if len(prcp_dates) > 0 and start_period_dt != DateTime.DateTime(*prcp_dates[0]):
				raise DateMismatch('Start of prcp data does not match requested start date!')
			if len(wspd_dates) > 0 and start_period_dt != DateTime.DateTime(*wspd_dates[0]):
				raise DateMismatch('Start of wspd data does not match requested start date!')
			if len(wdir_dates) > 0 and start_period_dt != DateTime.DateTime(*wdir_dates[0]):
				raise DateMismatch('Start of wdir data does not match requested start date!')
			if len(srad_dates) > 0 and start_period_dt != DateTime.DateTime(*srad_dates[0]):
				raise DateMismatch('Start of srad data does not match requested start date!')
			if len(st4i_dates) > 0 and start_period_dt != DateTime.DateTime(*st4i_dates[0]):
				raise DateMismatch('Start of st4i data does not match requested start date!')
		
#			find number of hours to loop through (before filling missing)
			num_hrs = max(len(temp),len(lwet),len(rhum),len(prcp),len(wspd),len(wdir),len(srad),len(st4i))
#			use longest date list
			for v,vd in [(temp,temp_dates),(lwet,lwet_dates),(rhum,rhum_dates),(prcp,prcp_dates),(wspd,wspd_dates),(wdir,wdir_dates),(srad,srad_dates),(st4i,st4i_dates)]:
				if len(v) == num_hrs:
					dates = vd
					break

#			if no data, fill with missing to be estimated later
			if len(temp) == 0 and temp0: temp,temp_dates,temp_vflags = fill_with_missing(start_period_dt,end_period_dt,miss)
			if len(lwet) == 0 and lwet0: lwet,lwet_dates,lwet_vflags = fill_with_missing(start_period_dt,end_period_dt,miss)
			if len(rhum) == 0 and rhum0: rhum,rhum_dates,rhum_vflags = fill_with_missing(start_period_dt,end_period_dt,miss)
			if len(prcp) == 0 and prcp0: prcp,prcp_dates,prcp_vflags = fill_with_missing(start_period_dt,end_period_dt,miss)
			if len(wspd) == 0 and wspd0: wspd,wspd_dates,wspd_vflags = fill_with_missing(start_period_dt,end_period_dt,miss)
			if len(wdir) == 0 and wdir0: wdir,wdir_dates,wdir_vflags = fill_with_missing(start_period_dt,end_period_dt,miss)
			if len(srad) == 0 and srad0: srad,srad_dates,srad_vflags = fill_with_missing(start_period_dt,end_period_dt,miss)
			if len(st4i) == 0 and st4i0: st4i,st4i_dates,st4i_vflags = fill_with_missing(start_period_dt,end_period_dt,miss)

#			if there was nothing before, check again now that lists have been filled
			if num_hrs == 0:
				num_hrs = max(len(temp),len(lwet),len(rhum),len(prcp),len(wspd),len(wdir),len(srad),len(st4i))
#				use longest date list
				for v,vd in [(temp,temp_dates),(lwet,lwet_dates),(rhum,rhum_dates),(prcp,prcp_dates),(wspd,wspd_dates),(wdir,wdir_dates),(srad,srad_dates),(st4i,st4i_dates)]:
					if len(v) == num_hrs:
						dates = vd
						break

#	 		process data hourly	
			theDate = start_period_dt
			hindx = 0
			while hindx < num_hrs:
###				Next line moved up from below
				lt_dt = theDate + DateTime.RelativeDate(hours=+theDate.dst)
				for var,values,vflags in [('temp',temp,temp_vflags), ('lwet',lwet,lwet_vflags),
				                          ('rhum',rhum,rhum_vflags), ('wspd',wspd,wspd_vflags),
				                          ('srad',srad,srad_vflags), ('st4i',st4i,st4i_vflags),
				                          ('prcp',prcp,prcp_vflags), ('wdir',wdir,wdir_vflags)]:
					if len(values) > 0:
						if hindx < len(values) and vflags[hindx]:
							val = values[hindx]
							val_eflag = ''
						else:
							val = miss
							val_eflag = 'M'
						if val == miss:							# for missing values, do estimation based on surrounding hours
							if var not in ['prcp','wdir']:
								val = estmiss(values,hindx,miss)
								val_eflag = 'I'
							else:
								val = miss
							if val == miss: 					# if still missing, use sister station
								val,est_tsvars,dataForEst,datesForEst,vflagsForEst = sister_est(orig_id,var,dates[hindx],end_period,est_tsvars,dataForEst, datesForEst, vflagsForEst,station_type)
								val_eflag = 'S'
								if val == miss:
									val_eflag = 'M'

### Following added 10/2/2014 - kle
							if val == miss and (var == 'temp' or var == 'rhum'):
								val = get_fcst_hour(orig_id, var, lt_dt)
								val_eflag = 'N'
###

					else:
						val = miss
						val_eflag = 'M'
					if   var == 'temp': tempv=val; temp_eflag=val_eflag
					elif var == 'lwet': lwetv=val; lwet_eflag=val_eflag
					elif var == 'rhum': rhumv=val; rhum_eflag=val_eflag
					elif var == 'wspd': wspdv=val; wspd_eflag=val_eflag
					elif var == 'srad': sradv=val; srad_eflag=val_eflag
					elif var == 'st4i': st4iv=val; st4i_eflag=val_eflag
					elif var == 'prcp': prcpv=val; prcp_eflag=val_eflag
					elif var == 'wdir': wdirv=val; wdir_eflag=val_eflag
					
#				save hourly data in local time
###				lt_dt = theDate + DateTime.RelativeDate(hours=+theDate.dst)
				eflags = (temp_eflag, prcp_eflag, lwet_eflag, rhum_eflag, wspd_eflag, wdir_eflag, srad_eflag, st4i_eflag)
				hourly_data.append(((lt_dt.year,lt_dt.month,lt_dt.day,lt_dt.hour),tempv,prcpv,lwetv,rhumv,wspdv,wdirv,sradv,st4iv,eflags))

#				do calculations for daily data
				if tempv != miss:
					temp_sum = temp_sum + tempv
					if tempv > temp_max: temp_max = copy.deepcopy(tempv)
					if tempv < temp_min: temp_min = copy.deepcopy(tempv)
					temp_cnt = temp_cnt + 1
					if temp_eflag in ['S','I']: temp_dflag = 'E'
				if prcpv != miss:
					prcp_sum = prcp_sum + prcpv
					prcp_cnt = prcp_cnt + 1
					if prcp_eflag in ['S','I']: prcp_dflag = 'E'
				if lwetv != miss:
					if lwetv > 0: lwet_sum = lwet_sum + 1
					lwet_cnt = lwet_cnt + 1
					if lwet_eflag in ['S','I']: lwet_dflag = 'E'
				if rhumv != miss:
					if rhumv >= 90: rhum_sum = rhum_sum + 1
					rhum_cnt = rhum_cnt + 1
					if rhum_eflag in ['S','I']: rhum_dflag = 'E'
				if wspdv != miss:
					wspd_sum = wspd_sum + wspdv
					wspd_cnt = wspd_cnt + 1
					if wspd_eflag in ['S','I']: wspd_dflag = 'E'
				if wdirv != miss:
					wdir_sum = wdir_sum + wdirv
					wdir_cnt = wdir_cnt + 1
					if wdir_eflag in ['S','I']: wdir_dflag = 'E'
				if sradv != miss:
					srad_sum = srad_sum + sradv
					srad_cnt = srad_cnt + 1
					if srad_eflag in ['S','I']: srad_dflag = 'E'
				if st4iv != miss:
					st4i_sum = st4i_sum + st4iv
					if st4iv > st4i_max: st4i_max = copy.deepcopy(st4iv)
					if st4iv < st4i_min: st4i_min = copy.deepcopy(st4iv)
					st4i_cnt = st4i_cnt + 1
					if st4i_eflag in ['S','I']: st4i_dflag = 'E'
					
#				end of "day" update
				last_hr = lt_end_hour-theDate.dst
				if last_hr == 24:
					last_hr = 0
					day_diff = -1
				else:
					day_diff = 0
				if theDate.hour == last_hr:
					if temp_cnt > 0:
						dly_temp_ave = temp_sum/temp_cnt
						dly_temp_max = temp_max
						dly_temp_min = temp_min
					else:
						dly_temp_ave = miss
						dly_temp_max = miss
						dly_temp_min = miss
					if prcp_cnt > 0:
						dly_prcp_tot = prcp_sum
					else:
						dly_prcp_tot = miss
					if lwet_cnt > 0:
						dly_lwet_hrs = lwet_sum
					else:
						dly_lwet_hrs = miss
					if rhum_cnt > 0:
						dly_rhum_hrs = rhum_sum
					else:
						dly_rhum_hrs = miss
					if wspd_cnt > 0:
						dly_wspd_ave = wspd_sum/wspd_cnt
					else:
						dly_wspd_ave = miss
					if wdir_cnt > 0:
						dly_wdir_ave = wdir_sum/wdir_cnt
					else:
						dly_wdir_ave = miss
					if srad_cnt > 0:
						dly_srad_tot = srad_sum
					else:
						dly_srad_tot = miss
					if st4i_cnt > 0:
						dly_st4i_ave = st4i_sum/st4i_cnt
						dly_st4i_max = st4i_max
						dly_st4i_min = st4i_min
					else:
						dly_st4i_ave = miss
						dly_st4i_max = miss
						dly_st4i_min = miss
						
#					save daily data
					if day_diff == 0:
						ddt = theDate
					else:
						ddt = theDate + DateTime.RelativeDate(days=day_diff)
					dflags = (temp_dflag, prcp_dflag, lwet_dflag, rhum_dflag, wspd_dflag, wdir_dflag, srad_dflag, st4i_dflag)
					daily_data.append(([ddt.year,ddt.month,ddt.day], 
					         dly_temp_ave, dly_temp_max, dly_temp_min, dly_prcp_tot, dly_lwet_hrs, \
					         dly_rhum_hrs, dly_wspd_ave, dly_srad_tot, dly_st4i_ave, dly_st4i_max, \
					         dly_st4i_min, dflags))
						
					temp_sum = 0.
					temp_cnt = 0.
					temp_max = -9999.
					temp_min = 9999.
					prcp_sum = 0.
					prcp_cnt = 0.
					lwet_sum = 0.
					lwet_cnt = 0.
					rhum_sum = 0.
					rhum_cnt = 0.
					wspd_sum = 0.
					wspd_cnt = 0.
					wdir_sum = 0.
					wdir_cnt = 0.
					srad_sum = 0.
					srad_cnt = 0.
					st4i_sum = 0.
					st4i_cnt = 0.
					st4i_max = -9999.
					st4i_min = 9999.
					temp_dflag = ''
					prcp_dflag = ''
					lwet_dflag = ''
					rhum_dflag = ''
					wspd_dflag = ''
					wdir_dflag = ''
					srad_dflag = ''
					st4i_dflag = ''
	
#				next hour to process
				theDate = theDate + DateTime.RelativeDate(hours=+1)
				hindx = hindx+1
	
#			reset for start of next 30-day chunk
			start_period_dt = end_period_dt
	except DateMismatch, logmsg:
		sys.stdout.write('%s\n' % logmsg)		
		return ([],[],[])
	except:
		print_exception()
	
#	release TSVars		
	if temp0: temp0.release()
	if lwet0: lwet0.release()
	if rhum0: rhum0.release()
	if prcp0: prcp0.release()
	if wspd0: wspd0.release()
	if wdir0: wdir0.release()
	if srad0: srad0.release()
	if st4i0: st4i0.release()
	for key in est_tsvars.keys():
		if est_tsvars[key]['tsv']: est_tsvars[key]['tsv'].release()
	return (hourly_data, daily_data, avail_vars)

#--------------------------------------------------------------------------------------------		

def get_fcst_data (stn, requested_var, start_date_dt, end_date_dt):
	hourly_fcst = {}
	try:
		if requested_var == 'prcp': requested_var = 'qpf'
		if requested_var == 'srad':
			hourly_fcst = solar_main_fcst2(stn,(start_date_dt.year,start_date_dt.month,start_date_dt.day,start_date_dt.hour),\
									(end_date_dt.year,end_date_dt.month,end_date_dt.day,end_date_dt.hour))
		else:
			stn = stn.upper()
			forecast_db = hashopen('/ndfd/hourly_forecasts.db','r')		
			stn_dict = loads(forecast_db[stn])
			forecast_db.close()
			if stn_dict.has_key(requested_var):
				for dkey in stn_dict[requested_var].keys():
					dkey_dt = DateTime.DateTime(*dkey)
					if dkey_dt >= start_date_dt and dkey_dt <= end_date_dt:
						for h in range(0,24):
							if stn_dict[requested_var][dkey][h] != miss:
								if requested_var != 'qpf':
									tkey = (dkey[0],dkey[1],dkey[2],h)
									hourly_fcst[tkey] = stn_dict[requested_var][dkey][h]
								else:
									#split qpf over last 6 hours
									for phr in range(0,6):
										pdt = dkey_dt + DateTime.RelativeDate(hour=h) + DateTime.RelativeDate(hours=-phr)
										tkey = (pdt.year,pdt.month,pdt.day,pdt.hour)
										hourly_fcst[tkey] = stn_dict[requested_var][dkey][h]/6.
	except:
		print_exception()
	return hourly_fcst

#------------


def get_hourly_data (native_id, requested_var, start_date_dt, end_date_dt, hourly_data, fcst_data, station_type='newa'):
	est_tsvars = {}
	dataForEst = {}
	datesForEst = {}
	vflagsForEst = {}
	if station_type == 'miwx' and len(native_id) == 3:
		orig_id = 'ew_%s' % native_id
	else:
		orig_id = native_id

	try:
#		start and end dates are provided in Local Time, adjust for DST if necessary
		start_date_dt = start_date_dt + DateTime.RelativeDate(hours=-start_date_dt.dst)
		end_date_dt = end_date_dt + DateTime.RelativeDate(hours=-end_date_dt.dst)
#		set for non-inclusive end date
		end_date_dt = end_date_dt + DateTime.RelativeDate(hours=+1)

#		setup necessary TSVars
		stn,station_name = get_metadata (native_id, station_type)
		if station_type == 'icao':
			stn = native_id.upper()
		temp0 = initHourlyVar (stn, requested_var, miss, station_type)

#		if dewpoint not directly available, estimate using rhum and previously obtained temp
		if requested_var == 'dwpt' and not temp0:
			temp0 = initHourlyVar (stn, 'rhum', miss, station_type)
			calc_dwpt = 1
		else:
			calc_dwpt = 0
		if requested_var == 'srad' and not temp0:
			dwpt0 = initHourlyVar (stn, 'dwpt', miss, station_type)
			tsky0 = initHourlyVar (stn, 'tsky', miss, station_type)
			stpr0 = initHourlyVar (stn, 'stpr', miss, station_type)
			wthr0 = initHourlyVar (stn, 'wthr', miss, station_type)
			visi0 = initHourlyVar (stn, 'visi', miss, station_type)
			ccnd0 = initHourlyVar (stn, 'ccnd', miss, station_type)
			chgt0 = initHourlyVar (stn, 'chgt', miss, station_type)
			ceil0 = initHourlyVar (stn, 'ceil', miss, station_type)
			calc_srad = 1
		else:
			calc_srad = 0
			if requested_var == 'srad' and (temp0.getUnits()).find('langley') < 0: 
				temp0.setUnits('langley/hour')
		
#	 	break entire period up into chunks no larger than 30-days
		start_period_dt = start_date_dt
		while start_period_dt < end_date_dt:
			end_period_dt = start_period_dt + DateTime.RelativeDate(days=+30)
			if end_period_dt > end_date_dt: end_period_dt = end_date_dt
#			convert dates to tuples for tsvar calls
			start_period = start_period_dt.tuple()[:4]
			end_period = end_period_dt.tuple()[:4]
			
#	 		get necessary hourly data for the period
			if calc_srad == 0:
				temp,temp_dates,temp_vflags = getHourlyVars(requested_var,temp0,start_period,end_period)
			else:
# 				here's where we use model to get srad
				temp_dates,temp = SOLAR_MAIN (stn,start_period,end_period,stpr0,wthr0,dwpt0,visi0,ccnd0,chgt0,ceil0,tsky0)

#			if no data, fill with missing to be estimated later
			if len(temp) == 0: temp,temp_dates,temp_vflags = fill_with_missing(start_period_dt,end_period_dt,miss)

#	 		process data hourly	
			hindx = 0
			while hindx < len(temp):
				theDate = DateTime.DateTime(*temp_dates[hindx])
				if theDate >= start_period_dt and theDate < end_period_dt:
					val = temp[hindx]
					val_eflag = ''
					# here's where we use rhum and temp to get dwpt
					if calc_dwpt == 1:
						theTempDate = theDate + DateTime.RelativeDate(hours=+theDate.dst)
						dateTuple = theTempDate.tuple()[:4]
						if val > 0 and hourly_data[dateTuple]['temp'][0] != miss:
							if val > 100: val = 100
							val = int(round(Base().calc_dewpoint(hourly_data[dateTuple]['temp'][0],val),0))
						else:
							val = miss					
					if val == miss:				# for missing values, do estimation based on surrounding hours
						if requested_var not in ['prcp','wdir','srad']:
							val = estmiss(temp,hindx,miss)
							val_eflag = 'I'
						if val == miss: 		# if still missing, use sister station
							val,est_tsvars,dataForEst,datesForEst,vflagsForEst = sister_est(orig_id,requested_var,temp_dates[hindx],end_period,est_tsvars,dataForEst, datesForEst, vflagsForEst,station_type)
##							if requested_var == 'srad' and station_type == 'newa' and val != miss:
##								val = val * 0.086		#newa stations are coming back in w/m2 here; convert to langleys
							val_eflag = 'S'
							if val == miss:		# if still missing, try forecast data (stored in local time already)
								theFcstDate = theDate + DateTime.RelativeDate(hours=+theDate.dst)
								dateTuple = theFcstDate.tuple()[:4]
								if fcst_data.has_key(dateTuple):
									val = fcst_data[dateTuple]
									val_eflag = 'F'
								if val == miss:
									val_eflag = 'M'
						
	#				save hourly data in local time
					lt_dt = theDate + DateTime.RelativeDate(hours=+theDate.dst)
					if not hourly_data.has_key((lt_dt.year,lt_dt.month,lt_dt.day,lt_dt.hour)):
						hourly_data[(lt_dt.year,lt_dt.month,lt_dt.day,lt_dt.hour)] = {}
					hourly_data[(lt_dt.year,lt_dt.month,lt_dt.day,lt_dt.hour)][requested_var] = (val,val_eflag)
				hindx = hindx+1
	
#			reset for start of next 30-day chunk
			start_period_dt = end_period_dt
	except DateMismatch, logmsg:
		sys.stdout.write('%s\n' % logmsg)		
		sys.exit(0)
	except:
		print_exception()
	
#	release TSVars		
	if temp0: 
		temp0.release()
	if calc_srad == 1:
		if dwpt0: dwpt0.release()
		if tsky0: tsky0.release()
		if stpr0: stpr0.release()
		if wthr0: wthr0.release()
		if visi0: visi0.release()
		if ccnd0: ccnd0.release()
		if chgt0: chgt0.release()
		if ceil0: ceil0.release()
	for key in est_tsvars.keys():
		if est_tsvars[key]['tsv']: est_tsvars[key]['tsv'].release()
	return hourly_data

#------------

def collect_hourly_input(native_id, start_date_dt, end_date_dt, vars, station_type="newa"):
	hourly_data = {}
	try:
		if station_type == 'miwx' and len(native_id) == 3:
			native_id = 'ew_%s' % native_id
		for requested_var in vars:
			# get forecast data
			fcst_data = get_fcst_data(native_id, requested_var, start_date_dt, end_date_dt)
			# build hourly data dictionary, filling with estimated and forecast data when obs not available
			hourly_data = get_hourly_data(native_id,requested_var,start_date_dt,end_date_dt,hourly_data,fcst_data,station_type)
	except:
		print_exception()	
	return hourly_data	

#--------------------------------------------------------------------------------------------		
class Base:
	# report no available data
	def nodata (self,stn, station_name, start_date_dt, end_date_dt):
		# try to provide additional information
		if sta_por.has_key(stn):
			bd,ed = sta_por[stn]
			spor_dt = DateTime.DateTime(int(bd[0:4]),int(bd[4:6]),int(bd[6:8]))
			if ed == '99991231':
				epor_dt = DateTime.now()
			else:
				epor_dt = DateTime.DateTime(int(ed[0:4]),int(ed[4:6]),int(ed[6:8]))
			if end_date_dt < spor_dt:
				addl_line = 'Data for %s starts %d/%d' % (station_name,spor_dt.month,spor_dt.year)
			elif start_date_dt > epor_dt:
				addl_line = 'Data for %s ends %d/%d' % (station_name,epor_dt.month,epor_dt.year)
			else:
				addl_line = None
		else:
			addl_line = None
		return newaCommon_io.nodata(addl_line)

	#--------------------------------------------------------------------------------------------
	# convert hour in 24-hour clock to 12-hour clock with am/pm
	def format_time (self,hr):
		ampm = ''
		try:
			if hr > 12:
				hr = hr-12
				ampm = 'PM'
			elif hr == 12:
				ampm = 'PM'
			elif hr == 0:
				hr = 12
				ampm = 'AM'
			else:
				ampm = 'AM'
		except:
			print_exception()
		return hr,ampm

	#--------------------------------------------------------------------------------------------		
	# obtain hourly data for station for time period
	def get_hourly (self, stn, start_date_dt, end_date_dt):
		hourly_data = []
		download_time = ''
		station_name = ''
		try:
			if stn[0:1] >= '1' and stn[0:1] <= '9' and stn[1:2] >= '0' and stn[1:2] <= '9':
				station_type = 'njwx'
			elif len(stn) == 4:
				station_type = 'icao'
			elif stn[0:3] == "cu_" or stn[0:3] == "um_" or stn[0:3] == "uc_" or stn[0:3] == "un_":
				station_type = 'cu_log'
			elif stn[0:3] == "ew_":
				stn = stn[3:]
				station_type = 'miwx'
			elif len(stn) == 3 or len(stn) == 6:
				station_type = 'newa'
			else:
				return newaCommon_io.errmsg('Error processing form; check station input')
	
			# get ucanid and station name from metadata
			ucanid,station_name = get_metadata (stn, station_type)
			if station_type == 'icao':
				staid = stn.upper()
			else:
				staid = ucanid
			
			# obtain all hourly data for station
			hourly_data,daily_data,avail_vars = get_newa_data (staid,stn,start_date_dt,end_date_dt,station_type)
			if len(hourly_data) > 0: 
				# save time of last hour downloaded
				download_time = hourly_data[-1][0]
		except:
			print_exception()
		return hourly_data, download_time, station_name

	#--------------------------------------------------------------------------------------------		
	# obtain hourly data for station for time period - same as get_hourly, except also returns avail_vars
	def get_hourly2 (self, stn, start_date_dt, end_date_dt):
		hourly_data = []
		download_time = ''
		station_name = ''
		avail_vars = []
		try:
			if stn[0:1] >= '1' and stn[0:1] <= '9' and stn[1:2] >= '0' and stn[1:2] <= '9':
				station_type = 'njwx'
			elif len(stn) == 4:
				station_type = 'icao'
			elif stn[0:3] == "cu_" or stn[0:3] == "um_" or stn[0:3] == "uc_" or stn[0:3] == "un_":
				station_type = 'cu_log'
			elif stn[0:3] == "ew_":
				stn = stn[3:]
				station_type = 'miwx'
			elif len(stn) == 3 or len(stn) == 6:
				station_type = 'newa'
			else:
				return newaCommon_io.errmsg('Error processing form; check station input')
	
			# get ucanid and station name from metadata
			ucanid,station_name = get_metadata (stn, station_type)
			if station_type == 'icao':
				staid = stn.upper()
			else:
				staid = ucanid
			
			# obtain all hourly data for station
			hourly_data,daily_data,avail_vars = get_newa_data (staid,stn,start_date_dt,end_date_dt,station_type)
			if len(hourly_data) > 0: 
				# save time of last hour downloaded
				download_time = hourly_data[-1][0]
		except:
			print_exception()
		return hourly_data, download_time, station_name, avail_vars

	#--------------------------------------------------------------------------------------------		
	# obtain daily data for station for time period
	def get_daily (self, stn, start_date_dt, end_date_dt):
		daily_data = []
		station_name = ''
		try:
			if stn[0:1] >= '1' and stn[0:1] <= '9' and stn[1:2] >= '0' and stn[1:2] <= '9':
				station_type = 'njwx'
			elif len(stn) == 4:
				station_type = 'icao'
			elif stn[0:3] == "cu_" or stn[0:3] == "um_" or stn[0:3] == "uc_" or stn[0:3] == "un_":
				station_type = 'cu_log'
			elif stn[0:3] == "ew_":
				stn = stn[3:]
				station_type = 'miwx'
			elif len(stn) == 3 or len(stn) == 6:
				station_type = 'newa'
			else:
				return newaCommon_io.errmsg('Error processing form; check station input')
	
			# get ucanid and station name from metadata
			ucanid,station_name = get_metadata (stn, station_type)
			if station_type == 'icao':
				staid = stn.upper()
			else:
				staid = ucanid
			
			# obtain all daily data for station
			hourly_data,daily_data,avail_vars = get_newa_data (staid,stn,start_date_dt,end_date_dt,station_type)
		except:
			print_exception()
		return daily_data, station_name

	#--------------------------------------------------------------------------------------------		
	# obtain hourly and daily data for station for time period
	def get_hddata (self, stn, start_date_dt, end_date_dt):
		hourly_data = []
		daily_date = []
		download_time = ''
		station_name = ''
		try:
			if stn[0:1] >= '1' and stn[0:1] <= '9' and stn[1:2] >= '0' and stn[1:2] <= '9':
				station_type = 'njwx'
			elif len(stn) == 4:
				station_type = 'icao'
			elif stn[0:3] == "cu_" or stn[0:3] == "um_" or stn[0:3] == "uc_" or stn[0:3] == "un_":
				station_type = 'cu_log'
			elif stn[0:3] == "ew_":
				stn = stn[3:]
				station_type = 'miwx'
			elif len(stn) == 3 or len(stn) == 6:
				station_type = 'newa'
			else:
				return newaCommon_io.errmsg('Error processing form; check station input')
	
			# get ucanid and station name from metadata
			ucanid,station_name = get_metadata (stn, station_type)
			if station_type == 'icao':
				staid = stn.upper()
			else:
				staid = ucanid
			
			# obtain all hourly data for station
			hourly_data,daily_data,avail_vars = get_newa_data (staid,stn,start_date_dt,end_date_dt,station_type)
			if len(hourly_data) > 0: 
				# save time of last hour downloaded
				download_time = hourly_data[-1][0]
		except:
			print_exception()
		return hourly_data, daily_data, download_time, station_name

	#--------------------------------------------------------------------------------------------		
	# obtain hourly and daily data for station for time period - same as get_hddata, except also returns avail_vars
	def get_hddata2 (self, stn, start_date_dt, end_date_dt):
		hourly_data = []
		daily_date = []
		download_time = ''
		station_name = ''
		try:
			if stn[0:1] >= '1' and stn[0:1] <= '9' and stn[1:2] >= '0' and stn[1:2] <= '9':
				station_type = 'njwx'
			elif len(stn) == 4:
				station_type = 'icao'
			elif stn[0:3] == "cu_" or stn[0:3] == "um_" or stn[0:3] == "uc_" or stn[0:3] == "un_":
				station_type = 'cu_log'
			elif stn[0:3] == "ew_":
				stn = stn[3:]
				station_type = 'miwx'
			elif len(stn) == 3 or len(stn) == 6:
				station_type = 'newa'
			else:
				return newaCommon_io.errmsg('Error processing form; check station input')
	
			# get ucanid and station name from metadata
			ucanid,station_name = get_metadata (stn, station_type)
			if station_type == 'icao':
				staid = stn.upper()
			else:
				staid = ucanid
			
			# obtain all hourly data for station
			hourly_data,daily_data,avail_vars = get_newa_data (staid,stn,start_date_dt,end_date_dt,station_type)
			if len(hourly_data) > 0: 
				# save time of last hour downloaded
				download_time = hourly_data[-1][0]
		except:
			print_exception()
		return hourly_data, daily_data, download_time, station_name, avail_vars

	#--------------------------------------------------------------------------------------------		
	# calculate daily degree day stats from daily values
	# vadd="accum" to make the last item in the tuple accumulate degday; vadd="prcp" and this is daily precip
	def degday_calcs (self,daily_data,start_date,end_date,smry_type,vadd="accum"):
		degday_data = []
		if vadd != "accum" and vadd != "prcp": vadd="accum"
		try:
			start_date = start_date + DateTime.RelativeDate(hour=0,minute=0,second=0)
			end_date = end_date + DateTime.RelativeDate(hour=23,minute=59,second=59)
			accum_degday = 0.
			for dly_dt,tave_hr,tmax,tmin,prcp,lwet,rhum,wspd,srad,st4a,st4x,st4n,dflags in daily_data:
				this_date = DateTime.DateTime(*dly_dt)
				if this_date >= start_date and this_date <= end_date:
					if tmax != miss and tmin != miss:
						if smry_type == 'dd4c':
							tave = (tmax+tmin)/2.
							tave_c = (5./9.) * (tave-32.)
							ddval = tave_c - 4.0
						elif smry_type == 'dd0c':
							tave = (tmax+tmin)/2.
							tave_c = (5./9.) * (tave-32.)
							ddval = tave_c - 0.0
						elif smry_type == 'dd143c':
							tave = (tmax+tmin)/2.
							tave_c = (5./9.) * (tave-32.)
							ddval = tave_c - 14.3
						elif smry_type == 'dd8650':
							if tmax > 86: 
								adjtmax = 86.
							else:
								adjtmax = tmax
							if tmin < 50: 
								adjtmin = 50.
							else:
								adjtmin = tmin
							tave = (adjtmax+adjtmin)/2.
							ddval = tave - 50.
						elif smry_type == 'dd43be' or smry_type == 'dd50be' or smry_type == 'dd55be':
							base = float(smry_type[2:4])
							if tmin >= base:
								tave = (tmax+tmin)/2.
								ddval = tave - base
							elif tmax <= base:
								ddval = 0.
							else:
								tave = (tmax + tmin) / 2.
								tamt = (tmax - tmin) / 2.
								t1 = math.sin((base-tave)/tamt)
								ddval = ((tamt*math.cos(t1))-((base-tave)*((3.14/2.)-t1)))/3.14
						else:
							try:
								base = int(smry_type[2:4])
								tave = (tmax+tmin)/2.
								ddval = tave - float(base)
							except:
								ddval = miss
		#				save values above zero and round
						if ddval > 0:
							ddval = round(ddval+.001,2)
						else:
							ddval = 0.
					else:
						ddval = miss
					if ddval != miss and accum_degday != miss: 
						accum_degday = accum_degday + ddval
					else:
						accum_degday = miss
		#			save values
					if vadd == "accum":
						degday_data.append((dly_dt,tmax,tmin,ddval,accum_degday))
					else:
						degday_data.append((dly_dt,tmax,tmin,ddval,prcp))
		except:
			print 'Error calculating degree days'
			print_exception()
		return degday_data

	#--------------------------------------------------------------------------------------------		
	# calculate dewpoint from temp and rh
	def calc_dewpoint(self,temp,rh):
		dewpt = miss
		try:
			if temp != miss and rh != miss and rh > 0:
				tempc = (5./9.)*(temp-32.)
				sat = 6.11*10.**(7.5*tempc/(237.7+tempc))
				vp = (rh*sat)/100.
				logvp = math.log(vp)
				dewptc = (-430.22+237.7*logvp)/(-logvp+19.08)
				dewpt = ((9./5.)*dewptc) + 32.
		except:
			print 'Bad data in dewpoint calculation:',temp,rh
			print_exception()
		return dewpt
