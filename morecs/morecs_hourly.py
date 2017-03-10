def initHourlyVar (stn, var, miss):
	import ucanCallMethods

	var_dict = {'prcp': [ 5,'inch',    '%4.2f'], 'temp': [23,'degF',      '%4.0f'],
				'dwpt': [22,'degF',    '%4.0f'], 'wspd': [28,'miles/hour','%4.1f'],
				'tsky': [33,'count',   '%3.1f'], 'stpr': [18,'inch_Hg',   '%6.3f'],
				'ceil': [35,'100 feet','%7.0f'], 'wthr': [20,'',       '%{abbr}s'],
				'ccnd': [30,'',     '%{abbr}s'], 'chgt': [31,'feet',      '%.0f '],
				'visi': [26,'miles',   '%5.2f'],
	           }

	miss_str = "%s" % miss
	major,units,format = var_dict[var]
	
	try:
		ucan = ucanCallMethods.general_ucan()
		data = ucan.get_data()
		v = data.newTSVarNative (major,0,stn)
		if units: v.setUnits (units)
		v.setDataStringFormat (format)
		v.setMissingDataAsString(miss_str)
		v.setMissingDataAsFloat(miss)
	except:
		print "Error initializing:",var
		list = ucanCallMethods.print_exception()
		for item in list: print item
		
	return (v)

#--------------------------------------------------------------------------------------------	
def getHourlyVars (stn, var, v, start_date, end_date):
	import string, Data
	from print_exception import print_exception

	values = []
	vdates = []
	
	try:
		v.setDateRange (start_date,end_date)
		vdates = v.getDateArraySeq()
		if var in ['wthr','ccnd','chgt']:
			values = v.getDataSeqAsAny ()
#		elif var == 'ceil':
#			values = v.getDataSeqAsString ()
		else:
			values = v.getDataSeqAsFloat ()
	except Data.TSVar.UnavailableDateRange:
		pass
	except:
		print "Error processing:",var
		print_exception()
				
	return (values, vdates)

#--------------------------------------------------------------------------------------------		
	
def getHourlySolar (stn, start_date, end_date, miss, stpr0, wthr0, dwpt0, visi0, ccnd0, chgt0, ceil0, tsky0):
	import string, Data
	from mx import DateTime
	from print_exception import print_exception
	from solar_main_routine import SOLAR_MAIN

	values = []
	vdates = []
	
	try:	
		srdates,srvalues = SOLAR_MAIN (stn,start_date,end_date,stpr0,wthr0,dwpt0,visi0,ccnd0,chgt0,ceil0,tsky0)
		
		start_date_dt = DateTime.DateTime(*start_date)
		end_date_dt   = DateTime.DateTime(*end_date)
		sr_start_dt   = DateTime.DateTime(*srdates[0])
		sr_end_dt     = DateTime.DateTime(*srdates[-1])

#		pad beginning, if necessary
		theDate = start_date_dt
		while theDate < sr_start_dt:
			vdates.append(theDate.tuple()[:4])
			values.append(miss)
			theDate = theDate + DateTime.RelativeDate(hours=+1)
#		only retain values in requested date range
		for vdy in range(len(srdates)):
			srdate_dt = DateTime.DateTime(*srdates[vdy])
			if srdate_dt >= start_date_dt and srdate_dt < end_date_dt:
				vdates.append(srdates[vdy])
#				convert from string to value
				values.append(string.atof(srvalues[vdy]))
#		pad end, if necessary
		theDate = sr_end_dt + DateTime.RelativeDate(hours=+1)
		while theDate < end_date_dt:
			vdates.append(theDate.tuple()[:4])
			values.append(miss)
			theDate = theDate + DateTime.RelativeDate(hours=+1)
	except:
		print_exception()	
				
	return (values, vdates)

#--------------------------------------------------------------------------------------------		
	
