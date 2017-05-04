import Data, Meta
from mx import DateTime
from print_exception import print_exception
import ucanCallMethods

ucan = ucanCallMethods.general_ucan()

miss = -999

#--------------------------------------------------------------------------------------------	
def initHourlyVar (staid, station_type='newa'):
	majors = {'newa':23, 'icao':23, 'njwx':23, 'cu_log':126}
	v = None
	try:
		data = ucan.get_data()
		if station_type == 'icao':
			v = data.newTSVarNative(majors[station_type],0,staid)
		else:
			v = data.newTSVar(majors[station_type],0,staid)
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
def getHourlyVars (v, start_date, end_date, stn):
	values = []
	vdates = []
	if v:
		try:
			v.setDateRange (start_date,end_date)
			vdates = v.getDateArraySeq()
			values = v.getDataSeqAsFloat ()
		except Data.TSVar.UnavailableDateRange:
#			print 'unavailable data range',start_date,end_date
			pass
		except:
			print "Error processing:",stn,v,start_date,end_date
			print_exception()
	return values, vdates

#--------------------------------------------------------------------------------------------	
def get_metadata (station_id,id_type):
	ucanid = None
	try:
		query = ucan.get_query()
		r = query.getUcanFromIdAsSeq(station_id,id_type)
		query.release()
		if len(r) > 0: ucanid = r[-1].ucan_id
	except:
		pass
	return ucanid

#--------------------------------------------------------------------------------------------	
def get_downloadtime (stn,station_type):
	download_time_dt = miss
	try:
		if station_type == 'icao': 
			staid = stn.upper()
		else:
			if stn[0:3] == "ew_":
				stn = stn[3:]
			staid = get_metadata (stn, station_type)
			if not staid: 
				print 'Exiting get_downloadtime: Error retrieving metadata for',stn,station_type
				return download_time_dt
		end_date_dt = DateTime.now()
#		adjust for DST if necessary (don't worry about this for start_date)
		if end_date_dt.dst == 1: end_date_dt = end_date_dt + DateTime.RelativeDate(hours=-1)
		start_date_dt = end_date_dt + DateTime.RelativeDate(months=-12, hour=0, minute=0, second=0)
#		set for non-inclusive end date
		end_date_dt = end_date_dt + DateTime.RelativeDate(hours=+1)
#		setup TSVar
		temp0 = initHourlyVar (staid, station_type)		
#	 	make first chunk just 2 days, 30 days in successive calls
		start_period_dt = end_date_dt + DateTime.RelativeDate(days=-2)
		end_period_dt = end_date_dt
		while end_period_dt >= start_date_dt:
#			convert dates to tuples for tsvar calls
			start_period = start_period_dt.tuple()[:4]
			end_period = end_period_dt.tuple()[:4]
#	 		get necessary hourly data for the period
			temp,temp_dates = getHourlyVars(temp0,start_period,end_period,stn)
#	 		process data 
			if len(temp) > 0:
				for i in range(len(temp)-1,-1,-1):
					if temp[i] != miss:
						temp0.release()
						theDate = DateTime.DateTime(temp_dates[i][0],temp_dates[i][1],temp_dates[i][2],temp_dates[i][3])
						download_time_dt = theDate + DateTime.RelativeDate(hours=+theDate.dst)
						return download_time_dt
#			reset for previous 30-day chunk
			start_period_dt = start_period_dt + DateTime.RelativeDate(days=-30)
			end_period_dt = start_period_dt + DateTime.RelativeDate(days=+30)
	except:
		print_exception()
#	release TSVar	
	if temp0: temp0.release()
	return download_time_dt

#Tests
#for id,type in [('KALB','icao'),('gen','newa'),('cu_gfr','cu_log'),('pav','newa'),('xxx','newa'),('zzz','bogus')]:
#	result = get_downloadtime(id,type)
#	print 'Result for ',id,type,result