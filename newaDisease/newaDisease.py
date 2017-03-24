#!/usr/local/bin/python

import sys, copy, math
from mx import DateTime
from print_exception import print_exception
import newaDisease_io
from newa_simcast import *
from newaCommon import newaCommon_io
from newaCommon.newaCommon import *

miss = -999
month_names = ["","January","February","March","April","May","June","July","August","September","October","November","December"]

class program_exit (Exception):
	pass

# add hourly forecast data to end of hourly_data
def add_hrly_fcst(stn,hourly_data,start_fcst_dt,end_fcst_dt,estp=False):
	try:
		if (estp):
			from ndfd.get_hourly_forecast_estp import get_hourly_forecast_estp
			forecast_data = get_hourly_forecast_estp(stn,start_fcst_dt,end_fcst_dt)		
		else:
			from ndfd.get_hourly_forecast import get_hourly_forecast
			forecast_data = get_hourly_forecast(stn,start_fcst_dt,end_fcst_dt)		
		hourly_data = hourly_data+forecast_data
	except:
		print_exception()
	return hourly_data	

#--------------------------------------------------------------------------------------------		
# add daily forecast data to end of daily_data
def add_dly_fcst(stn,daily_data,start_fcst_dt,end_fcst_dt):
	try:
		from ndfd.get_daily_forecast import get_daily_forecast
		forecast_data = get_daily_forecast(stn,start_fcst_dt,end_fcst_dt)
		daily_data = daily_data+forecast_data
	except:
		print_exception()
	return daily_data	

#--------------------------------------------------------------------------------------------		
def hrly_to_dly (hourly_data, lt_end_hour = 23):
	daily_data = []
	miss=-999
	try:		
#		init counters
		temp_sum = 0.
		temp_cnt = 0.
		temp_max = -9999.
		temp_min = 9999.
		prcp_sum = 0.
		prcp_cnt = 0.
		qpf_sum = 0.
		qpf_cnt = 0.
		pop12_list = []
		rhum_sum = 0.
		rhum_cnt = 0.
		temp_dflag = ''
		prcp_dflag = ''
		pop12_dflag = ''
		rhum_dflag = ''
		qpf_dflag = ''
		wdir_dflag = ''
		srad_dflag = ''
		st4i_dflag = ''
			
		for theTime,tempv,prcpv,pop12v,rhumv,miss,miss,miss,miss,eflags in hourly_data:
			temp_eflag, prcp_eflag, pop12_eflag, rhum_eflag, wspd_eflag, wdir_eflag, srad_eflag, st4i_eflag = eflags
			theDate = DateTime.DateTime(*theTime)

#			do calculations for daily data
			if tempv != miss:
				temp_sum = temp_sum + tempv
				if tempv > temp_max: temp_max = copy.deepcopy(tempv)
				if tempv < temp_min: temp_min = copy.deepcopy(tempv)
				temp_cnt = temp_cnt + 1
				if temp_eflag in ['S','I','F']: temp_dflag = 'E'
			if prcpv != miss:
				prcp_sum = prcp_sum + prcpv
				prcp_cnt = prcp_cnt + 1
				if prcp_eflag != "P":
					qpf_sum = qpf_sum + prcpv
					qpf_cnt = qpf_cnt + 1
				if prcp_eflag in ['S','I','F']:
					prcp_dflag = 'E'
					qpf_dflag = 'E'
			if pop12v != miss:
				pop12_list.append((theDate.hour,int(pop12v)))
				if pop12_eflag in ['S','I','F']: pop12_dflag = 'E'
			if rhumv != miss:
				if rhumv >= 90: rhum_sum = rhum_sum + 1
				rhum_cnt = rhum_cnt + 1
				if rhum_eflag in ['S','I','F']: rhum_dflag = 'E'
			
#			end of "day" update
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
				if qpf_cnt > 0:
					dly_qpf_tot = qpf_sum
				else:
					dly_qpf_tot = miss
				if len(pop12_list) > 0:
					dly_pop12 = pop12_list
				else:
					dly_pop12 = []
				if rhum_cnt > 0:
					dly_rhum_hrs = rhum_sum
				else:
					dly_rhum_hrs = miss
				
#				save daily data
				if day_diff == 0:
					ddt = theDate
				else:
					ddt = theDate + DateTime.RelativeDate(days=day_diff)
				dflags = (temp_dflag, prcp_dflag, pop12_dflag, rhum_dflag, qpf_dflag, wdir_dflag, srad_dflag, st4i_dflag)
				daily_data.append(([ddt.year,ddt.month,ddt.day], 
						 dly_temp_ave, dly_temp_max, dly_temp_min, dly_prcp_tot, dly_pop12, \
						 dly_rhum_hrs, miss, miss, dly_qpf_tot, miss, \
						 miss, dflags))
				
				temp_sum = 0.
				temp_cnt = 0.
				temp_max = -9999.
				temp_min = 9999.
				prcp_sum = 0.
				prcp_cnt = 0.
				qpf_sum = 0.
				qpf_cnt = 0.
				pop12_list = []
				rhum_sum = 0.
				rhum_cnt = 0.
				temp_dflag = ''
				prcp_dflag = ''
				pop12_dflag = ''
				rhum_dflag = ''
				qpf_dflag = ''
				wdir_dflag = ''
				srad_dflag = ''
				st4i_dflag = ''
	except:
		print_exception()

	return daily_data

#--------------------------------------------------------------------------------------------		
# routines used by both new potato and new tomato disease models
class Pottom (Base, general_simcast):
	# find last value precip amount		
	def getLastPrecip(self, hourly_data):
		last_pcpn = None
		for theTime,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags in hourly_data:
			if prcp != miss:
				last_pcpn = theTime
		return last_pcpn
		
	#--------------------------------------------------------------------------------------------				
	# determine severity unit value
	def get_severity(self,wet_hrs,temp_ave,cold_hrs,continuation):
		wet_hrs = wet_hrs - cold_hrs
		severity = miss
		try:
			itemp = round(temp_ave,0)
			if itemp < 46:
				return 0
			elif itemp > 85:
				return miss
			if (continuation):
				if itemp >= 46 and itemp <= 53:
					severity = int((wet_hrs+9)/9)
				elif itemp >= 54 and itemp <= 59:
					severity = int((wet_hrs+5)/6)
				elif itemp >= 60 and itemp <= 85:
					if wet_hrs == 21: 
						severity = 5	#doesn't fit formula
					else:
						severity = int((wet_hrs+3)/5)
			else:
				if itemp >= 46 and itemp <= 53:
					severity = int((wet_hrs-13)/3)
				elif itemp >= 54 and itemp <= 59:
					severity = int((wet_hrs-10)/3)
				elif itemp >= 60 and itemp <= 85:
					if wet_hrs == 22 or wet_hrs == 23: 
						severity = 4	#doesn't fit formula
					else:
						severity = int((wet_hrs-7)/3)
			if severity < 0: severity = 0
		except:
			print_exception()
		return severity

	#--------------------------------------------------------------------------------------------		
	# determine wet and dry periods from hourly data provided 
	def get_wetting_rh (self,hourly_data,stn):
		wet_periods = []
		try:
			wet_hrs = 0
			cold_hrs = 0
			temp_sum = 0.
			temp_cnt = 0.
			prcp_sum = 0.
			prcp_cnt = 0.
			severity_sum = 0.
			date_sev = []
			for theTime,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags in hourly_data:
				# Adjust relative humidity for icao stations and forecast data
				if (eflags[3] == "F" or (len(stn) == 4 and stn[0:1].upper() == 'K')) and rhum != miss:
#					rhum = rhum/(rhum*0.0047+0.53)						 replaced with following to match Laura - 8/25/2011 kle
					rhum = min(100,rhum+15)
				if (rhum < 90 and wet_hrs > 0) or wet_hrs-cold_hrs == 24:
					#end wetting period ...
					wet_end = theTime
					if temp_cnt > 0:
						temp_ave = temp_sum/temp_cnt
					else:
						temp_ave = miss
					if prcp_cnt > 0:
						prcp_tot = prcp_sum
					else:
						prcp_tot = miss
					if len(wet_periods) > 0 and wet_start == wet_periods[-1][1]:
						continuation = 1
					else:
						continuation = 0
					severity = self.get_severity(wet_hrs,temp_ave,cold_hrs,continuation)
					wet_end_dt = DateTime.DateTime(wet_end[0],wet_end[1],wet_end[2],wet_end[3])
					if severity != miss: 
						severity_sum = severity_sum + severity
						date_sev.append((wet_end_dt,severity))
					else:
						severity = 'n/a'
					severity_week = 0.
					for i in range(len(date_sev)-1,-1,-1):
						ldt,lsev = date_sev[i]
						if (wet_end_dt-ldt).days > 7:
							break
						else:
							severity_week = severity_week+lsev
					wet_periods.append((wet_start,wet_end,wet_hrs,cold_hrs,temp_ave,prcp_tot,severity,severity_week,severity_sum))
					wet_hrs = 0
					cold_hrs = 0
					temp_sum = 0.
					temp_cnt = 0.
					prcp_sum = 0.
					prcp_cnt = 0.					
				if rhum >= 90:
					wet_hrs = wet_hrs + 1
					if wet_hrs == 1: 
						wet_start = theTime
					if temp != miss:
						if temp >= 46:
							temp_sum = temp_sum + temp
							temp_cnt = temp_cnt + 1
						else:
							cold_hrs = cold_hrs + 1
					if prcp != miss:
						prcp_sum = prcp_sum + prcp
						prcp_cnt = prcp_cnt + 1
	#		end period in progress
			if wet_hrs > 0:
				wet_end = theTime
				if temp_cnt > 0:
					temp_ave = temp_sum/temp_cnt
				else:
					temp_ave = miss
				if prcp_cnt > 0:
					prcp_tot = prcp_sum
				else:
					prcp_tot = miss
				if len(wet_periods) > 0 and wet_start == wet_periods[-1][1]:
					continuation = 1
				else:
					continuation = 0
				severity = self.get_severity(wet_hrs,temp_ave,cold_hrs,continuation)
				wet_end_dt = DateTime.DateTime(theTime[0],theTime[1],theTime[2],theTime[3])
				if severity != miss: 
					severity_sum = severity_sum + severity
					date_sev.append((wet_end_dt,severity))
				else:
					severity = 'n/a'
				severity_week = 0.
				for i in range(len(date_sev)-1,-1,-1):
					ldt,lsev = date_sev[i]
					if (wet_end_dt-ldt).days > 7:
						break
					else:
						severity_week = severity_week+lsev
				wet_periods.append((wet_start,wet_end,wet_hrs,cold_hrs,temp_ave,prcp_tot,severity,severity_week,severity_sum))
		except:
			print_exception()
		return wet_periods

	#--------------------------------------------------------------------------------------------		
	# convert from wet periods to values for each of current and next 6 days		
	def get_daily_accum(self, wet_data_short, end_date_dt, last_hour):
		daily_vals = {}
		last_hour_dt = DateTime.DateTime(*last_hour)
		for dy in range(-1, 7):
			eval_dt = end_date_dt + DateTime.RelativeDate(days=+dy, hour=12, minute=0, second=0)
			fd = '%02d/%02d' % (eval_dt.month, eval_dt.day)
			if eval_dt > last_hour_dt:
				daily_vals[fd] = 'NA'
				continue
			last_val = 0
			for ws_dt, we_dt, val in wet_data_short:
				if eval_dt < ws_dt:
					daily_vals[fd] = last_val
					break
				elif eval_dt > ws_dt and eval_dt < we_dt:
					daily_vals[fd] = '%d*'%val		# in progress
					break
				elif eval_dt == we_dt:
					daily_vals[fd] = val
					break
				elif eval_dt > we_dt:
					daily_vals[fd] = val		# need to do this in case the date is after the last wet end date
					last_val = val
				else:
					print "I do not think this can happen"
		return daily_vals
		
	#--------------------------------------------------------------------------------------------		
	# do blitecast calculations 
	def run_blitecast(self, stn, hourly_data, bliteD, end_date_dt, last_hour):
		# pick out wet and dry periods
		wet_periods = self.get_wetting_rh(hourly_data,stn)   ### new version instituted 6/18/2008 ##revised again 9/29/2011
		if len(wet_periods) > 0:
			# fill summary table
#						save_date = end_fcst_dt + DateTime.RelativeDate(days = -7)
#						summary_table = {'dates' : [], 'units' : []}
#						for i in range(0,8):
#							summary_table['dates'].append((save_date.year,save_date.month,save_date.day,23))
#							summary_table['units'].append(miss)
#							save_date = save_date + DateTime.RelativeDate(days = +1)
#						summary_table['units'][0] = 0
			bwet_data_short = []
			for sTime,eTime,skip,skip,skip,skip,skip,skip,sevunits in wet_periods:
				bwet_data_short.append((DateTime.DateTime(*sTime),DateTime.DateTime(*eTime),int(round(sevunits,0))))