def estmiss (var,hindx,miss):
#	estimate missing values using average of previous and next good value within three hours.
 
	listlen = len(var)
	
	chk = hindx
	prev = miss
	while prev == miss:
		chk = chk-1
		if chk < hindx-3 or chk <0:
			break
		else:
			prev = var[chk]

	chk = hindx
	next = miss
	while next == miss:
		chk = chk+1
		if chk > hindx+3 or chk >= listlen:
			break
		else:
			next = var[chk]
			
	if next == miss:
		next = prev
	elif prev == miss:
		prev = next
		
	if next != miss and prev != miss:
		replacement = (next+prev)/2.
	else:
		replacement = miss
		
	return (replacement)
	
#--------------------------------------------------------------------------------------------		

def write_hourly_vars(theDate,tempv,dwptv,wspdv,tskyv,sradv,rain,evapo,snow,dly_evap,depth_hour,end_hour):
	import sys
	sys.stdout.write ('%02d/%02d/%4d %02d:' % (theDate.month,theDate.day,theDate.year,theDate.hour))
	sys.stdout.write (' %2d'   % tempv)
	sys.stdout.write (' %2d'   % dwptv)
	sys.stdout.write (' %4.1f' % wspdv)
	sys.stdout.write (' %3.1f' % tskyv)
	sys.stdout.write (' %5.1f' % sradv)
	sys.stdout.write (' %4.2f' % rain)
	sys.stdout.write (' %.3f'  % evapo)
	if theDate.hour == depth_hour: sys.stdout.write (' Snow_depth: %3d' % snow)
	if theDate.hour == end_hour: sys.stdout.write (' Daily_PET: %.2f' % dly_evap)
	sys.stdout.write ('\n')
	return
	
#--------------------------------------------------------------------------------------------		

def morecs_hourly (stn,backup,request_start_date,request_end_date,gtype,stype,end_hour,daily_ppt,hour_to_add,hour_for_depth):

	import string, sys
	from mx import DateTime

# 	necessary external routines
	from getDaily import getDaily
	from print_exception import print_exception
	from station_searches import getNearestCoop
	if '/Users/keith/progs/Morecs' not in sys.path: sys.path.insert(1,'/Users/keith/progs/Morecs')
	from et_model_all import etsoil_calc, getcropconst
	from stationInfo import stationInfo
	
#	dictionaries
	sc_status =     {'gtotal': 0.0, 'interception': 0.0, 'soil_x': 0.0, 'soil_y': 0.0, 
				     'crop_x': 0.0, 'crop_y': 0.0}
	sc_constants =  {'h_max': 0.0, 'h_min': 0.0, 'd_e': 0, 'd_f': 0, 'd_h': 0, 
					 'cp_albedo': 0.0, 'max_leaf': 0.0, 'surf_res': 0.0, 'water_cap': 0.0,
					 'soil_max': 0.0, 'crop_max': 0.0}
	loc_constants = {'lat': 42.0, 'long': 76.0, 'gmtoff': 5}
	
	miss = -999
	DateMismatch = "DateMismatch"
	BadRainList = "BadRainList"
	BadSnowList = "BadSnowList"
	NoSnowStation = "NoSnowStation"
	NoRainStation = "NoRainStation"
	ProblemDates = "ProblemDates"
	
	et_dict = {'dates': [], 'values':[] }
		
	try:
#	 	check for legal input
		if end_hour <= 1 or end_hour > 23:
			raise ProblemDates
		if daily_ppt and (hour_to_add == 1 or hour_to_add > 23):
			raise ProblemDates

#	 	convert requested start and end dates to DateTime format
		request_start_dt = DateTime.DateTime(*request_start_date)
		request_end_dt   = DateTime.DateTime(*request_end_date)

#		end date is exclusive. make it the hour after last hour needed for request
		end_date_dt = (request_end_dt + DateTime.RelativeDate(hour=end_hour)) + DateTime.RelativeDate(hours=+1)
		if end_date_dt.dst == 1: end_date_dt = end_date_dt + DateTime.RelativeDate(hours=-1)
		end_date    = end_date_dt.tuple()[:4]
		
