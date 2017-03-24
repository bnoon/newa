import sys, copy, Data
from mx import DateTime
from print_exception import print_exception
import ucanCallMethods

ucan = ucanCallMethods.general_ucan()

#--------------------------------------------------------------------------------------------	
def get_metadata (station_id,id_type):
	ucanid = None
	station_name = station_id
	query = ucan.get_query()
	try:
		r = query.getUcanFromIdAsSeq(station_id,id_type)
		if len(r) > 0:
			ucanid = r[-1].ucan_id
			info = query.getInfoForUcanIdAsSeq(ucanid,())
			fields = ucanCallMethods.NameAny_to_dict(info[-1].fields)
			station_name = fields['name']
		query.release()
	except:
		query.release()
		print_exception()
		raise
	return ucanid, station_name

#--------------------------------------------------------------------------------------------	
def initHourlyVar (staid, var, miss, station_type='newa'):
	var_dict = {'newa':  {'prcp': [5,6,  'inch','%.2f'],      'temp': [23,6, 'degF',   '%.1f'],
						  'lwet': [118,1,'',    '%3.0f'],     'rhum': [24,5, 'percent','%.1f'],
						  'wspd': [28,5, 'miles/hour','%.1f'],'srad': [119,1,'watt/m2','%.2f'],
						  'st4i': [120,1,'degF','%.1f'],
						  'st8i': [120,2,'degF','%.1f'] },
				'icao':  {'prcp': [5,3,  'inch','%.2f'],      'temp': [23,3, 'degF',   '%.0f'],
						                                      'rhum': [24,3, None,'%.0f'],
						  'wspd': [28,3, 'miles/hour','%.1f'],
						  'wdir': [27,3, 'degrees', '%.0f'],
						  'dwpt': [22,3,'degF',    '%4.0f'],  'tsky': [33,3,None,'%3.1f'] },
				'cu_log':{'prcp': [5,7,  'inch','%.2f'],      'temp': [126,1,'degF',   '%.1f'],
						                                      'rhum': [24,6, None,'%.0f'],
						  'wspd': [128,1,'miles/hour','%.1f'],'srad': [132,1,'langley','%.1f'],
						  'wdir': [130,1,'degrees','%.0f'],   'st4i': [121,265,'degF','%.1f'],
						  'st8i': [121,393,'degF','%.1f'] } }
	v = None
	miss_str = "%s" % miss
	if var_dict.has_key(station_type) and var_dict[station_type].has_key(var):
		major,minor,units,format = var_dict[station_type][var]
	else:
		return v
	try:
		data = ucan.get_data()
		if station_type == 'icao':
			v = data.newTSVarNative(major,0,staid)
		else:
			v = data.newTSVar(major,minor,staid)
		if units: v.setUnits (units)
		v.setMissingDataAsFloat(miss)
	except Data.TSVarFactory.UnknownUcanId:
#		print 'Unknown ucan id',var
		pass
	except:
#		print "Error initializing:",var
#		print_exception()
		pass
	return v

#--------------------------------------------------------------------------------------------	
def getHourlyVars (stn, var, v, start_date, end_date, miss):
	values = []
	vdates = []
	if v:
		try:
			v.setDateRange (start_date,end_date)
			vdates = v.getDateArraySeq()
			values = v.getDataSeqAsFloat ()
			values,vdates = trim_missing(values,vdates,miss)
		except Data.TSVar.UnavailableDateRange:
#			print 'unavailable data range',start_date,end_date
#			vldrange = v.getValidDateRange()
#			print 'valid date range',vldrange
			pass
		except:
#			print "Error processing:",var,start_date,end_date
			print_exception()
	return values, vdates

#--------------------------------------------------------------------------------------------		
def trim_missing (values,vdates,miss):
#	remove missing values at the end of the list
	try:
		for i in range(len(values)-1,-1,-1):
			if values[i] == miss:
				del values[i]
				del vdates[i]
			else:
				break
	except:
		print_exception()
	return values,vdates

#--------------------------------------------------------------------------------------------		
def get_hourly_data (stn,var,start_date_dt,end_date_dt,miss,station_type=None):
	obs_dict = {}
	try:
		if not station_type:
			if len(stn) == 3:
				station_type = 'newa'
			elif len(stn) == 4:
				station_type = 'icao'
			elif len(stn) == 6:
				station_type = 'cu_log'
			else:
				return obs_dict
				

#		get ucanid and station name from metadata
		ucanid,station_name = get_metadata (stn, station_type)
		if station_type == 'icao':
			stn = stn.upper()
		else:
			stn = ucanid
			
	
#		start and end dates are provided in Local Time, adjust for DST if necessary
		if start_date_dt.dst == 1:
			start_date_dt = start_date_dt + DateTime.RelativeDate(hours=-1)
		if end_date_dt.dst == 1:
			end_date_dt = end_date_dt + DateTime.RelativeDate(hours=-1)

#		set for non-inclusive end date
		end_date_dt = end_date_dt + DateTime.RelativeDate(hours=+1)
		
#		setup necessary TSVars
		tsv0 = initHourlyVar (stn, var, miss, station_type)
		
#	 	break entire period up into chunks no larger than 30-days
		start_period_dt = start_date_dt
		while start_period_dt < end_date_dt:
			end_period_dt = start_period_dt + DateTime.RelativeDate(days=+30)
			if end_period_dt > end_date_dt: end_period_dt = end_date_dt
#			convert dates to tuples for tsvar calls
			start_period = start_period_dt.tuple()[:4]
			end_period = end_period_dt.tuple()[:4]
			
#	 		get necessary hourly data for the period
			values,dates = getHourlyVars(stn,var,tsv0,start_period,end_period,miss)
			
#	 		save data in local time	
			for hindx in range(len(values)):
				theDate = DateTime.DateTime(*dates[hindx][:])
				lt_dt = theDate + DateTime.RelativeDate(hours=+theDate.dst)
				obs_dict[lt_dt.tuple()[:4]] = values[hindx]
	
#			reset for start of next 30-day chunk
			start_period_dt = end_period_dt
	except:
		print_exception()
	
#	release TSVars		
	if tsv0: tsv0.release()
	return obs_dict