#							if (eTime[0:3] < summary_table['dates'][0][0:3]):
#								summary_table['units'][0] = sevunits
#							else:
#								for i in range(0,8):
#									if eTime[0:3] == summary_table['dates'][i][0:3]:
#										summary_table['units'][i] = sevunits
#										break
#						for i in range(1,8):
#							if summary_table['units'][i] == miss:
#								summary_table['units'][i] = summary_table['units'][i-1]
#						for i in range(len(summary_table['dates'])):
#							idt = summary_table['dates'][i]
#							zdt = "%02d/%02d" % (idt[1],idt[2])
#							bliteD['daily_accums'][zdt] = int(round(summary_table['units'][i]))			
			bliteD['daily_accums'] = self.get_daily_accum(bwet_data_short, end_date_dt, last_hour)
			bliteD["wet_periods"] = wet_periods
		return bliteD
		
	#--------------------------------------------------------------------------------------------		
	# do simcast calculations
	def run_simcast(self, stn, station_name, simcastD, cultivar, month, day, year, start_date, end_date_dt, download_time):
		# obtain resisance of cultivar
		(resistance,maturity) = self.get_potato_status(cultivar)
		if resistance == "":
			return newaCommon_io.errmsg('Need to select a cultivar')
		elif resistance == 'resistant':
			simcastD['resistant'] = True
			simcastD['cultivar'] = cultivar
		else:
			# get station name from metadata
			# determine station type
			if stn[0:1] >= '1' and stn[0:1] <= '9' and stn[1:2] >= '0' and stn[1:2] <= '9':
				station_type = 'njwx'
			elif len(stn) == 4:
				station_type = 'icao'
			elif stn[0:3] == 'cu_' or stn[0:3] == 'um_' or stn[0:3] == "un_" or stn[0:3] == "uc_":
				station_type = 'cu_log'
			elif len(stn) == 3 or len(stn) == 6:
				station_type = 'newa'
			elif stn[0:3] == "ew_":
				stn = stn[3:]
				station_type = 'miwx'
			else:
				print 'Cannot determine station type for %s'%stn
				return newaCommon_io.errmsg('Invalid station selection')

			#initialize weather data dictionary
			stnWeather = {'dates': [], 'forecastDayDate': None, 'tmpF': [], 'flags': [], 'prcpMM': [], 'rh': [] }

			# last fungicide application
			fDate = "%d/%d/%d" % (month,day,year)
			fDate_dt =  start_date

			# setup dates (terminology different than above)
			start_date_dt = end_date_dt + DateTime.RelativeDate(hour=0,minute=0,second=0.0)
			stnWeather['forecastDayDate'] = (start_date_dt.year,start_date_dt.month,start_date_dt.day)
			download_dt = DateTime.DateTime(*download_time) + DateTime.RelativeDate(hours=+1)
##			stnWeather['forecastDayDate'] = (download_dt.year, download_dt.month, download_dt.day)
			end_date_dt = start_date_dt + DateTime.RelativeDate(days=+6) + DateTime.RelativeDate(hour=23,minute=0,second=0.0)

			# get hourly data
			start_input_dt = min(start_date_dt, fDate_dt)
			###### ADDED FOLLOWING #####
			start_input_dt = start_input_dt + DateTime.RelativeDate(days=-3)
			hourly_data = collect_hourly_input(stn, start_input_dt, end_date_dt, ['temp','prcp','rhum'], station_type)
			ks = hourly_data.keys()
			# and format it for simcast use
			if len(ks) > 0:
				ks.sort()
				for key_date in ks:
					#these times are in LT. Convert to EST for simcast.
					theTime_dt = DateTime.DateTime(*key_date)
					theTime_dt = theTime_dt + DateTime.RelativeDate(hours=-theTime_dt.dst)
					est = (theTime_dt.year,theTime_dt.month,theTime_dt.day,theTime_dt.hour)
					stnWeather['dates'].append(est)
					stnWeather['tmpF'].append(hourly_data[key_date]['temp'][0])
					if hourly_data[key_date]['prcp'][0] != -999:
						prcp = inch_to_mm.convert(hourly_data[key_date]['prcp'][0])
					else:
						prcp = -999
					stnWeather['prcpMM'].append(prcp)
					if hourly_data[key_date]['rhum'][1] == "F" or station_type == 'icao' and hourly_data[key_date]['rhum'][0] != miss:
						stnWeather['rh'].append(min(100,hourly_data[key_date]['rhum'][0]+15))
					else:
						stnWeather['rh'].append(hourly_data[key_date]['rhum'][0])
					stnWeather['flags'].append(hourly_data[key_date]['prcp'][1])
				simcastD = self.process_simcast(station_name,resistance,fDate,stnWeather)
				simcastD['resistant'] = False
			else:
				return newaCommon_io.nodata()

			if not simcastD.has_key('length') or simcastD['length'] <= 0:
				return newaCommon_io.nodata()
			simcastD['daily_accums'] = {}
			for i in range(0, simcastD['length']):
				zmmdd = simcastD['dates'][i].split('/')
				zdt = "%02d/%02d" % (int(zmmdd[0]),int(zmmdd[1]))
				simcastD['daily_accums'][zdt] = [simcastD['bliteVals'][i], simcastD['bliteCrit'][i], simcastD['fungicideVals'][i], simcastD['fungicideCrit'][i]]
		return simcastD


#--------------------------------------------------------------------------------------------		
class Potato (Pottom):
	#--------------------------------------------------------------------------------------------		
	# get p for given temperature (used in p-day calculation)
	def getp(self,t):
		if t < 7:
			p = 0.
		elif t >= 7 and t < 21:
			p = 10. * (1.-(((21-t)**2.)/196.))
		elif t >= 21 and t < 30:
			p = 10. * (1.-(((t-21)**2.)/81.))
		else:
			p = 0.
		return p
		
	#--------------------------------------------------------------------------------------------		
	# calculate daily pday value
	def calc_pday(self,tmax,tmin):
		tminc = (5./9.)*(tmin-32.)
		tmaxc = (5./9.)*(tmax-32.)
		at2 = ((2.*tminc) + tmaxc)/3.
		at3 = (tminc + (2.*tmaxc))/3.
		pday = round((1./24.)*(5.*self.getp(tminc)+8.*self.getp(at2)+8.*self.getp(at3)+3.*self.getp(tmaxc)),1)
		return pday

	#--------------------------------------------------------------------------------------------		
	def run_potato_lb (self,stn,year,month,day,output):
		try:
			# obtain hourly data
			now = DateTime.now()
			start_date_dt = DateTime.DateTime(year,month,day,1)
			if year == now.year:
				end_date_dt = now
			else:
				end_date_dt = DateTime.DateTime(year,10,1,1)
			hourly_data, download_time, station_name = self.get_hourly (stn, start_date_dt, end_date_dt)

			# add hourly forecast data  - added 5/11/2012 KLE
			start_fcst_dt = DateTime.DateTime(*download_time) + DateTime.RelativeDate(hours = +1)
			end_fcst_dt = end_date_dt + DateTime.RelativeDate(days = +6) + DateTime.RelativeDate(hour=23,minute=0,second=0.0)
			hourly_data = add_hrly_fcst(stn,hourly_data,start_fcst_dt,end_fcst_dt)
			
			if len(hourly_data) > 0:
				# pick out wet and dry periods
				wet_periods = self.get_wetting_rh(hourly_data,stn)   ### new version instituted 6/18/2008 ##revised again 9/29/2011
			else:
				return self.nodata (stn, station_name, start_date_dt, end_date_dt)

			if len(wet_periods) > 0:
				# fill summary table
				save_date = end_fcst_dt + DateTime.RelativeDate(days = -7)
				summary_table = {'dates' : [], 'units' : []}
				for i in range(0,8):
					summary_table['dates'].append((save_date.year,save_date.month,save_date.day,23))
					summary_table['units'].append(miss)
					save_date = save_date + DateTime.RelativeDate(days = +1)
				summary_table['units'][0] = 0
				for sTime,eTime,skip,skip,skip,skip,skip,skip,sevunits in wet_periods:
					if (eTime[0:3] < summary_table['dates'][0][0:3]):
						summary_table['units'][0] = sevunits
					else:
						for i in range(0,8):
							if eTime[0:3] == summary_table['dates'][i][0:3]:
								summary_table['units'][i] = sevunits
								break
				for i in range(1,8):
					if summary_table['units'][i] == miss:
						summary_table['units'][i] = summary_table['units'][i-1]
									
				# convert to html and write to file (single station)
				return newaDisease_io.potato_lb_html(stn,station_name,download_time,wet_periods,summary_table,output)
			else:
				return self.nodata(stn, station_name, start_date_dt, end_date_dt)
		except:
			print_exception()
			return newaCommon_io.errmsg('Unable to complete request')

	#--------------------------------------------------------------------------------------------		
	def run_potato_simcast(self,stn,year,month,day,cultivar):
		results = {}
		try:
			# obtain resisance of cultivar
			(resistance,maturity) = self.get_potato_status(cultivar)
			if resistance == "":
				return newaCommon_io.errmsg('Need to select a cultivar')
			elif resistance == 'resistant':
				return newaDisease_io.resistant(cultivar)
	
			# get station name from metadata
			# determine station type
			if stn[0:1] >= '1' and stn[0:1] <= '9' and stn[1:2] >= '0' and stn[1:2] <= '9':
				station_type = 'njwx'
			elif len(stn) == 4:
				station_type = 'icao'
			elif stn[0:3] == 'cu_' or stn[0:3] == 'um_' or stn[0:3] == "un_" or stn[0:3] == "uc_":
				station_type = 'cu_log'
			elif len(stn) == 3 or len(stn) == 6:
				station_type = 'newa'
			elif station_id[0:3] == "ew_":
				station_id = station_id[3:]
				station_type = 'miwx'
			else:
				print 'Cannot determine station type for %s'%stn
				return newaCommon_io.errmsg('Invalid station selection')
			ucanid, station_name = get_metadata (stn, station_type)
			if station_name == stn:
				return newaCommon_io.errmsg('Invalid station selection')
			
			#initialize weather data dictionary
			stnWeather = {'dates': [], 'forecastDayDate': None, 'tmpF': [], 'flags': [], 'prcpMM': [], 'rh': [] }
	
			# last fungicide application
			fDate = "%d/%d/%d" % (month,day,year)
			fDate_dt =  DateTime.DateTime(year,month,day,10)

			# setup dates
			start_date_dt = DateTime.now() + DateTime.RelativeDate(hour=0,minute=0,second=0.0)
			stnWeather['forecastDayDate'] = (start_date_dt.year,start_date_dt.month,start_date_dt.day)
			end_date_dt = start_date_dt + DateTime.RelativeDate(days=+6) + DateTime.RelativeDate(hour=23,minute=0,second=0.0)
		
			# get hourly data
			start_input_dt = min(start_date_dt, fDate_dt)
			###### ADDED FOLLOWING #####
			start_input_dt = start_input_dt + DateTime.RelativeDate(days=-3)
			hourly_data = collect_hourly_input(stn, start_input_dt, end_date_dt, ['temp','prcp','rhum'], station_type)
			ks = hourly_data.keys()
			# and format it for simcast use
			if len(ks) > 0:
				ks.sort()
				for key_date in ks:
					#these times are in LT. Convert to EST for simcast.
					theTime_dt = DateTime.DateTime(*key_date)
					theTime_dt = theTime_dt + DateTime.RelativeDate(hours=-theTime_dt.dst)
					est = (theTime_dt.year,theTime_dt.month,theTime_dt.day,theTime_dt.hour)
					stnWeather['dates'].append(est)
					stnWeather['tmpF'].append(hourly_data[key_date]['temp'][0])
					if hourly_data[key_date]['prcp'][0] != -999:
						prcp = inch_to_mm.convert(hourly_data[key_date]['prcp'][0])
					else:
						prcp = -999
					stnWeather['prcpMM'].append(prcp)
					if hourly_data[key_date]['rhum'][1] == "F" or station_type == 'icao':
						stnWeather['rh'].append(min(100,hourly_data[key_date]['rhum'][0]+15))
					else:
						stnWeather['rh'].append(hourly_data[key_date]['rhum'][0])
					stnWeather['flags'].append(hourly_data[key_date]['prcp'][1])
				results = self.process_simcast(station_name,resistance,fDate,stnWeather) 
			else:
				return newaCommon_io.nodata()
	
			if results.has_key('length') and results['length'] > 0:
				return newaDisease_io.potato_simcast_html(station_name,results)
			else:
				return newaCommon_io.nodata()
		except:
			print_exception()
			return newaCommon_io.errmsg('Unable to complete request')

	#--------------------------------------------------------------------------------------------		
	# calculate p-day values for all days
	def run_potato_pdays (self,stn,year,month,day,output):
		try:
			# obtain daily data
			now = DateTime.now()
			start_date_dt = DateTime.DateTime(year,month,day,1)
			if year == now.year:
				end_date_dt = now
			else:
				end_date_dt = DateTime.DateTime(year,10,1,1)
			daily_data, station_name = self.get_daily (stn, start_date_dt, end_date_dt)
			
			if len(daily_data) > 0:
				daily_pday = []
				saccum = 0.
				# do calculations
				for dt,tave,tmax,tmin,prcp,lwet,rhum,wspd,srad,st4ia,st4ix,st4in,dflags in daily_data:
					if dt[1] < start_date_dt.month: continue
					if tmax != miss and tmin != miss:
						pday = self.calc_pday(tmax,tmin)
						saccum = saccum + pday
					else:
						pday = miss
						#ignore missing values in accumulation
					daily_pday.append((dt,pday,saccum))

				if len(daily_pday) > 0:
					return newaDisease_io.potato_pdays_html(station_name,daily_pday,output)
				else:
					return self.nodata(stn, station_name, start_date_dt, end_date_dt)
			else:
				return self.nodata(stn, station_name, start_date_dt, end_date_dt)
		except:
			print_exception()
			return newaCommon_io.errmsg('Unable to complete request')
			
	#--------------------------------------------------------------------------------------------		
	# get pdays
	def run_pdays(self, stn, station_name, hourly_data, start_date_dt, end_date_dt):
		daily_pday = []
		daily_data = hrly_to_dly(hourly_data, 12)	#end day at 12 noon
		if len(daily_data) > 0:
			saccum = 0.
			# do calculations
			for dt,tave,tmax,tmin,prcp,v,v,v,v,v,v,v,dflags in daily_data:
				if dt[1] < start_date_dt.month: continue
				if tmax != miss and tmin != miss:
					pday = self.calc_pday(tmax,tmin)
					saccum = saccum + pday
				else:
					pday = miss
					#ignore missing values in accumulation
				daily_pday.append((dt,pday,saccum))

			if len(daily_pday) > 0:
				return daily_pday
			else:
				return self.nodata(stn, station_name, start_date_dt, end_date_dt)
		else:
			return self.nodata(stn, station_name, start_date_dt, end_date_dt)
			
	#--------------------------------------------------------------------------------------------		
	def run_potato_for (self,subtype,stn,year,month,day,emerg_dt,cultivar,accend,output):
		#year,month,day is either first tissue emergence (BC) or last fungicide (SC)
		#emerg_dt is crop emergence date for both
		try:
			simcastD = {}
			bliteD = {}
			smry_dict = {}
			pday_list = []

			if accend:
				end_date_dt = accend + DateTime.RelativeDate(hour=12,minute=0,second=0)
			else:
				end_date_dt = DateTime.now()
				year = end_date_dt.year
				
			if emerg_dt > end_date_dt:
				return newaCommon_io.errmsg('Cannot have future crop emergence date')
			
			#start date for bc and sc	
			start_date = DateTime.DateTime(year,month,day,10)
			if start_date > end_date_dt:
				if subtype == 'blitecast':
					return newaCommon_io.errmsg('Cannot have future tissue emergence date')
				else:
					return newaCommon_io.errmsg('Cannot have future fungicide date')
			
			# obtain all hourly data for station
			end_fcst_dt = end_date_dt + DateTime.RelativeDate(days = +6) + DateTime.RelativeDate(hour=23,minute=0,second=0)
			hourly_data, download_time, station_name, avail_vars = self.get_hourly2 (stn, emerg_dt, end_fcst_dt)
			smry_dict = {'download_time':download_time, 'avail_vars':avail_vars, 'output': output}
			start_fcst_dt = DateTime.DateTime(*download_time) + DateTime.RelativeDate(hours = +1)
			# append any available forecast data after end of observed data
			if end_fcst_dt >= start_fcst_dt:
				hourly_data = add_hrly_fcst(stn,hourly_data,start_fcst_dt,end_fcst_dt)
			# get last (forecast) value with precip amt
			smry_dict['lastqpf'] = self.getLastPrecip(hourly_data)
			last_hour = hourly_data[-1][0]

	# this is pdays
			if len(hourly_data) > 0: 
				pday_list = self.run_pdays(stn, station_name, hourly_data, emerg_dt, end_date_dt)
			else:
				return self.nodata(stn, station_name, start_date, end_date_dt)
	# end pdays
				
	# this is blitecast
			if subtype == 'blitecast':
				if emerg_dt != start_date:
					# need different data than we did for pdays
					hourly_data, download_time, station_name, avail_vars = self.get_hourly2 (stn, start_date, end_fcst_dt)
					if end_fcst_dt >= start_fcst_dt:
						hourly_data = add_hrly_fcst(stn,hourly_data,start_fcst_dt,end_fcst_dt)					
				if len(hourly_data) > 0:
					bliteD = self.run_blitecast(stn, hourly_data, bliteD, end_date_dt, last_hour)
	# end blitecast
						
	# this is simcast
			elif subtype == 'simcast':
				if start_date > end_date_dt:
					return newaCommon_io.errmsg('Cannot have future fungicide date')
				simcastD = self.run_simcast(stn, station_name, simcastD, cultivar, month, day, year, start_date, end_date_dt, download_time)					
	# end simcast
			
			# send off data to results page
			return newaDisease_io.potato_for_html(station_name,smry_dict,pday_list,simcastD,bliteD)
		except:
			print_exception()
			return newaCommon_io.errmsg('Unable to complete request')