#		must start 24 hours earlier then beginning of day, since first returned value is bogus
		start_date_dt = (request_start_dt + DateTime.RelativeDate(hour=end_hour)) + DateTime.RelativeDate(hours=-47)
		if start_date_dt.dst == 1: start_date_dt = start_date_dt + DateTime.RelativeDate(hours=-1)
		start_date    = start_date_dt.tuple()[:4]		

#		class for retrieving and storing station information
		sinf = stationInfo()

#	 	get station information (name, latitude, longitude, gmt offset)
		lat = sinf.getvar(stn, 'lat')
		loc_constants['lat'] = lat
		lon = sinf.getvar(stn, 'lon')
		loc_constants['long'] = lon * -1.
		gmtoff = sinf.getvar(stn, 'gmt_offset')
		loc_constants['gmtoff'] = gmtoff
		sys.stdout.write ('Station: %s\n' % sinf.getvar(stn, 'name'))
			
#		assume no snow June-October
		if start_date_dt.year == end_date_dt.year and start_date_dt.month >= 6 and end_date_dt.month <= 9:
			coopid = -1
			sinf.setvar(stn, 'snow_station', coopid)
		else:
#	 		find the closest station observing snow cover and get data
			coopid = sinf.getvar(stn, 'snow_station')
			if coopid == None:
				varmajor = 11
				detailed_check = 1
				coopid = getNearestCoop (lat, lon, varmajor, start_date, end_date, detailed_check)
				sinf.setvar(stn, 'snow_station', coopid)
			
		if coopid != -1:
			sys.stdout.write ('Coop station for snow cover: %s\n' % (coopid))
			varmajor = 11
			grd_dict = getDaily(start_date, end_date, varmajor, coopid)
		else:
#			no nearby station, fill the dictionary with zeros
			sys.stdout.write ('Coop station for snow cover: none available\n')
			sdt_list = []
			svl_list = []
			filldate = start_date_dt
			while filldate <= end_date_dt + DateTime.RelativeDate(hours=+1):
				sdt_list.append([filldate.year,filldate.month,filldate.day])
				svl_list.append(0.0)
				filldate = filldate + DateTime.RelativeDate(days=+1)
			grd_dict = {}
			grd_dict['dates'] = sdt_list
			grd_dict['values'] = svl_list
			
#		initial snow depth
		todindx = 0
		snow = grd_dict['values'][todindx]

#	 	if using daily precip, find closest station and get data
		if daily_ppt:
			varmajor = 4
			detailed_check = 1
			coopid = getNearestCoop (lat, lon, varmajor, start_date, end_date, detailed_check)
			if coopid != -1:
				sys.stdout.write ('Coop station for daily precip: %s\n' % (coopid))
				ppt_dict = getDaily(start_date, end_date, varmajor, coopid)
			else:
				ppt_dict = {}
				sys.stdout.write('No daily precip station found; assuming zero ...\n')
				
#	 	get crop constants
		getcropconst (gtype, stype, sc_constants)
	
#	 	Initialize to just having crop_y filled
		sc_status['crop_y'] = 0.6 * (sc_constants['water_cap'] - ((stype+2)*5.))
	
#		initialize daily evap accumulation
		dly_evap = 0.0
		dly_miss = 0
		
#		setup necessary TSVars
		temp0 = initHourlyVar (stn, 'temp', miss)
		dwpt0 = initHourlyVar (stn, 'dwpt', miss)
		wspd0 = initHourlyVar (stn, 'wspd', miss)
		tsky0 = initHourlyVar (stn, 'tsky', miss)
		if not daily_ppt: 
			prcp0 = initHourlyVar (stn, 'prcp', miss)
		else:
			prcp0 = None