#--------------------------------------------------------------------------------------------		
class Apple (Base):
	# determine wet and dry periods from hourly data provided
	def get_wetting (self,hourly_data):
		wet_periods = []
		dry_periods = []
		try:
			wet_hrs = 0
			dry_hrs = 0
			temp_sum = 0.
			temp_cnt = 0.
			prcp_sum = 0.
			prcp_cnt = 0.
			for theTime,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags in hourly_data:
				if lwet == miss and rhum != miss:
					if rhum >= 90 or prcp > 0.00:
						lwet = 60
					else:
						lwet = 0
				if lwet > 0 and wet_hrs == 0 and (prcp == 0 or prcp == miss): lwet=0	#wetting period must start with prcp
				if lwet > 0:
					if dry_hrs > 0:
						dry_end = (DateTime.DateTime(*theTime) + DateTime.RelativeDate(hours=-1)).tuple()[:4]
						if temp_cnt > 0:
							temp_ave = temp_sum/temp_cnt
						else:
							temp_ave = miss
						dry_periods.append((dry_start,dry_end,dry_hrs,temp_ave))
						dry_hrs = 0
						temp_sum = 0.
						temp_cnt = 0.
					wet_hrs = wet_hrs + 1
					if wet_hrs == 1: 
						wet_start = (DateTime.DateTime(*theTime) + DateTime.RelativeDate(hours=-1)).tuple()[:4]
					if temp != miss:
						temp_sum = temp_sum + temp
						temp_cnt = temp_cnt + 1
					if prcp != miss:
						prcp_sum = prcp_sum + prcp
						prcp_cnt = prcp_cnt + 1
				else:
					if wet_hrs > 0: 
						wet_end = (DateTime.DateTime(*theTime) + DateTime.RelativeDate(hours=-1)).tuple()[:4]
						if temp_cnt > 0:
							temp_ave = temp_sum/temp_cnt
						else:
							temp_ave = miss
						if prcp_cnt > 0:
							prcp_tot = prcp_sum
						else:
							prcp_tot = miss
						wet_periods.append((wet_start,wet_end,wet_hrs,temp_ave,prcp_tot))
						wet_hrs = 0
						temp_sum = 0.
						temp_cnt = 0.
						prcp_sum = 0.
						prcp_cnt = 0.					
					dry_hrs = dry_hrs + 1
					if dry_hrs == 1:
						dry_start = (DateTime.DateTime(*theTime) + DateTime.RelativeDate(hours=-1)).tuple()[:4]
					if temp != miss:
						temp_sum = temp_sum + temp
						temp_cnt = temp_cnt + 1
			# end period in progress
			if wet_hrs > 0:
				wet_end = miss
				if temp_cnt > 0:
					temp_ave = temp_sum/temp_cnt
				else:
					temp_ave = miss
				if prcp_cnt > 0:
					prcp_tot = prcp_sum
				else:
					prcp_tot = miss
				wet_periods.append((wet_start,wet_end,wet_hrs,temp_ave,prcp_tot))
			elif dry_hrs > 0:
				dry_end = miss
				if temp_cnt > 0:
					temp_ave = temp_sum/temp_cnt
				else:
					temp_ave = miss
				dry_periods.append((dry_start,dry_end,dry_hrs,temp_ave))	
		except:
			print_exception()
		return wet_periods, dry_periods
		
	#--------------------------------------------------------------------------------------------		
	# fire blight degree hours from hourly data
	def get_deghrs(self,hourly_data):
		daily_fire = []
		try:
			yest_tmax = 9999
			day2_tmax = 9999
			fbdh = 0.
			accfbdh = 0.
			accgdd = 0.
			temp_cnt = 0.
			tmax = -9999.
			tmin = 9999.
			for i in range(len(hourly_data)):
				dt,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags = hourly_data[i]
				if temp != miss:
					# fire blight degree hours for day
					if temp > 65:
						fbdh = fbdh + (temp - 65.)
					if temp > tmax: tmax = copy.deepcopy(temp)
					if temp < tmin: tmin = copy.deepcopy(temp)
					temp_cnt = temp_cnt + 1
				# end of day summary
				theDate = DateTime.DateTime(dt[0],dt[1],dt[2],dt[3])
				last_hr = 23 - theDate.dst
				if last_hr == 24:
					last_hr = 0
					day_diff = -1
				else:
					day_diff = 0
				if dt[3] == last_hr or i == len(hourly_data)-1:
					if temp_cnt == 0:
						fbdh = miss
						tmax = miss
						tmin = miss
					# regular base 50 gdd
					if tmax != miss and tmin != miss:
						gdd = ((tmax+tmin)/2.) - 50
						if gdd < 0: gdd = 0.
						if accgdd != miss:
							accgdd = accgdd + gdd
					else:
						accgdd = miss
					# accumulated fire blight degree hours for season
					if accfbdh != miss and fbdh != miss:
						accfbdh = accfbdh + fbdh
					else:
						accfbdh = miss
					# fine-tuned fire blight dh
					if accfbdh == miss:
						pass
					elif (tmax < 65 and yest_tmax < 65 and day2_tmax < 65) or tmin < 32:
						if accfbdh < 400: accfbdh = 0.
					elif tmax < 65 and yest_tmax < 65:
						if accfbdh < 400: accfbdh = 0.75*accfbdh
					elif tmax < 65:
						if accfbdh < 400: accfbdh = 0.667*accfbdh
					if day_diff == 0:
						ddt = theDate
					else:
						ddt = theDate + DateTime.RelativeDate(days=day_diff)
					dt3 = [ddt.year,ddt.month,ddt.day,ddt.hour]
					daily_fire.append((dt3,tmax,tmin,accgdd,fbdh,accfbdh))
					fbdh = 0.
					day2_tmax = yest_tmax
					yest_tmax = tmax
					temp_cnt = 0.
					tmax = -9999.
					tmin = 9999.
		except:
			print_exception()
		return daily_fire

	#--------------------------------------------------------------------------------------------		
	# format wet and dry period information into tab-delimited lines for output
	def apple_log(self,wet_periods,dry_periods):
		lines = []
		try:
			first_wet_dt = DateTime.DateTime(*wet_periods[0][0])
			first_dry_dt = DateTime.DateTime(*dry_periods[0][0])
			if first_wet_dt < first_dry_dt:
				wet_start,wet_end,wet_hrs,temp_ave,prcp_tot = wet_periods[0]
				wsyr,wsmn,wsdy,wshr = wet_start
				wshr,wsampm = self.format_time(wshr)
				weyr,wemn,wedy,wehr = wet_end
				wehr,weampm = self.format_time(wehr)
				wet_part = '%d/%d/%d %d:01 %s\t%d/%d/%d %d:00 %s\t%d\t%d\t%.2f' % \
					(wsyr,wsmn,wsdy,wshr,wsampm, weyr,wemn,wedy,wehr,weampm,wet_hrs,round(temp_ave,0),prcp_tot)
				dry_part = '\t---\t---\t--'
				lines.append(wet_part+dry_part)
				wet_cnt = 1
			else:
				wet_cnt = 0
			for i in range(len(dry_periods)):
				if wet_cnt < len(wet_periods):
					wet_start,wet_end,wet_hrs,temp_ave,prcp_tot = wet_periods[wet_cnt]
					wsyr,wsmn,wsdy,wshr = wet_start
					wshr,wsampm = self.format_time(wshr)
					if wet_end == miss:
						we_str = 'in progress'
					else:
						weyr,wemn,wedy,wehr = wet_end
						wehr,weampm = self.format_time(wehr)
						we_str = '%d/%d/%d %d:00 %s' % (wemn,wedy,weyr,wehr,weampm)
					wet_part = '%d/%d/%d %d:01 %s\t%s\t%d\t%d\t%.2f' % \
						(wsmn,wsdy,wsyr,wshr,wsampm,we_str,wet_hrs,round(temp_ave,0),prcp_tot)
					wet_cnt = wet_cnt + 1
				else:
					wet_part = '---\t---\t--\t--\t---'
				dry_start,dry_end,dry_hrs,dtemp_ave = dry_periods[i]
				dsyr,dsmn,dsdy,dshr = dry_start
				dshr,dsampm = self.format_time(dshr)
				if dry_end == miss:
					de_str = 'in progress'
				else:
					deyr,demn,dedy,dehr = dry_end
					dehr,deampm = self.format_time(dehr)
					de_str = '%d/%d/%d %d:00 %s' % (demn,dedy,deyr,dehr,deampm)
				dry_part = '\t%d/%d/%d %d:01 %s\t%s\t%d\t%d' % (dsmn,dsdy,dsyr,dshr,dsampm,de_str,dry_hrs,round(dtemp_ave,0))
				lines.append(wet_part+dry_part)
		except:
			print_exception()
		return lines

	#--------------------------------------------------------------------------------------------		
	def run_apple_lw (self,stn,year):
		try:
			# obtain hourly data
			if year:
				end_date_dt = DateTime.DateTime(year,10,31)
			else:
				end_date_dt = DateTime.now()
			start_date_dt = DateTime.DateTime(end_date_dt.year,3,1,1)	#Leave this March 1			
			hourly_data, download_time, station_name, avail_vars = self.get_hourly2 (stn, start_date_dt, end_date_dt)
			
			if len(hourly_data) > 0:
				# pick out wet and dry periods
				wet_periods,dry_periods = self.get_wetting(hourly_data)
			else:
				return self.nodata (stn, station_name, start_date_dt, end_date_dt)

			if len(wet_periods) > 0 and len(dry_periods) > 0:
				# format leaf wetness data for output
				wd_lines = self.apple_log(wet_periods,dry_periods)
				# convert to html and write to file for Wet and Dry Log (single station)
				return newaDisease_io.apple_lw_html(station_name,download_time,wd_lines, avail_vars)
			else:
				return self.nodata(stn, station_name, start_date_dt, end_date_dt)
		except:
			print_exception()
			
	#--------------------------------------------------------------------------------------------		
	def run_apple_fb (self,stn):
		try:
			# obtain hourly data
			end_date_dt = DateTime.now()
			start_date_dt = DateTime.DateTime(end_date_dt.year,3,1,1)	#Leave this March 1			
			hourly_data, download_time, station_name = self.get_hourly (stn, start_date_dt, end_date_dt)
			
			if len(hourly_data) > 0:
				# base 50 GDD and fire blight degree hours
				daily_fire = self.get_deghrs(hourly_data)
			else:
				return self.nodata (stn, station_name, start_date_dt, end_date_dt)

			if len(daily_fire) > 0:
				return newaDisease_io.apple_fb_html(station_name,download_time,daily_fire)
			else:
				return self.nodata(stn, station_name, start_date_dt, end_date_dt)
		except:
			print_exception()
			