#		solar rad TSVars
		stpr0 = initHourlyVar (stn, 'stpr', miss)
		wthr0 = initHourlyVar (stn, 'wthr', miss)
		visi0 = initHourlyVar (stn, 'visi', miss)
		ccnd0 = initHourlyVar (stn, 'ccnd', miss)
		chgt0 = initHourlyVar (stn, 'chgt', miss)
		ceil0 = initHourlyVar (stn, 'ceil', miss)

#		will initialize for backup station if/when needed
		temp0_bckp = None
		dwpt0_bckp = None
		wspd0_bckp = None
		tsky0_bckp = None
		stpr0_bckp = None
		wthr0_bckp = None
		visi0_bckp = None
		ccnd0_bckp = None
		chgt0_bckp = None
		ceil0_bckp = None
		
		est_from_hrs = {}
		est_from_bckp = {}
		no_est = {}
		for tv in ['temp','dwpt','wspd','srad']:
			est_from_hrs[tv] = 0
			est_from_bckp[tv] = 0
			no_est[tv] = 0
	
#	 	break entire period up into chunks no larger than 30-days
		start_period_dt = start_date_dt
		while start_period_dt < end_date_dt:
			end_period_dt = start_period_dt + DateTime.RelativeDate(days=+30)
			if end_period_dt > end_date_dt: end_period_dt = end_date_dt
			
#			convert dates to tuples for tsvar calls
			start_period = start_period_dt.tuple()[:4]
			end_period = end_period_dt.tuple()[:4]
			
#	 		get necessary hourly data for the period
			temp,temp_dates = getHourlyVars(stn,'temp',temp0,start_period,end_period)
			dwpt,dwpt_dates = getHourlyVars(stn,'dwpt',dwpt0,start_period,end_period)
			wspd,wspd_dates = getHourlyVars(stn,'wspd',wspd0,start_period,end_period)
			tsky,tsky_dates = getHourlyVars(stn,'tsky',tsky0,start_period,end_period)
			srad,srad_dates = getHourlySolar(stn,start_period,end_period,miss,stpr0,wthr0,dwpt0,visi0,ccnd0,chgt0,ceil0,tsky0)
			if not daily_ppt: prcp,prcp_dates = getHourlyVars(stn,'prcp',prcp0,start_period,end_period)

#	 		check beginning dates of all lists
			if start_period_dt != DateTime.DateTime(*srad_dates[0]):
				sys.stdout.write ('Start of srad data (%s) does not match requested start date!\n' % srad_dates[0])
				raise DateMismatch
			if start_period_dt != DateTime.DateTime(*temp_dates[0]):
				sys.stdout.write ('Start of temp data does not match requested start date!\n')
				raise DateMismatch
			if start_period_dt != DateTime.DateTime(*dwpt_dates[0]):
				sys.stdout.write ('Start of dwpt data does not match requested start date!\n')
				raise DateMismatch
			if start_period_dt != DateTime.DateTime(*wspd_dates[0]):
				sys.stdout.write ('Start of wspd data does not match requested start date!\n')
				raise DateMismatch
			if start_period_dt != DateTime.DateTime(*tsky_dates[0]):
				sys.stdout.write ('Start of tsky data does not match requested start date!\n')
				raise DateMismatch
			if not daily_ppt:
				if start_period_dt != DateTime.DateTime(*prcp_dates[0]):
					sys.stdout.write ('Start of prcp data does not match requested start date!\n')
					raise DateMismatch
		
#	 		process data hourly	
			theDate = start_period_dt
			hindx = 0
			while theDate < end_period_dt:
#				adjust hour_to_add and end_hour if we're in DST			
				if theDate.dst == 1: 
					lt_hr_to_add = hour_to_add - 1
					lt_end_hour = end_hour - 1
				else:
					lt_hr_to_add = hour_to_add
					lt_end_hour = end_hour
					