#--------------------------------------------------------------------------------------------		
class Cabbage (Base):
	#  save dates for use later
	def setup_dates (self,smry_dict,end_date_dt):
		try:
			smry_dict['day0'] = {}
			smry_dict['pday1'] = {}
			smry_dict['pday2'] = {}
			smry_dict['fday1'] = {}
			smry_dict['fday2'] = {}
			smry_dict['fday3'] = {}
			smry_dict['fday4'] = {}
			smry_dict['fday5'] = {}
			
			day0 = end_date_dt
			day0 = day0 + DateTime.RelativeDate(hour=0,minute=0,second=0)
			pday1 = day0 + DateTime.RelativeDate(days=-1)
			pday2 = day0 + DateTime.RelativeDate(days=-2)
			fday1 = day0 + DateTime.RelativeDate(days=+1)
			fday2 = day0 + DateTime.RelativeDate(days=+2)
			fday3 = day0 + DateTime.RelativeDate(days=+3)
			fday4 = day0 + DateTime.RelativeDate(days=+4)
			fday5 = day0 + DateTime.RelativeDate(days=+5)
	
			smry_dict['day0']['ymd']  = (day0.year,day0.month,day0.day)
			smry_dict['pday1']['ymd'] = (pday1.year,pday1.month,pday1.day)
			smry_dict['pday2']['ymd'] = (pday2.year,pday2.month,pday2.day)
			smry_dict['fday1']['ymd'] = (fday1.year,fday1.month,fday1.day)
			smry_dict['fday2']['ymd'] = (fday2.year,fday2.month,fday2.day)
			smry_dict['fday3']['ymd'] = (fday3.year,fday3.month,fday3.day)
			smry_dict['fday4']['ymd'] = (fday4.year,fday4.month,fday4.day)
			smry_dict['fday5']['ymd'] = (fday5.year,fday5.month,fday5.day)
	
			smry_dict['day0']['date']  = '%s %d' % (month_names[day0.month][0:3],day0.day)
			smry_dict['pday1']['date'] = '%s %d' % (month_names[pday1.month][0:3],pday1.day)
			smry_dict['pday2']['date'] = '%s %d' % (month_names[pday2.month][0:3],pday2.day)
			smry_dict['fday1']['date'] = '%s %d' % (month_names[fday1.month][0:3],fday1.day)
			smry_dict['fday2']['date'] = '%s %d' % (month_names[fday2.month][0:3],fday2.day)
			smry_dict['fday3']['date'] = '%s %d' % (month_names[fday3.month][0:3],fday3.day)
			smry_dict['fday4']['date'] = '%s %d' % (month_names[fday4.month][0:3],fday4.day)
			smry_dict['fday5']['date'] = '%s %d' % (month_names[fday5.month][0:3],fday5.day)
		except:
			print_exception()
		return smry_dict

	#--------------------------------------------------------------------------------------------		
	# add degree days to dictionary
	def add_ddays (self,smry_dict,degday_dict,start_date_dt,end_date_dt):
		try:
			day0 =  end_date_dt + DateTime.RelativeDate(hour=0,minute=0,second=0)
			pday1 = day0 + DateTime.RelativeDate(days=-1)
			pday2 = day0 + DateTime.RelativeDate(days=-2)
			fday1 = day0 + DateTime.RelativeDate(days=+1)
			fday2 = day0 + DateTime.RelativeDate(days=+2)
			fday3 = day0 + DateTime.RelativeDate(days=+3)
			fday4 = day0 + DateTime.RelativeDate(days=+4)
			fday5 = day0 + DateTime.RelativeDate(days=+5)
			smry_dict['day0']['dday']  = 'NA'
			smry_dict['pday1']['dday'] = 'NA'
			smry_dict['pday2']['dday'] = 'NA'
			smry_dict['fday1']['dday'] = 'NA'
			smry_dict['fday2']['dday'] = 'NA'
			smry_dict['fday3']['dday'] = 'NA'
			smry_dict['fday4']['dday'] = 'NA'
			smry_dict['fday5']['dday'] = 'NA'
			smry_dict['day0']['accdday']  = 'NA'
			smry_dict['pday1']['accdday'] = 'NA'
			smry_dict['pday2']['accdday'] = 'NA'
			smry_dict['fday1']['accdday'] = 'NA'
			smry_dict['fday2']['accdday'] = 'NA'
			smry_dict['fday3']['accdday'] = 'NA'
			smry_dict['fday4']['accdday'] = 'NA'
			smry_dict['fday5']['accdday'] = 'NA'

			# add ddays for last three days, forecast next 5 days
			accum = 0.
			for theDate,max,min,gdd,prcp in degday_dict:
				theDate_dt = DateTime.DateTime(*theDate) + DateTime.RelativeDate(hour=0,minute=0,second=0)
				if accum != miss and gdd != miss: accum = accum + gdd
				for td,std in [(day0,'day0'),(pday1,'pday1'),(pday2,'pday2'),(fday1,'fday1'),(fday2,'fday2'),(fday3,'fday3'),(fday4,'fday4'),(fday5,'fday5')]:
					if td == theDate_dt and gdd != miss: 
						smry_dict[std]['dday'] = int(round(gdd,0))
						if accum != miss: smry_dict[std]['accdday'] = int(round(accum,0))
		except:
			print_exception()
		return smry_dict

	#--------------------------------------------------------------------------------------------		
	def run_cabbage_maggot (self,stn,accend):
		try:
			now = DateTime.now()
			if not accend:
				accend = now
			smry_dict = {}
			# obtain daily data
			end_date_dt = accend
			midOctober = DateTime.DateTime(end_date_dt.year,10,15,23)
			if end_date_dt > midOctober:
				 return newaDisease_io.cabbage_maggot_dormant(smry_dict)
			start_date_dt = DateTime.DateTime(end_date_dt.year,1,1,1)		

			if end_date_dt.year != now.year:
				smry_dict['this_year'] = False
				end_date_dt = end_date_dt + DateTime.RelativeDate(days = +6)
			else:
				smry_dict['this_year'] = True

			hourly_data, daily_data, download_time, station_name, avail_vars = self.get_hddata2 (stn, start_date_dt, end_date_dt)

			# add forecast data
			if smry_dict['this_year']:
				start_fcst_dt = DateTime.DateTime(*download_time) + DateTime.RelativeDate(hours = +1)
				end_fcst_dt = end_date_dt + DateTime.RelativeDate(days = +6)
				hourly_data = add_hrly_fcst(stn,hourly_data,start_fcst_dt,end_fcst_dt)
				daily_data = hrly_to_dly(hourly_data)
			else:
				start_fcst_dt = end_date_dt + DateTime.RelativeDate(hours = +1)
				end_fcst_dt = end_date_dt	
				end_date_dt = end_date_dt + DateTime.RelativeDate(days = -6)


#			daily_data, station_name = self.get_daily (stn, start_date_dt, end_date_dt)
#			start_fcst_dt = DateTime.DateTime(*daily_data[-1][0]) + DateTime.RelativeDate(days = +1)
#			end_fcst_dt = end_date_dt + DateTime.RelativeDate(days = +5)
#			daily_data = add_dly_fcst(stn,daily_data,start_fcst_dt,end_fcst_dt)
			
			if len(daily_data) > 0:
				# base 40degF GDD 
				degday_dict = self.degday_calcs (daily_data,start_date_dt,end_fcst_dt,'dd40', "accum")

				if len(degday_dict) > 0:
					# get dates for gdd table
					smry_dict = self.setup_dates(smry_dict, end_date_dt)
					# get dd for days of interest (including forecast)
					smry_dict = self.add_ddays(smry_dict,degday_dict,start_date_dt,end_date_dt)
					return newaDisease_io.cabbage_maggot_html(station_name,smry_dict,degday_dict)
				else:
					return self.nodata(stn, station_name, start_date_dt, end_date_dt)
			else:
				return self.nodata (stn, station_name, start_date_dt, end_date_dt)
		except:
			print_exception()

#--------------------------------------------------------------------------------------------		
class Onion (Base, Cabbage):
	# determine botrytis spore_index for given day
	def get_bot_sindx(self,d3_temp,d3_vpd):
		spore_index = miss
		sindex_dict = {
		0.00: [90, 92, 94, 96, 97, 97, 98, 98, 98, 99, 99, 99, 99, 99, 100, 100, 100],
		0.25: [88, 91, 93, 95, 96, 97, 97, 98, 98, 99, 99, 99, 99, 99, 99, 100, 100],
		0.50: [86, 88, 91, 94, 95, 96, 97, 97, 97, 98, 98, 98, 99, 99, 99, 99, 99],
		0.75: [83, 86, 89, 92, 94, 95, 96, 96, 97, 97, 98, 98, 98, 99, 99, 99, 99],
		1.00: [79, 83, 87, 90, 92, 94, 95, 96, 96, 97, 97, 98, 98, 98, 99, 99, 99],
		1.25: [75, 80, 84, 87, 90, 92, 94, 95, 96, 96, 97, 97, 98, 98, 98, 99, 99],
		1.50: [67, 78, 71, 85, 87, 90, 92, 94, 95, 96, 96, 97, 97, 98, 98, 98, 98],
		1.75: [60, 69, 77, 82, 85, 87, 90, 92, 94, 95, 96, 96, 97, 97, 97, 98, 98],
		2.00: [51, 62, 71, 78, 82, 85, 88, 90, 93, 94, 95, 96, 96, 97, 97, 97, 98],
		2.25: [42, 55, 65, 74, 79, 82, 85, 88, 91, 93, 94, 95, 95, 96, 96, 97, 97],
		2.50: [31, 46, 59, 68, 75, 79, 83, 85, 89, 91, 93, 94, 94, 95, 95, 96, 97],
		2.75: [23, 36, 50, 62, 70, 76, 80, 83, 86, 89, 91, 93, 93, 94, 95, 95, 96],
		3.00: [17, 28, 40, 53, 64, 71, 77, 80, 84, 86, 89, 91, 92, 93, 94, 95, 95],
		3.25: [12, 20, 32, 44, 56, 65, 72, 77, 81, 84, 86, 89, 91, 92, 93, 94, 94],
		3.50: [ 7, 15, 25, 37, 48, 58, 66, 72, 77, 81, 84, 86, 89, 90, 92, 92, 93],
		3.75: [ 4, 10, 20, 29, 39, 50, 60, 67, 73, 78, 81, 84, 86, 88, 89, 91, 92],
		4.00: [ 1,  6, 14, 22, 32, 43, 52, 62, 68, 74, 77, 81, 83, 85, 87, 88, 90],
		4.25: [ 0,  4,  9, 17, 25, 36, 45, 54, 62, 68, 74, 76, 80, 82, 84, 85, 87],
		4.50: [ 0,  2,  7, 12, 20, 28, 38, 46, 54, 61, 67, 72, 75, 78, 80, 82, 83],
		4.75: [ 0,  1,  4,  9, 15, 22, 31, 39, 47, 53, 59, 64, 71, 72, 75, 78, 80],
		5.00: [ 0,  0,  2,  6, 11, 17, 25, 32, 39, 44, 51, 56, 60, 68, 68, 71, 74],
		5.25: [ 0,  0,  0,  3,  8, 13, 19, 25, 32, 38, 44, 48, 52, 56, 61, 64, 66],
		5.50: [ 0,  0,  0,  1,  5,  9, 15, 20, 25, 31, 37, 40, 45, 49, 52, 55, 58],
		5.75: [ 0,  0,  0,  0,  3,  6, 10, 16, 20, 25, 29, 33, 37, 41, 45, 48, 50],
		6.00: [ 0,  0,  0,  0,  1,  4,  7, 11, 15, 19, 23, 26, 30, 33, 37, 41, 42],
		6.25: [ 0,  0,  0,  0,  0,  2,  4,  7, 11, 14, 17, 20, 24, 27, 30, 33, 35],
		6.50: [ 0,  0,  0,  0,  0,  0,  2,  4,  7, 10, 12, 15, 18, 20, 21, 25, 28],
		6.75: [ 0,  0,  0,  0,  0,  0,  0,  1,  4,  6,  9, 10, 12, 14, 16, 19, 23],
		7.00: [ 0,  0,  0,  0,  0,  0,  0,  0,  1,  3,  5,  6,  8,  9, 10, 14, 18],
		7.25: [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  2,  3,  4,  5,  7, 10, 13],
		7.50: [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  2,  3,  4,  6,  9],
		7.75: [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  2,  3,  5],
		8.00: [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  2] }
		try:
			if d3_temp != miss and d3_vpd != miss:
				if int(d3_temp) <= 7: 
					spore_index = 0.0
				else:
					if d3_temp > 24: 
						itemp = 24
					else:
						itemp = int(d3_temp)
					if d3_vpd >= 8:
						spore_index = sindex_dict[8.00][itemp-8]
					else:
						vkeys = sindex_dict.keys()
						vkeys.sort()
						for k in range(len(vkeys)):
							if d3_vpd >= vkeys[k] and d3_vpd < vkeys[k+1]:
								spore_index = sindex_dict[vkeys[k]][itemp-8]
								break
			else:
				spore_index = miss
		except:
			print_exception()
		return spore_index
			
	#--------------------------------------------------------------------------------------------		
	# calculate daily Botrytis potential
	def get_botrytis(self,daily_onion):
		botrytis = {}
		try:
			for i in range(len(daily_onion)-1,1,-1):
				if daily_onion[i][1] != miss and daily_onion[i-1][1] != miss and daily_onion[i-2][1] != miss:
					d3_temp = (daily_onion[i][1] + daily_onion[i-1][1] + daily_onion[i-2][1])/3.
					d3_temp = 0.555 * (d3_temp-32.)
				else:
					d3_temp = miss
				if daily_onion[i][2] != miss and daily_onion[i-1][2] != miss and daily_onion[i-2][2] != miss:
					d3_vpd = (daily_onion[i][2] + daily_onion[i-1][2] + daily_onion[i-2][2])/3.
				else:
					d3_vpd = miss
				spore_index = self.get_bot_sindx(d3_temp,d3_vpd)
				if spore_index == miss:
					bf = miss
				elif spore_index >= 50:
					bf = "SIP"
				else:
					bf = "IIP"
				botrytis[daily_onion[i][0][0:3]] = (spore_index,bf)
		except:
			print_exception()
		return botrytis	
			
	#--------------------------------------------------------------------------------------------		
	# calculate daily Blight Alert
	def get_ba(self,daily_onion,plant_date):
		balert = {}
		try:
			for i in range(len(daily_onion)-1,-1,-1):
				dt,dly_temp,dly_vpd,rh_cnt = daily_onion[i]
				if dly_temp != miss and dly_vpd != miss and rh_cnt != miss:
					the_date = DateTime.DateTime(*dt)
					ta_C = 0.555 * (dly_temp-32.)
					efi = -0.357+0.077*ta_C-0.0023*ta_C**2+0.0065*rh_cnt+0.0011*rh_cnt**2+0.0022*(ta_C*rh_cnt)
					day61 = ((the_date-plant_date).days) - 61
					day33 = ((the_date-plant_date).days) - 33
					if day61 < 47:
						ipi = 7.83*efi*(-0.0563+0.0626*day61-0.00067*day61**2.)
					else:
						ipi = 11.12*efi
					ba_ipi = ipi
					if day33 < 47:
						ipi = 7.83*efi*(-0.0563+0.0626*day33-0.00067*day33**2.)
					else:
						ipi = 11.12*efi
					mba_ipi = ipi
					balert[dt[0:3]] = (ba_ipi,mba_ipi)
				else:
					balert[dt[0:3]] = (miss,miss)
		except:
			print_exception()
		return balert
		
	#--------------------------------------------------------------------------------------------		
	# compute conditions for downy mildew
	def get_mildew(self,hourly_data):
		mildew = {}
		start_hour = 8
		end_hour = 8
		start = 0
		try:
			temp1_sum = 0.0
			temp1_cnt = 0
			temp2_sum = 0.0
			temp2_cnt = 0
			rhum_cnt = 0
			prcp_cnt = 0
			for dt,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags in hourly_data:
				hr = dt[3]
				if not start and hr != start_hour:	#read thru to beginning of first day
					continue
				else:
					start = 1			
				if hr >= 20 or hr <= 8:
					if temp != miss and temp1_cnt != miss:
						temp1_sum = temp1_sum+temp
						temp1_cnt = temp1_cnt + 1
					else:
						temp1_cnt = miss
				if hr >= 9 and hr <= 20:					# hr 8 is included after summarizing prev day (below)
					if temp != miss and temp2_cnt != miss:
						temp2_sum = temp2_sum+temp
						temp2_cnt = temp2_cnt + 1
					else:
						temp2_cnt = miss
				if hr >= 1 and hr <= 6:
					if prcp != miss and prcp_cnt != miss:
						if prcp > 0: prcp_cnt = prcp_cnt + 1
					else:
						prcp_cnt = miss
				if hr >= 2 and hr <= 6:
					if rhum != miss and rhum_cnt != miss:
						if rhum < 95: rhum_cnt = rhum_cnt + 1
					else:
						rhum_cnt = miss
					
				if hr == end_hour:
					if temp1_cnt == 13:
						temp1_avg = temp1_sum/temp1_cnt
					else:
						temp1_avg = miss
					if temp2_cnt == 13:
						temp2_avg = temp2_sum/temp2_cnt
					else:
						temp2_avg = miss
					if prcp_cnt != miss and rhum_cnt != miss and temp1_avg != miss and temp2_avg != miss:
						if prcp_cnt > 0 or rhum_cnt > 0 or temp1_avg < 40 or temp1_avg > 75 or temp2_avg > 75:
							mildew_status = "Unfavorable"
						else:
							mildew_status = "Favorable"
					else:
						mildew_status = "Unavailable"
					mildew[dt[0:3]] = mildew_status
					temp1_sum = 0.0
					temp1_cnt = 0
					temp2_sum = 0.0
					temp2_cnt = 0
					prcp_cnt = 0
					rhum_cnt = 0
					# last hour of day is same as first hour of next day
					if temp != miss:
						temp2_sum = temp2_sum+temp
						temp2_cnt = temp2_cnt + 1
					else:
						temp2_cnt = miss
						
	#		on last day, can do calculations even if last two hours for temp1 are not yet available
			if hr == 6 or hr == 7:
				if temp1_cnt <= 11:
					temp1_avg = temp1_sum/temp1_cnt
				else:
					temp1_avg = miss
				if temp2_cnt == 13:
					temp2_avg = temp2_sum/temp2_cnt
				else:
					temp2_avg = miss
				if prcp_cnt != miss and rhum_cnt != miss and temp1_avg != miss and temp2_avg != miss:
					if prcp_cnt > 0 or rhum_cnt > 0 or temp1_avg < 40 or temp1_avg > 75 or temp2_avg > 75:
						mildew_status = "Unfavorable"
					else:
						mildew_status = "Favorable"
				else:
					mildew_status = "Unavailable"
				mildew[dt[0:3]] = mildew_status
		except:
			print_exception()
		return mildew
	
	#--------------------------------------------------------------------------------------------		
	# calculate daily Alternaria risk
	def get_alt(self,daily_altvars):
		alter = {}
		aindex = []
		try:
			for i in range(len(daily_altvars)):
				dt,temp_max,temp_min,rh95_cnt,rh_min = daily_altvars[i]
				if temp_max != miss and temp_min != miss and rh95_cnt != miss and rh_min != miss:
					tmax_c = 0.555*(temp_max-32.)
					tmin_c = 0.555*(temp_min-32.)
					if tmax_c <= 30 and tmin_c <= 30 and tmax_c >= 13 and tmin_c >= 13:
						temp_index = 2
					elif tmax_c <= 30 and tmax_c <= 30 and tmax_c >= 7 and tmin_c >= 7:
						temp_index = 1
					else:
						temp_index = 0
					if rh95_cnt >= 8:
						nite_rh_index = 3
					elif rh95_cnt >= 4:
						nite_rh_index = 2
					else:
						nite_rh_index = 1
					if rh_min < 75:
						rel_rh_index = 2
					elif rh_min <= 85:
						rel_rh_index = 1
					else:
						rel_rh_index = 0
					aindex.append((dt,temp_index,nite_rh_index,rel_rh_index))
				else:
					aindex.append((dt,miss,miss,miss))
			for i in range(len(aindex)-1,1,-1):
				if aindex[i][1] != miss and aindex[i][2] != miss and \
				   aindex[i-1][1] != miss and aindex[i-1][2] != miss and \
				   aindex[i-2][1] != miss and aindex[i-2][2] != miss and \
				   aindex[i][3] != miss:
					day1 = aindex[i][1]+aindex[i][2]
					day2 = aindex[i-1][1]+aindex[i-1][2]
					day3 = aindex[i-2][1]+aindex[i-2][2]
					alt_index = (day1+day2+day3)/3. + aindex[i][3]
					if alt_index >= 5:
						alt_risk = 'High risk'
					else:
						alt_risk = 'Low risk'
				else:
					alt_index = miss
					alt_risk = 'Unavailable'
				alter[aindex[i][0][0:3]] = (alt_index,alt_risk)
		except:
			print_exception()
		return alter
		
	#--------------------------------------------------------------------------------------------		
	# compute daily avg temp, hours rh >=90, and vapor pressure deficit (used for Botrytis and Blight Alert)
	# "day" is 7am-6am
	def get_dly_onion(self,hourly_data):
		dly_onion = []
		end_hour = 6
		start = 0
		try:
			temp_sum = 0.0
			temp_cnt = 0.
			vpd_sum = 0.0
			vpd_cnt = 0.
			rh_cnt = 0.
			for dt,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags in hourly_data:
				if not start and dt[3] != end_hour+1:	#read thru to beginning of first day
					continue
				else:
					start = 1
				if temp != miss:
					temp_sum = temp_sum + temp
					temp_cnt = temp_cnt + 1
					if rhum != miss:
	#					calculate vpd
						tempK = (0.555)*(temp-32.) + 273.16
						esat = 10**(23.832241-5.02808*math.log10(tempK)-0.00000013816*10**(11.344-0.0303998*tempK)+\
							   0.008132801*10**(3.49149-1302.8844/tempK)-2949.076/tempK)
						dew_vapor =(rhum*esat)/100.
						vpd = esat-dew_vapor
						vpd_sum = vpd_sum + vpd
						vpd_cnt = vpd_cnt + 1
	#			count hours >= 90
				if rhum != miss and rh_cnt != miss:
					if rhum >= 90: rh_cnt = rh_cnt + 1
				else:
					rh_cnt = miss
				if dt[3] == end_hour:
					if temp_cnt > 0:
						dly_temp = temp_sum/temp_cnt
					else:
						dly_temp = miss
					if vpd_cnt > 0:
						dly_vpd = vpd_sum/vpd_cnt
					else:
						dly_vpd = miss
					dly_onion.append((dt,dly_temp,dly_vpd,rh_cnt))
					temp_sum = 0.0
					temp_cnt = 0.
					vpd_sum = 0.0
					vpd_cnt = 0.
					rh_cnt = 0.
		except:
			print_exception()
		return dly_onion
	
	#--------------------------------------------------------------------------------------------		
	# get daily parameters for Alternaria
	def get_dly_altvars(self,hourly_data):
		dly_altvar = []
		end_hour = 10
		minrh_end_hour = 12
		start_hour = 22
		start = 0
		try:
			temp_max = -1000.
			temp_min = 1000.
			rh95_cnt = 0.
			rh_min = 100.
			for dt,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags in hourly_data:
				the_hour = dt[3]
				if not start and the_hour != start_hour:	#read thru to beginning of first day
					continue
				else:
					start = 1
				if the_hour >= start_hour or the_hour <= end_hour:
					if temp != miss and temp_max != miss:
						if temp > temp_max: temp_max = copy.deepcopy(temp)
						if temp < temp_min: temp_min = copy.deepcopy(temp)
					else:
						temp_max = miss
						temp_min = miss
		#			count hours >= 95 and get min rh
					if rhum != miss and rh95_cnt != miss:
						if rhum >= 95: rh95_cnt = rh95_cnt + 1
						if rhum < rh_min: rh_min = copy.deepcopy(rhum)
					else:
						rh95_cnt = miss
						rh_min = miss
				elif the_hour > end_hour and the_hour <= minrh_end_hour:
					if rhum != miss and rh_min != miss:
						if rhum < rh_min: rh_min = copy.deepcopy(rhum)
					else:
						rh_min = miss
					if the_hour == minrh_end_hour:
						dly_altvar.append((dt,temp_max,temp_min,rh95_cnt,rh_min))
						temp_max = -9999.
						temp_min = 9999.
						rh95_cnt = 0.
						rh_min = 100.
		except:
			print_exception()
		return dly_altvar
		
	#--------------------------------------------------------------------------------------------		
	# add pop forecast
	def add_pops (self,smry_dict,end_date_dt,pops_list):
		try:
			day0 =  end_date_dt + DateTime.RelativeDate(hour=0,minute=0,second=0)
			fday1 = day0 + DateTime.RelativeDate(days=+1)
			fday2 = day0 + DateTime.RelativeDate(days=+2)
			fday3 = day0 + DateTime.RelativeDate(days=+3)
			fday4 = day0 + DateTime.RelativeDate(days=+4)
			fday5 = day0 + DateTime.RelativeDate(days=+5)

			smry_dict['pops']  = {}
			smry_dict['pops']['day0'] = {}
			smry_dict['pops']['pday1'] = {}
			smry_dict['pops']['pday2'] = {}
			smry_dict['pops']['fday1'] = {}
			smry_dict['pops']['fday2'] = {}
			smry_dict['pops']['fday3'] = {}
			smry_dict['pops']['fday4'] = {}
			smry_dict['pops']['fday5'] = {}
			smry_dict['pops']['day0']['am']  = miss
			smry_dict['pops']['pday1']['am'] = miss
			smry_dict['pops']['pday2']['am'] = miss
			smry_dict['pops']['fday1']['am'] = miss
			smry_dict['pops']['fday2']['am'] = miss
			smry_dict['pops']['fday3']['am'] = miss
			smry_dict['pops']['fday4']['am'] = miss
			smry_dict['pops']['fday5']['am'] = miss
			smry_dict['pops']['day0']['pm']  = miss
			smry_dict['pops']['pday1']['pm'] = miss
			smry_dict['pops']['pday2']['pm'] = miss
			smry_dict['pops']['fday1']['pm'] = miss
			smry_dict['pops']['fday2']['pm'] = miss
			smry_dict['pops']['fday3']['pm'] = miss
			smry_dict['pops']['fday4']['pm'] = miss
			smry_dict['pops']['fday5']['pm'] = miss

			# add pops for today and forecast next 5 days
			for theDate,qpf,pop in pops_list:
				if pop != miss:
					theDate_dt = DateTime.DateTime(*theDate) + DateTime.RelativeDate(hour=0,minute=0,second=0)
					if theDate[3] < 12:
						which = 'am'
					else:
						which = 'pm'
					if day0 == theDate_dt:
						smry_dict['pops']['day0'][which] = pop
					elif fday1 == theDate_dt:
						smry_dict['pops']['fday1'][which] = pop
					elif fday2 == theDate_dt:
						smry_dict['pops']['fday2'][which] = pop
					elif fday3 == theDate_dt:
						smry_dict['pops']['fday3'][which] = pop
					elif fday4 == theDate_dt:
						smry_dict['pops']['fday4'][which] = pop
					elif fday5 == theDate_dt:
						smry_dict['pops']['fday5'][which] = pop
		except:
			print_exception()
		return smry_dict
	
	#--------------------------------------------------------------------------------------------		
	def run_onion_dis(self,stn,month,day,product,accend,output):
		from ndfd.get_precip_forecast import get_precip_forecast
		now = DateTime.now()
		if not accend:
			accend = now
		smry_dict = {}
		smry_dict["output"] = output
		try:
			# obtain daily data
			year = accend.year
			plant_date = DateTime.DateTime(year,month,day,1)
			end_date_dt = accend
			pday3 = end_date_dt + DateTime.RelativeDate(days = -3, hour=1)
			if plant_date > end_date_dt:
				return newaCommon_io.errmsg('Plant date must be before date of interest')