#				get correct precip value (daily or hourly)
				if daily_ppt:
					if theDate.hour == lt_hr_to_add:
						try:
							todindx = ppt_dict['dates'].index([theDate.year,theDate.month,theDate.day])
							rain = ppt_dict['values'][todindx]
						except:
							rain = 0.0
							sys.stdout.write ('   ... bad rain list; assuming zero.\n')
					else:
						rain = 0.0
				else:
					rain = prcp[hindx]
		
#				set missing precip to zero
				if rain == miss: rain = 0.00
	
#				get daily snow depth
				if theDate.hour == hour_for_depth:
					try:
						todindx = grd_dict['dates'].index([theDate.year,theDate.month,theDate.day])
						snow = grd_dict['values'][todindx]
#						deal with missing snow depth
						if snow == miss: 
#							replacement is yesterday's snow depth ...
							if todindx != 0 and grd_dict['values'][todindx-1] != miss:
								snow = grd_dict['values'][todindx-1]
							else:
#								.. if not available, zero
								snow = 0
					except:
						raise BadSnowList
										
#				for missing hourly variables, do estimation based on surrounding hours
				tempv = temp[hindx]
				if  tempv < -150 or tempv > 150:
					tempv = miss
				if tempv == miss:
					tempv = estmiss(temp,hindx,miss)
					if  tempv < -150 or tempv > 150:
						tempv = miss
					if tempv != miss:
						est_from_hrs['temp'] = est_from_hrs['temp'] + 1
##					print theDate.tuple()[:4],"temp replacement:",tempv
				dwptv = dwpt[hindx]
				if dwptv == miss:
					dwptv = estmiss(dwpt,hindx,miss)
					if dwptv != miss:
						est_from_hrs['dwpt'] = est_from_hrs['dwpt'] + 1
##					print theDate.tuple()[:4],"dwpt replacement:",dwptv
				wspdv = wspd[hindx]
				if wspdv == miss:
					wspdv = estmiss(wspd,hindx,miss)
					if wspdv != miss:
						est_from_hrs['wspd'] = est_from_hrs['wspd'] + 1
##					print theDate.tuple()[:4],"wspd replacement:",wspdv
				tskyv = tsky[hindx]
				if tskyv == miss: 
					tskyv = estmiss(tsky,hindx,miss)
##					print theDate.tuple()[:4],"tsky replacement:",tskyv
#				always use backup station - srad is too time dependent to average adjacent hours
				sradv = srad[hindx]
					
#				if data are still missing, look to backup station
				if tempv == miss or dwptv == miss or wspdv == miss or tskyv == miss or sradv == miss:
					bsd = theDate.tuple()[:4]
					bed = (theDate+DateTime.RelativeDate(hours=+1)).tuple()[:4]
					
					if tempv == miss or dwptv == miss:
						if temp0_bckp == None: temp0_bckp = initHourlyVar (backup, 'temp', miss)
						btemp,dts = getHourlyVars(backup,'temp',temp0_bckp,bsd,bed)
						if btemp != []: tempv = btemp[0]
						if tempv != miss:
							est_from_bckp['temp'] = est_from_bckp['temp'] + 1
						else:
							no_est['temp'] = no_est['temp'] + 1
##						print theDate.tuple()[:4],"temp for backup:",tempv
						if dwpt0_bckp == None: dwpt0_bckp = initHourlyVar (backup, 'dwpt', miss)
						bdwpt,dts = getHourlyVars(backup,'dwpt',dwpt0_bckp,bsd,bed)
						if bdwpt != []: dwptv = bdwpt[0]
						if dwptv != miss:
							est_from_bckp['dwpt'] = est_from_bckp['dwpt'] + 1
						else:
							no_est['dwpt'] = no_est['dwpt'] + 1