##			midOctober = DateTime.DateTime(end_date_dt.year,10,15,23)
##			if end_date_dt > midOctober:
##				return newaDisease_io.onion_dis_dormant(smry_dict)
			if end_date_dt.year != now.year:
				smry_dict['this_year'] = False
				end_date_dt = end_date_dt + DateTime.RelativeDate(days = +6)
			else:
				smry_dict['this_year'] = True
			if plant_date > pday3:
				start_hrly = pday3
			else:
				start_hrly = plant_date
			hourly_data, download_time, station_name = self.get_hourly (stn, start_hrly, end_date_dt)
			smry_dict['last_time'] = download_time

			# add hourly forecast data
			if smry_dict['this_year']:
				start_fcst_dt = DateTime.DateTime(*download_time) + DateTime.RelativeDate(hours = +1)
				end_fcst_dt = end_date_dt + DateTime.RelativeDate(days = +6) + DateTime.RelativeDate(hour=23,minute=0,second=0.0)
				hourly_data = add_hrly_fcst(stn,hourly_data,start_fcst_dt,end_fcst_dt)
			else:
				start_fcst_dt = end_date_dt + DateTime.RelativeDate(hours = +1)
				end_fcst_dt = end_date_dt
				end_date_dt = end_date_dt + DateTime.RelativeDate(days = -6)
								
			if len(hourly_data) > 0:
				# compute daily values needed for later computations
				daily_onion = self.get_dly_onion(hourly_data)

				if product in ['onion_dis','onion_sbalog','onion_smbalog']:
					try:
						# calculate blight alert and modified blight alert index
						blight_alert = self.get_ba(daily_onion,plant_date)
					except:
						print 'Error: Skipping blight alert calculations.'
						blight_alert = []
						print_exception()
			
				if product in ['onion_dis','onion_onlog']:
					# compute Botrytis infection potential
					botrytis = self.get_botrytis(daily_onion)
					
					# compute downy mildew conditions
					mildew = self.get_mildew(hourly_data)
					
					#compute alternaria risk
					daily_altvar =  self.get_dly_altvars(hourly_data)
					alternaria = self.get_alt(daily_altvar)

				if product == 'onion_dis':
					if len(blight_alert) > 0 or len(alternaria) > 0 or len(botrytis) > 0 or len(mildew) > 0:
### new summary table dictionary creation
						last_day = end_date_dt + DateTime.RelativeDate(hour=23,minute=0,second=0.0)
						first_day = last_day + DateTime.RelativeDate(days = -6)
						bot_favorable_count = 0
						bot_spore_count = 0
						bot_day_count = 0
						ba_favorable_count = 0
						ba_ipi_count = 0
						ba_day_count = 0
						mba_favorable_count = 0
						mba_ipi_count = 0
						mba_day_count = 0
						dm_favorable_count = 0
						dm_day_count = 0
						pb_favorable_count = 0
						pb_val_count = 0
						pb_day_count = 0
						theDate = first_day
						while theDate <= last_day:
							dkey = (theDate.year,theDate.month,theDate.day)
							if botrytis.has_key(dkey):
								spore_index, bf = botrytis[dkey]
								if spore_index != miss:
									bot_day_count += 1
									bot_spore_count += spore_index					
									if spore_index >= 50:
										bot_favorable_count += 1
							if blight_alert.has_key(dkey):
								ba_ipi, mba_ipi = blight_alert[dkey]
								if ba_ipi != miss:
									ba_day_count += 1
									ba_ipi_count += ba_ipi
									if ba_ipi >= 7:
										ba_favorable_count += 1
								if mba_ipi != miss:
									mba_day_count += 1
									mba_ipi_count += mba_ipi
									if mba_ipi >= 7:
										mba_favorable_count += 1
							if mildew.has_key(dkey):
								status = mildew[dkey]
								if status != 'Unavailable':
									dm_day_count += 1
									if status == 'Favorable':
										dm_favorable_count += 1					
							if alternaria.has_key(dkey):
								pbval, pbrisk = alternaria[dkey]
								if pbval != miss:
									pb_day_count += 1
									pb_val_count += pbval
									if pbval >= 5.7:
										pb_favorable_count += 1					
							theDate = theDate + DateTime.RelativeDate(days = +1)
	
						if bot_day_count == 7:
							smry_dict["botrytis_days"] = bot_favorable_count
						else:
							smry_dict["botrytis_days"] = '-'
						if bot_day_count > 0:
							smry_dict["botrytis_avg"] = int(round(bot_spore_count/bot_day_count))
						else:
							smry_dict["botrytis_avg"] = '-'
						smry_dict["botrytis_today"] = int(round(botrytis[last_day.year,last_day.month,last_day.day][0]))
						if ba_day_count == 7:
							smry_dict["blightalert_days"] = ba_favorable_count
						else:
							smry_dict["blightalert_days"] = '-'
						if ba_day_count > 0:
							smry_dict["blightalert_avg"] = round(ba_ipi_count/ba_day_count, 2)
						else:
							smry_dict["blightalert_avg"] = '-'
						smry_dict["blightalert_today"] = round(blight_alert[last_day.year,last_day.month,last_day.day][0], 2)
						if mba_day_count == 7:
							smry_dict["modblightalert_days"] = mba_favorable_count
						else:
							smry_dict["modblightalert_days"] = '-'
						if mba_day_count > 0:
							smry_dict["modblightalert_avg"] = round(mba_ipi_count/mba_day_count, 2)
						else:
							smry_dict["modblightalert_avg"] = '-'
						smry_dict["modblightalert_today"] = round(blight_alert[last_day.year,last_day.month,last_day.day][1], 2)
						if dm_day_count == 7:
							smry_dict["downymildew_days"] = dm_favorable_count
						else:
							smry_dict["downywildew_days"] = '-'
						smry_dict["downymildew_today"] = mildew[last_day.year,last_day.month,last_day.day]
						if pb_day_count == 7:
							smry_dict["purpleblotch_days"] = pb_favorable_count
						else:
							smry_dict["purpleblotch_days"] = '-'
						if pb_day_count > 0:
							smry_dict["purpleblotch_avg"] = round(pb_val_count/pb_day_count, 1)
						else:
							smry_dict["purpleblotch_avg"] = '-'
						smry_dict["purpleblotch_today"] = round(alternaria[last_day.year,last_day.month,last_day.day][0], 1)

						smry_dict['day0'] = {}
						smry_dict['day0']['date'] = '%s %d' % (month_names[last_day.month][0:3],last_day.day)
						smry_dict['day0']['ymd'] = (last_day.year,last_day.month,last_day.day)
						for dy in range(1,6):
							theDate = last_day + DateTime.RelativeDate(days = +dy)
							index = 'fday' + str(dy)
							smry_dict[index] = '%s %d' % (month_names[theDate.month][0:3],theDate.day)
							index = 'ymd' + str(dy)
							smry_dict[index] = (theDate.year,theDate.month,theDate.day)
							index = 'botrytis_fday' + str(dy)
							smry_dict[index] = int(round(botrytis[theDate.year,theDate.month,theDate.day][0]))
							index = 'blightalert_fday' + str(dy)
							smry_dict[index] = round(blight_alert[theDate.year,theDate.month,theDate.day][0], 2)
							index = 'modblightalert_fday' + str(dy)
							smry_dict[index] = round(blight_alert[theDate.year,theDate.month,theDate.day][1], 2)
							index = 'downymildew_fday' + str(dy)
							smry_dict[index] = mildew[theDate.year,theDate.month,theDate.day]
							index = 'purpleblotch_fday' + str(dy)
							smry_dict[index] = round(alternaria[theDate.year,theDate.month,theDate.day][0], 1)
						# get 12-hour pops
						pops_list = get_precip_forecast (stn,end_date_dt + DateTime.RelativeDate(hour=0,minute=0,second=0.0),end_fcst_dt)
						smry_dict = self.add_pops(smry_dict,end_date_dt,pops_list)
						
						last_prcp_dt = start_hrly + DateTime.RelativeDate(hours = -1)
						for i in range(len(hourly_data), 0, -1):
							theTime,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags = hourly_data[i-1]
							temp_eflag, prcp_eflag, pop12_eflag, rhum_eflag, wspd_eflag, wdir_eflag, srad_eflag, st4i_eflag = eflags
							if prcp != miss and prcp_eflag != "P":
								last_prcp_dt = DateTime.DateTime(*theTime)
								break
						smry_dict["last_prcp"] = last_prcp_dt
						
						return newaDisease_io.onion_dis_html(station_name,blight_alert,plant_date,alternaria,botrytis,mildew,smry_dict)
### end new section
					else:
						return self.nodata(stn, station_name, plant_date, end_date_dt)
				elif product == 'onion_onlog':
					if len(alternaria) > 0 or len(botrytis) > 0 or len(mildew) > 0:
						return newaDisease_io.onion_onlog_html(station_name,download_time,alternaria,botrytis,mildew)
					else:
						return self.nodata(stn, station_name, plant_date, end_date_dt)
				elif product == 'onion_sbalog':
					if len(blight_alert) > 0 :
						return newaDisease_io.onion_balog_html(station_name,download_time,blight_alert,plant_date,'')
					else:
						return self.nodata(stn, station_name, plant_date, end_date_dt)
				elif product == 'onion_smbalog':
					if len(blight_alert) > 0 :
						return newaDisease_io.onion_balog_html(station_name,download_time,blight_alert,plant_date,'Modified')
					else:
						return self.nodata(stn, station_name, plant_date, end_date_dt)
				else:
					return newaCommon_io.errmsg('Unknown product')
			else:
				return self.nodata(stn, station_name, plant_date, end_date_dt)
		except:
			print_exception()
			return newaCommon_io.errmsg('Unable to complete request')
	
	#--------------------------------------------------------------------------------------------		
	def run_onion_maggot (self,stn,accend,output):
		try:
			now = DateTime.now()
			if not accend:
				accend = now
			smry_dict = {'output':output}
			# obtain daily data
			end_date_dt = accend
			midOctober = DateTime.DateTime(end_date_dt.year,10,15,23)
			if end_date_dt > midOctober:
				 return newaDisease_io.onion_maggot_dormant(smry_dict)
				 
			if end_date_dt.year != now.year:
				smry_dict['this_year'] = False
				end_date_dt = end_date_dt + DateTime.RelativeDate(days = +6)
			else:
				smry_dict['this_year'] = True
				
			# obtain hourly and daily data
			start_date_dt = DateTime.DateTime(end_date_dt.year,1,1,1)		
			hourly_data, daily_data, download_time, station_name, avail_vars = self.get_hddata2 (stn, start_date_dt, end_date_dt)

			# add forecast data
			if smry_dict['this_year']:
				start_fcst_dt = DateTime.DateTime(*download_time) + DateTime.RelativeDate(hours = +1)
				end_fcst_dt = end_date_dt + DateTime.RelativeDate(days = +6)
				hourly_data = add_hrly_fcst(stn,hourly_data,start_fcst_dt,end_fcst_dt)
				daily_data = hrly_to_dly(hourly_data)
			else:
				start_fcst_dt = end_date_dt + DateTime.RelativeDate(hours = +1)
				end_fcst_dt = end_date_dt	
				end_date_dt = end_date_dt + DateTime.RelativeDate(days = -6)

#			daily_data, station_name = self.get_daily (stn, start_date_dt, end_date_dt)
#			start_fcst_dt = DateTime.DateTime(*daily_data[-1][0]) + DateTime.RelativeDate(days = +1)
#			end_fcst_dt = end_date_dt + DateTime.RelativeDate(days = +5)
#			daily_data = add_dly_fcst(stn,daily_data,start_fcst_dt,end_fcst_dt)
			
			if len(daily_data) > 0:
				# base 40degF GDD 
				degday_dict = self.degday_calcs (daily_data,start_date_dt,end_fcst_dt,'dd40', "accum")

				if len(degday_dict) > 0:
					# get dates for gdd table
					smry_dict = self.setup_dates(smry_dict, end_date_dt)
					# get dd for days of interest (including forecast)
					smry_dict = self.add_ddays(smry_dict,degday_dict,start_date_dt,end_date_dt)
					return newaDisease_io.onion_maggot_html(station_name,smry_dict,degday_dict)
				else:
					return self.nodata(stn, station_name, start_date_dt, end_date_dt)
			else:
				return self.nodata (stn, station_name, start_date_dt, end_date_dt)
		except:
			print_exception()