##						print theDate.tuple()[:4],"dwpt for backup:",dwptv
					if wspdv == miss:
						if wspd0_bckp == None: wspd0_bckp = initHourlyVar (backup, 'wspd', miss)
						bwspd,dts = getHourlyVars(backup,'wspd',wspd0_bckp,bsd,bed)
						if bwspd != []: wspdv = bwspd[0]
						if wspdv != miss:
							est_from_bckp['wspd'] = est_from_bckp['wspd'] + 1
						else:
							no_est['wspd'] = no_est['wspd'] + 1
##						print theDate.tuple()[:4],"wspd for backup:",wspdv
					if tskyv == miss:
						if tsky0_bckp == None: tsky0_bckp = initHourlyVar (backup, 'tsky', miss)
						btsky,dts = getHourlyVars(backup,'tsky',tsky0_bckp,bsd,bed)
						if btsky != []: tskyv = btsky[0]
##						print theDate.tuple()[:4],"tsky for backup:",tskyv
					if sradv == miss:
						if stpr0_bckp == None: stpr0_bckp = initHourlyVar (backup, 'stpr', miss)
						if wthr0_bckp == None: wthr0_bckp = initHourlyVar (backup, 'wthr', miss)
						if dwpt0_bckp == None: dwpt0_bckp = initHourlyVar (backup, 'dwpt', miss)
						if visi0_bckp == None: visi0_bckp = initHourlyVar (backup, 'visi', miss)
						if ccnd0_bckp == None: ccnd0_bckp = initHourlyVar (backup, 'ccnd', miss)
						if chgt0_bckp == None: chgt0_bckp = initHourlyVar (backup, 'chgt', miss)
						if ceil0_bckp == None: ceil0_bckp = initHourlyVar (backup, 'ceil', miss)
						if tsky0_bckp == None: tsky0_bckp = initHourlyVar (backup, 'tsky', miss)
						bsrad,dts = getHourlySolar(backup,bsd,bed,miss,stpr0_bckp,wthr0_bckp,dwpt0_bckp,visi0_bckp,ccnd0_bckp,chgt0_bckp,ceil0_bckp,tsky0_bckp)
						if bsrad != []: sradv = bsrad[0]
						if sradv != miss:
							est_from_bckp['srad'] = est_from_bckp['srad'] + 1
						else:
							no_est['srad'] = no_est['srad'] + 1
##						print theDate.tuple()[:4],"srad for backup:",sradv
	
#				final checks
				if dwptv > tempv: dwptv = tempv
				if tskyv == miss: tskyv = 0.5
		
#				do hourly et calculations
				evapo = etsoil_calc (gtype,stype,theDate.month,theDate.day,theDate.hour, \
				        tempv,dwptv,wspdv,rain,sradv,tskyv,snow,daily_ppt, \
						loc_constants,sc_status,sc_constants)
	
#				accumulate hourly values for day
				if evapo != miss:
					dly_evap = dly_evap + evapo
				else:
					dly_miss = dly_miss + 1
	
##				display hourly input variables and et values
##				write_hourly_vars(theDate,tempv,dwptv,wspdv,tskyv,sradv,rain,evapo,snow,dly_evap,hour_for_depth,lt_end_hour)
			
#				end of "day" update
				if theDate.hour == lt_end_hour:
#					save daily et values
					if theDate >= request_start_dt:
						if dly_miss > 1:
							et_dict['values'].append(miss)
						else:
							et_dict['values'].append(dly_evap)
						et_dict['dates'].append((theDate.year,theDate.month,theDate.day))
#					soil moisture
#					soil_moist = (sc_status['soil_x']+sc_status['soil_x']+sc_status['crop_x']+sc_status['crop_y'])/25.4
#					reset daily accumulater
					dly_evap = 0.0
					dly_miss = 0
					
					if (theDate.month == 12 and theDate.day == 31):
						sys.stdout.write ('%d:\n' % theDate.year)
						for tv in ['temp','dwpt','wspd','srad']:
							if tv == 'srad': est_from_hrs[tv] = '-'
							sys.stdout.write ('   %s %5s %5d %5d\n' % (tv,est_from_hrs[tv],est_from_bckp[tv],no_est[tv]))
							est_from_hrs[tv] = 0
							est_from_bckp[tv] = 0
							no_est[tv] = 0
	
				theDate = theDate + DateTime.RelativeDate(hours=+1)
				hindx = hindx+1
	