#--------------------------------------------------------------------------------------------		
class Alfalfa (Base):
	def run_alf_weev (self,stn):
		try:
			# obtain daily data
			end_date_dt = DateTime.now()
			start_date_dt = DateTime.DateTime(end_date_dt.year,1,1,1)		
			daily_data, station_name = self.get_daily (stn, start_date_dt, end_date_dt)
			
			if len(daily_data) > 0:
				# base 48 GDD 
				daily_degday = self.degday_calcs (daily_data,start_date_dt,end_date_dt,'dd48')
			else:
				return self.nodata (stn, station_name, start_date_dt, end_date_dt)

			if len(daily_degday) > 0:
				return newaDisease_io.alf_weev_html(station_name,daily_degday)
			else:
				return self.nodata(stn, station_name, start_date_dt, end_date_dt)
		except:
			print_exception()

#--------------------------------------------------------------------------------------------		
class Tomato (Pottom):
	# determine wet periods - need 3 consecutive dry hours to end wetting period
	def get_wetting (self,hourly_data,stn):
		wet_periods = []
		try:
			wet_hrs = 0
			dry_hrs = 0
			for theTime,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags in hourly_data:
				# Adjust relative humidity for icao stations and forecast data
				if (eflags[3] == "F" or (len(stn) == 4 and stn[0:1].upper() == 'K')) and rhum != miss:
					rhum = rhum/(rhum*0.0047+0.53)
				if lwet == miss and rhum != miss:
					if rhum >= 90 or prcp > 0.00:
						lwet = 60
					else:
						lwet = 0
				if lwet != miss:
					last_hour = theTime
				if lwet > 0:
					if dry_hrs > 0:
						wet_hrs = wet_hrs + dry_hrs
						dry_hrs = 0
					wet_hrs = wet_hrs + 1
					if wet_hrs == 1: 
						wet_start = (DateTime.DateTime(*theTime) + DateTime.RelativeDate(hours=-1,minute=1)).tuple()[:5]
				else:
					if wet_hrs > 0: 
						if dry_hrs == 0:
							wet_end = (DateTime.DateTime(*theTime) + DateTime.RelativeDate(hours=-1,minute=0)).tuple()[:5]
						dry_hrs = dry_hrs+1
						if dry_hrs == 3:
							wet_periods.append((wet_start,wet_end))
							wet_hrs = 0
							dry_hrs = 0
	#		end period in progress
			if wet_hrs > 0:
				wet_end = (DateTime.DateTime(*theTime) + DateTime.RelativeDate(hours=-(dry_hrs+1),minute=1)).tuple()[:5]
## changed this line to above 11/16/2015 -kle				if dry_hrs == 0: wet_end = miss
				wet_periods.append((wet_start,wet_end))
		except:
			print_exception()
		return wet_periods, last_hour
		
	#--------------------------------------------------------------------------------------------		
	# split wet periods longer than 24 hours at 12 noon
	def refine_wetperiods (self,wet_periods,download_time):
		refined_periods = []
		try:
			for i in range(len(wet_periods)):
				ws,we = wet_periods[i][0],wet_periods[i][1]
				ws_dt = DateTime.DateTime(*ws)
				we_dt = DateTime.DateTime(*we)
				num_hrs = round((we_dt-ws_dt).hours,0)
					
				if num_hrs <= 24:
					refined_periods.append(wet_periods[i])
				else:
					while num_hrs > 24:
						new_start = wet_periods[i][0]
						ns_dt = DateTime.DateTime(*new_start)
						if ns_dt.hour >= 12:
							ne_dt = ns_dt + DateTime.RelativeDate(days=+1,hour=12,minute=0)
						else:
							ne_dt = ns_dt + DateTime.RelativeDate(hour=12,minute=0)
						new_end = ne_dt.tuple()[:5]
						refined_periods.append((new_start,new_end))
						wet_periods[i] = ((new_end[0],new_end[1],new_end[2],new_end[3],1),wet_periods[i][1])
						if we != miss:
							num_hrs = round((we_dt-ne_dt).hours,0)
						else:
							num_hrs = round((dl_dt-ne_dt).hours,0)
					else:
						refined_periods.append(wet_periods[i])
		except:
			print_exception()
		return refined_periods
	
	#--------------------------------------------------------------------------------------------	
	# gather weather data for wet periods
	def get_weather (self,hourly_data, wet_periods):
		wet_data = []
		wet_data_short = []
		try:
			accum_sv = 0
			wet_hrs = 0
			temp_sum = 0.
			temp_cnt = 0.
			prcp_sum = 0.
			prcp_cnt = 0.
			thePeriod = 0
			ws,we = wet_periods[thePeriod]
			ws_dt = DateTime.DateTime(*ws) + DateTime.RelativeDate(hours=+1,minute=0)
			we_dt = DateTime.DateTime(*we)
			for theTime,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags in hourly_data:
				theTime_dt = DateTime.DateTime(*theTime)
				if theTime_dt >= ws_dt and theTime_dt <= we_dt:
					wet_hrs = wet_hrs+1
					if temp != miss:
						temp_sum = temp_sum + temp
						temp_cnt = temp_cnt + 1
					if prcp != miss:
						prcp_sum = prcp_sum + prcp
						prcp_cnt = prcp_cnt + 1
				if theTime_dt == we_dt:
					if temp_cnt > 0:
						temp_ave = temp_sum/temp_cnt
						temp_ave = int(round(temp_ave,0))
					else:
						temp_ave = miss
					if prcp_cnt > 0:
						prcp_tot = prcp_sum
					else:
						prcp_tot = miss
					dsv = self.get_tomato_severity (temp_ave,wet_hrs)
					if dsv != miss: accum_sv = accum_sv + dsv
					wet_data.append((self.format_date(ws),self.format_date(we),wet_hrs,temp_ave,prcp_tot,dsv,accum_sv))
					wet_data_short.append((DateTime.DateTime(*ws),DateTime.DateTime(*we),accum_sv))
					wet_hrs = 0
					temp_sum = 0.
					temp_cnt = 0.
					prcp_sum = 0.
					prcp_cnt = 0.	
					thePeriod = thePeriod+1
					if thePeriod < len(wet_periods):
						ws,we = wet_periods[thePeriod]
						ws_dt = DateTime.DateTime(*ws) + DateTime.RelativeDate(hours=+1,minute=0)
						we_dt = DateTime.DateTime(*we)
					else:
						break
	#		end period in progress
			if wet_hrs > 0:
				if temp_cnt > 0:
					temp_ave = temp_sum/temp_cnt
					temp_ave = int(round(temp_ave,0))
				else:
					temp_ave = miss
				if prcp_cnt > 0:
					prcp_tot = prcp_sum
				else:
					prcp_tot = miss
				dsv = self.get_tomato_severity (temp_ave,wet_hrs)
				if dsv != miss: accum_sv = accum_sv + dsv
				wet_data.append((self.format_date(ws),self.format_date(we),wet_hrs,temp_ave,prcp_tot,dsv,accum_sv))				
				wet_data_short.append((DateTime.DateTime(*ws),DateTime.DateTime(*we),accum_sv))
		except:
			print_exception()
		return wet_data, wet_data_short
	
	#--------------------------------------------------------------------------------------------		
	# tomcast severity value
	def get_tomato_severity (self,temp,wthrs):
		tomcast_dict = {(55,63): [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3],
						(64,68): [0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 4, 4],
						(69,77): [0, 0, 0, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4],
						(78,85): [0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 4, 4]}
		dsv = miss
		try:
			if temp == miss or wthrs == miss:
				dsv = miss
			elif temp < 55:
				dsv = 0
			elif temp > 85:
				dsv = 0
			else:
				for tt in tomcast_dict.keys():
					if temp >= tt[0] and temp <= tt[1]:
						if wthrs <= 24:
							dsv = tomcast_dict[tt][wthrs]
						else:
							dsv = tomcast_dict[tt][24]
						break
		except:
			print_exception()
		return dsv
	
	#--------------------------------------------------------------------------------------------		
	# format date/time, converting hour in 24-hour clock to 12-hour clock with am/pm
	def format_date (self,datehr):
		datehr_str = ''
		try:
			if datehr == miss:
				datehr_str = 'in progress'
			else:
				yr,mn,dy,hr,mt = datehr
				hr,ampm = self.format_time(hr)
				datehr_str = '%d/%d/%d %d:%02d %s' % (mn,dy,yr,hr,mt,ampm)
		except:
			print_exception()
		return datehr_str
		
	#--------------------------------------------------------------------------------------------		
	# do tomcast calculations
	def run_tomcast(self, stn, station_name, hourly_data, smry_dict, log_dict, start_date, end_date_dt):
		# pick out wet periods
		initial_wet_periods, last_hour = self.get_wetting(hourly_data, stn)
		# refine wet periods (break into chunks no longer than 24 hours)
		wet_periods = self.refine_wetperiods(initial_wet_periods,log_dict['download_time'])
		if len(wet_periods) > 0:
			# get weather data for each (refined) wet period
			log_dict['wet_data'], wet_data_short = self.get_weather (hourly_data, wet_periods)
			# get the accum sv for today and next 6 days
			smry_dict['daily_accums'] = self.get_daily_accum(wet_data_short, end_date_dt, last_hour)
		else:
			return self.nodata(stn, station_name, start_date, end_date_dt)
		return smry_dict, log_dict, last_hour
	
	#--------------------------------------------------------------------------------------------		
	def run_tomato_for (self,subtype,stn,year,month,day,emerg_dt,cultivar,accend,output):
		try:
			simcastD = {}
			bliteD = {}
			smry_dict = {'output': output}
			log_dict = {}

			if accend:
				end_date_dt = accend + DateTime.RelativeDate(hour=12,minute=0,second=0)
			else:
				end_date_dt = DateTime.now()
				year = end_date_dt.year
			start_date = DateTime.DateTime(year,month,day,10)
			
			if start_date > end_date_dt:
				return newaCommon_io.errmsg('Cannot have future transplant or fungicide dates')
				
			# obtain all hourly data for station
			end_fcst_dt = end_date_dt + DateTime.RelativeDate(days = +6) + DateTime.RelativeDate(hour=23,minute=0,second=0)
			hourly_data, download_time, station_name, avail_vars = self.get_hourly2 (stn, start_date, end_fcst_dt)
			log_dict = {'download_time':download_time, 'avail_vars':avail_vars}
			start_fcst_dt = DateTime.DateTime(*download_time) + DateTime.RelativeDate(hours = +1)
			# append any available forecast data after end of observed data
			if end_fcst_dt >= start_fcst_dt:
				hourly_data = add_hrly_fcst(stn,hourly_data,start_fcst_dt,end_fcst_dt)
			# get last (forecast) value with precip amt
			smry_dict['lastqpf'] = self.getLastPrecip(hourly_data)


	# this is tomcast
			if len(hourly_data) > 0: 
				smry_dict, log_dict, last_hour = self.run_tomcast(stn, station_name, hourly_data, smry_dict, log_dict, start_date, end_date_dt)
			else:
				return self.nodata(stn, station_name, start_date, end_date_dt)
	# end tomcast
				
	# this is blitecast
			if subtype == 'blitecast':
				if emerg_dt < start_date:
					# need more data than we did for Tomcast
					start_date = emerg_dt
					if start_date > end_date_dt:
						return newaCommon_io.errmsg('Cannot have future emergence dates')
					hourly_data, download_time, station_name, avail_vars = self.get_hourly2 (stn, start_date, end_fcst_dt)
					if end_fcst_dt >= start_fcst_dt:
						hourly_data = add_hrly_fcst(stn,hourly_data,start_fcst_dt,end_fcst_dt)					
				if len(hourly_data) > 0:
					bliteD = self.run_blitecast(stn, hourly_data, bliteD, end_date_dt, last_hour)
						
	# this is simcast
			elif subtype == 'simcast':
				simcastD = self.run_simcast(stn, station_name, simcastD, cultivar, month, day, year, start_date, end_date_dt, download_time)					
			# end simcast
			
			# send off data to results page
			return newaDisease_io.tomato_for_html(station_name,smry_dict,log_dict,simcastD,bliteD)
		except:
			print_exception()
			return newaCommon_io.errmsg('Unable to complete request')

#--------------------------------------------------------------------------------------------					
class Grape (Base):
	# determine wet and dry periods from hourly data provided
	def get_wetting (self,hourly_data):
		wet_periods = []
		try:
			wet_hrs = 0
			last_wet = miss
			temp_sum = 0.
			temp_cnt = 0.
			prcp_sum = 0.
			prcp_cnt = 0.
			for theTime,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags in hourly_data:
				if lwet >=  30:
					wet_hrs = wet_hrs + 1
					last_wet = theTime
					if wet_hrs == 1: 
						wet_start = theTime
					if temp != miss:
						temp_sum = temp_sum + temp
						temp_cnt = temp_cnt + 1
					if prcp != miss:
						prcp_sum = prcp_sum + prcp
						prcp_cnt = prcp_cnt + 1
				elif wet_hrs > 0: 
					wet_end = last_wet
					if temp_cnt > 0:
						temp_ave = temp_sum/temp_cnt
					else:
						temp_ave = miss
					if prcp_cnt > 0:
						prcp_tot = prcp_sum
					else:
						prcp_tot = miss
					phomopsis = self.get_phomop(wet_hrs,temp_ave,prcp_tot)
					blackrot = self.get_blackrot(wet_hrs,temp_ave,prcp_tot)
					wet_periods.append((wet_start,wet_end,wet_hrs,temp_ave,prcp_tot,phomopsis,blackrot))
					wet_hrs = 0
					last_wet = miss
					temp_sum = 0.
					temp_cnt = 0.
					prcp_sum = 0.
					prcp_cnt = 0.					
	#		end period in progress
			if wet_hrs > 0:
				wet_end = miss
				if temp_cnt > 0:
					temp_ave = temp_sum/temp_cnt
				else:
					temp_ave = miss
				if prcp_cnt > 0:
					prcp_tot = prcp_sum
				else:
					prcp_tot = miss
				phomopsis = self.get_phomop(wet_hrs,temp_ave,prcp_tot)
				blackrot = self.get_blackrot(wet_hrs,temp_ave,prcp_tot)
				wet_periods.append((wet_start,wet_end,wet_hrs,temp_ave,prcp_tot,phomopsis,blackrot))
		except:
			print_exception()
		return wet_periods
		
	#--------------------------------------------------------------------------------------------		
	# determine whether or not there was phomopsis infection during this wet period
	def get_phomop (self,wet_hrs,temp_ave,prcp_tot):
		phomop_dict = { 46: 13, 47: 12, 48: 12, 49: 12, 50: 12,
						51: 11, 52: 11, 53: 11, 54: 11, 55: 10, 56: 10, 57: 10, 58: 9, 59: 9, 60: 8,
						61:  8, 62:  7, 63:  7, 64:  7, 65:  6, 66:  6, 67:  6, 68: 6, 69: 5, 70: 5,
						71:  5, 72:  5, 73:  5, 74:  5, 75:  5, 76:  5, 77:  5, 78: 5, 79: 5, 80: 5,
						81:  6, 82:  6, 83:  6, 84:  6, 85:  6, 86:  8 }
		phomopsis = "Unknown"
		try:
			if temp_ave == miss or wet_hrs == miss or prcp_tot == miss:
				phomopsis = "-----"
			elif temp_ave < 46:
				phomopsis = "No infect; temp<46"
			elif temp_ave > 86:
				phomopsis = "Unknown infect; temp>86"
			else:
				int_temp = int(round(temp_ave,0))
				if prcp_tot >= 0.01 and wet_hrs >= phomop_dict[int_temp]:
					phomopsis = "Infection"
				else:
					phomopsis = "No infection"
		except:
			print_exception()
		return phomopsis
		
	#--------------------------------------------------------------------------------------------		
	# determine whether or not there was a blackrot infection during this wet period
	def get_blackrot (self,wet_hrs,temp_ave,prcp_tot):
		blackrot_dict = { 50: 24, 55: 12, 60: 9, 65: 8, 70: 7, 75: 7, 80: 6, 85: 9, 90: 12 }
		blackrot = "Unknown"
		try:
			if temp_ave == miss or wet_hrs == miss or prcp_tot == miss:
				blackrot = "-----"
			elif temp_ave < 50:
				blackrot = "No infect; temp<50"
			elif temp_ave > 90:
				blackrot = "Unknown infect; temp>90"
			else:
				# round temp to nearest 5 degrees
				temp_nearest10 = int(round(temp_ave/10.,0)*10.)
				if temp_ave-temp_nearest10 >= 2.5:
					temp_nearest5 = temp_nearest10 + 5
				elif temp_nearest10-temp_ave > 2.5:
					temp_nearest5 = temp_nearest10 - 5
				else:
					temp_nearest5 = temp_nearest10
				if prcp_tot >= 0.01 and wet_hrs >= blackrot_dict[temp_nearest5]:
					blackrot = "Infection"
				else:
					blackrot = "No infection"
		except:
			print_exception()
		return blackrot
		
	#--------------------------------------------------------------------------------------------		
	# compute daily and accumulated gdd and powdery mildew
	def get_dly_grape(self,daily_data,base):
		dly_grape = []
		try:
			accum_gdd = 0.
			for dt,tave,tmax,tmin,prcp,lwet,rhum,wspd,srad,st4a,st4x,st4n,dflags in daily_data:
				if tmax != miss and tmin != miss:
					dly_gdd = ((tmax+tmin)/2.) - base
					if dly_gdd < 0: dly_gdd = 0.
					if accum_gdd != miss:
						accum_gdd = accum_gdd + dly_gdd
				else:
					dly_gdd = miss
					accum_gdd = miss
				# powdery mildew:
				if prcp != miss and tave != miss:
					if prcp >= 0.10 and tave >= 50:
						pm = "Infection"
					else:
						pm = "None"	
				else:
					pm = "Not available"
	
				dly_grape.append((dt,dly_gdd,accum_gdd,pm))
		except:
			print_exception()
		return dly_grape
			
	#--------------------------------------------------------------------------------------------	
	def run_grape_dis (self,stn,year):
		try:
			if year:
				end_date_dt = DateTime.DateTime(year,10,31)
			else:
				end_date_dt = DateTime.now()
			start_date_dt = DateTime.DateTime(end_date_dt.year,3,1,1)	#Leave this March 1			
			
			# obtain all hourly and daily data for station
			hourly_data,daily_data,download_time,station_name = self.get_hddata (stn,start_date_dt,end_date_dt)
			if len(hourly_data) > 0: 
				
				# pick out wet periods
				wet_periods = self.get_wetting(hourly_data)
				
				# compute gdd
				daily_grape = self.get_dly_grape(daily_data,50.)
				
				if len(wet_periods) > 0:
					# convert to html and write to file for Wet Period Log (single station)
					return newaDisease_io.grape_dis_html(station_name,download_time,wet_periods,daily_grape)
			else:
				return self.nodata(stn, station_name, start_date_dt, end_date_dt)
		except:
			print_exception()
			return newaCommon_io.errmsg('Unable to complete request')

#--------------------------------------------------------------------------------------------					
def process_help (request,path):
	try:
		smry_type = None
#	 	retrieve input
		if path is None:
			if request and request.form:
				try:
					smry_type = request.form['type'].strip()
				except:
					print_exception()
					raise program_exit('Error processing request')
			else:
				return newaCommon_io.errmsg('Error processing form; check input')
		elif path[0] in ['cabbage_maggot']:
			try:
				smry_type = path[0]
			except IndexError:
				raise program_exit('Error processing request - index error')
			except:
				print_exception()
				raise program_exit('Error processing request')
		else:
			return newaCommon_io.errmsg('Error processing input')
			
# 		send input to appropriate routine
		if smry_type == 'cabbage_maggot':
##			return newaDisease_io.helppage([
##				("About Cabbage Maggot","/cabbage_maggot_about.htm"),
##				("How to Use Cabbage Maggot Forecasts","/cabbage_maggot_howto.htm"),
##				("Degree Day Accumulations for Cabbage Maggot Stages","/cabbage_maggot_dd.htm")
##				])
			pass
		else:
			return newaCommon_io.errmsg('Error processing input')
	except program_exit,msg:
		print msg
		return newaCommon_io.errmsg('Error processing input')
	except:
		print_exception()
		return newaCommon_io.errmsg('Unexpected error')

#--------------------------------------------------------------------------------------------					
def process_input (request,path):
	try:
#	 	retrieve input
		emonth = None
		eday = None
		if path is None:
			if request and request.form:
				try:
					smry_type = request.form['type'].strip()
					if request.form.has_key('stn'):
						stn = request.form['stn'].strip()
					else:
						stn = None
					if request.form.has_key('month'):
						month = int(request.form['month'])
					else:
						month = None
					if request.form.has_key('year'):
						year = int(request.form['year'])
					else:
						year = None
					if request.form.has_key('day'):
						day = int(request.form['day'])
					else:
						day = None
					if request.form.has_key('accend'):
						try:
							mm,dd,yy = request.form['accend'].split("/")
							accend = DateTime.DateTime(int(yy),int(mm),int(dd),23)
						except:
							accend = None
					else:
						accend = None
					if request.form.has_key('emonth'):
						emonth = int(request.form['emonth'])
					else:
						emonth = None
					if request.form.has_key('eday'):
						eday = int(request.form['eday'])
					else:
						eday = None
					if request.form.has_key('subtype'):
						subtype = request.form['subtype']
					else:
						subtype = None
					if request.form.has_key('potato_cultivar'):
						potato_cultivar = request.form['potato_cultivar']
					else:
						potato_cultivar = None
					if request.form.has_key('tomato_cultivar'):
						tomato_cultivar = request.form['tomato_cultivar']
					else:
						tomato_cultivar = None
					if request.form.has_key('cultivar'):
						cultivar = request.form['cultivar']
					else:
						cultivar = None
					if request.form.has_key('crop'):
						crop = request.form['crop']
					else:
						crop = None
					if request.form.has_key('output'):
						output = request.form['output']
					else:
						output = 'tab'
				except:
					print_exception()
					raise program_exit('Error processing request')
			else:
				return newaCommon_io.errmsg('Error processing form; check input')
		elif path[0] in ('apple_fb','alf_weev','cabbage_maggot','onion_maggot'):
			try:
				output = 'standalone'
				smry_type = path[0]
				if len(path) > 1:
					stn = path[1]
				else:
					stn = None
				year = None
				month = None
				day = None
				accend = None
			except IndexError:
				raise program_exit('Error processing request - index error')
			except:
				print_exception()
				raise program_exit('Error processing request')
		elif path[0] in ('apple_lw','grape_dis'):
			try:
				smry_type = path[0]
				if len(path) > 2:
					stn = path[1]
					year = int(path[2])
				elif len(path) > 1:
					stn = path[1]
					year = None
				else:
					stn = None
					year = None
				month = None
				day = None
			except IndexError:
				raise program_exit('Error processing request - index error')
			except:
				print_exception()
				raise program_exit('Error processing request')
		elif path[0] in ('potato_lb','potato_pdays'):
			try:
				output = 'standalone'
				smry_type = path[0]
				if len(path) > 1:
					stn = path[1]
					year = int(path[2])
					month = int(path[3])
					day = int(path[4])
				else:
					return newaCommon_io.errmsg('Error processing input')
			except IndexError:
				raise program_exit('Error processing request - index error')
			except:
				print_exception()
				raise program_exit('Error processing request')
		elif path[0] in ('onion_dis','onion_sbalog','onion_smbalog','onion_onlog'):
			try:
				smry_type = path[0]
				if len(path) > 1:
					stn = path[1]
					year = int(path[2])
					if len(path) > 3:
						month = int(path[3])
						day = int(path[4])
					else:
						month = 4
						day = 21
				else:
					return newaCommon_io.errmsg('Error processing input')
			except IndexError:
				raise program_exit('Error processing request - index error')
			except:
				print_exception()
				raise program_exit('Error processing request')
		elif path[0] in ('tomato_for','potato_for'):
			output = 'standalone'
			try:
				smry_type = path[0]
				if len(path) > 1:
					stn = path[1]
					year = int(path[2])
					if len(path) > 3:
						month = int(path[3])
						if len(path) > 4:
							day = int(path[4])
						else:
							day = 1
					else:
						month = 5
						day = 1
				else:
					return newaCommon_io.errmsg('Error processing input')
			except IndexError:
				raise program_exit('Error processing request - index error')
			except:
				print_exception()
				raise program_exit('Error processing request')
		else:
			return newaCommon_io.errmsg('Error processing input')
			
		if year and year == 9999:
			now = DateTime.now()
			year = now.year
		
		if emonth and eday:
			emerg_dt = DateTime.DateTime(year,int(emonth),int(eday),10)
		else:
			emerg_dt = None

# 		send input to appropriate routine
		if stn:
			if smry_type == 'apple_lw':
				return Apple().run_apple_lw(stn,year)
			elif smry_type == 'apple_fb':
				return Apple().run_apple_fb(stn)
			elif smry_type == 'potato_lb':
				return Potato().run_potato_lb(stn,year,month,day,output)
			elif smry_type == 'potato_simcast':
				if crop == 'tomato':
					cultivar = tomato_cultivar
				else:
					cultivar = potato_cultivar
				return Potato().run_potato_simcast(stn,year,month,day,cultivar)
			elif smry_type == 'potato_lb_old':
				return Potato().run_potato_lb_old(stn,year,month,day)
			elif smry_type == 'potato_pdays':
				return Potato().run_potato_pdays(stn,year,month,day,output)
			elif smry_type in ['onion_dis','onion_onlog','onion_sbalog','onion_smbalog']:
				return Onion().run_onion_dis(stn,month,day,smry_type,accend,output)
			elif smry_type == 'tomato_for':
				return Tomato().run_tomato_for(subtype,stn,year,month,day,emerg_dt,cultivar,accend,output)
			elif smry_type == 'potato_for':
				return Potato().run_potato_for(subtype,stn,year,month,day,emerg_dt,cultivar,accend,output)
			elif smry_type == 'grape_dis':
				return Grape().run_grape_dis(stn,year)
			elif smry_type == 'alf_weev':
				return Alfalfa().run_alf_weev(stn)
			elif smry_type == 'cabbage_maggot':
				return Cabbage().run_cabbage_maggot(stn,accend)
			elif smry_type == 'onion_maggot':
				return Onion().run_onion_maggot(stn,accend,output)
			else:
				return newaCommon_io.errmsg('Error processing form; check input')
		else:
			return newaCommon_io.errmsg('Error processing form; select station')
	except program_exit,msg:
		print msg
		return newaCommon_io.errmsg('Error processing form; check input')
	except:
		print_exception()
		return newaCommon_io.errmsg('Unexpected error')