#	 		check ending dates of lists to make sure we ended where we think we did
			lastDate = theDate + DateTime.RelativeDate(hours=-1)
			if lastDate != DateTime.DateTime(*srad_dates[hindx-1]):
				sys.stdout.write ('Date of last srad value does not match expected end date!\n')
				raise DateMismatch
			if lastDate != DateTime.DateTime(*temp_dates[hindx-1]):
				sys.stdout.write ('Date of last temp value does not match expected end date!\n')
				raise DateMismatch
			if lastDate != DateTime.DateTime(*dwpt_dates[hindx-1]):
				sys.stdout.write ('Date of last dwpt value does not match expected end date!\n')
				raise DateMismatch
			if lastDate != DateTime.DateTime(*wspd_dates[hindx-1]):
				sys.stdout.write ('Date of last wspd value does not match expected end date!\n')
				raise DateMismatch
			if lastDate != DateTime.DateTime(*tsky_dates[hindx-1]):
				sys.stdout.write ('Date of last tsky value does not match expected end date!\n')
				raise DateMismatch
			if not daily_ppt:
				if lastDate != DateTime.DateTime(*prcp_dates[hindx-1]):
					sys.stdout.write ('Date of last prcp value does not match expected end date!\n')
					raise DateMismatch
		
#			reset for start of next 30-day chunk
			start_period_dt = end_period_dt
			
		if (theDate.month != 12 or theDate.day != 31):
			sys.stdout.write ('%s\n' % theDate)
			for tv in ['temp','dwpt','wspd','srad']:
				if tv == 'srad': est_from_hrs[tv] = '-'
				sys.stdout.write ('   %s %5s %5d %5d\n' % (tv,est_from_hrs[tv],est_from_bckp[tv],no_est[tv]))
			
	except NoRainStation:
		sys.stdout.write('No daily precip station found; exiting...\n')
	except NoSnowStation:
		sys.stdout.write('No daily snow depth station found; exiting...\n')
	except DateMismatch:
		sys.stdout.write('Date mismatch exception; exiting...\n')
	except BadRainList:
		sys.stdout.write('Bad daily rainfall list; exiting...\n')
		print 'ppt_dict:',ppt_dict
	except BadSnowList:
		sys.stdout.write('Bad daily snow depth list; exiting...\n')
		print 'grd_dict:',grd_dict
	except ProblemDates:
		sys.stdout.write('Bad input: end_hour and hour_to_add must be between 3 and 23; exiting...n')
	except:
		print_exception()
	
#	release TSVars		
	if temp0: temp0.release()
	if dwpt0: dwpt0.release()
	if wspd0: wspd0.release()
	if tsky0: tsky0.release()
	if prcp0: prcp0.release()
	if stpr0: stpr0.release()
	if wthr0: wthr0.release()
	if visi0: visi0.release()
	if ccnd0: ccnd0.release()
	if chgt0: chgt0.release()
	if ceil0: ceil0.release()
	
#	TSVars for backups, if used
	if temp0_bckp: temp0_bckp.release()
	if dwpt0_bckp: dwpt0_bckp.release()
	if wspd0_bckp: wspd0_bckp.release()
	if tsky0_bckp: tsky0_bckp.release()
	if stpr0_bckp: stpr0_bckp.release()
	if wthr0_bckp: wthr0_bckp.release()
	if visi0_bckp: visi0_bckp.release()
	if ccnd0_bckp: ccnd0_bckp.release()
	if chgt0_bckp: chgt0_bckp.release()
	if ceil0_bckp: ceil0_bckp.release()

	return (et_dict)