#!/usr/local/bin/python

import sys, copy, math
from mx import DateTime
from print_exception import print_exception
import newaModel_io
import newaCommon.newaCommon_io
from newaCommon.newaCommon import *

miss = -999
month_names = ["","January","February","March","April","May","June","July","August","September","October","November","December"]

biofixfile = '/newa/static/apple_biofix.txt'

class program_exit (Exception):
	pass

#--------------------------------------------------------------------------------------------		
class Models(Base):
	# compute distance between two locations
	def lldis (self,lat1,lon1,lat2,lon2):
		dtom = 69.057
		dtor = math.pi/180.
		rtod = 180./math.pi
		if abs(lat1-lat2) < 0.01:
			if abs(lon1-lon2) < 0.01:
				dist = 0.0
			else:
				dist = abs(lon1-lon2)
		else:
			lat1 = lat1*dtor
			lon1 = lon1*dtor
			lat2 = lat2*dtor
			lon2 = lon2*dtor
			dist = rtod*(math.acos(math.sin(lat1)*math.sin(lat2)+math.cos(lat1)*math.cos(lat2)*math.cos(lon2-lon1)))
	#	convert degrees to miles
		dist = dist*dtom
		return dist
	
	#--------------------------------------------------------------------------------------------		
	# find latitude and longitude of station	
	def get_latlon (self,station_id,id_type):
		lat = miss
		lon = miss
		ucan = ucanCallMethods.general_ucan(user_name="NewaQuixote")
		query = ucan.get_query()
		try:
			r = query.getUcanFromIdAsSeq(station_id,id_type)
			if len(r) > 0:
				ucanid = r[-1].ucan_id
				info = query.getInfoForUcanIdAsSeq(ucanid,())
				fields = ucanCallMethods.NameAny_to_dict(info[-1].fields)
				lat = fields['lat']
				lon = fields['lon']
			query.release()
		except:
			query.release()
			print_exception()
		return lat,lon

	#--------------------------------------------------------------------------------------------		
	# add hourly forecast data to end of hourly_data
	def add_hrly_fcst(self,stn,hourly_data,start_fcst_dt,end_fcst_dt,estp=False):
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
	def add_dly_fcst(self,stn,daily_data,start_fcst_dt,end_fcst_dt):
		try:
			from ndfd.get_daily_forecast import get_daily_forecast
			forecast_data = get_daily_forecast(stn,start_fcst_dt,end_fcst_dt)
			daily_data = daily_data+forecast_data
		except:
			print_exception()
		return daily_data	
	
	#--------------------------------------------------------------------------------------------		
	def hrly_to_dly (self,hourly_data):
		daily_data = []
		lt_end_hour = 23
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
	# calculate hourly integrated degree days from hourly temperature values
	def hidd_calcs (self,hourly_data,start_date,end_date,dd_type):
		degday_data = []
		try:
			if dd_type == 'dd4714hi':
				base = 47.14
			else:
				return degday_data
			dly_sum = 0.
			dly_msg = 0.
			start_date = start_date + DateTime.RelativeDate(hour=0,minute=0,second=0)
			end_date = end_date + DateTime.RelativeDate(hour=23,minute=59,second=59)
			for theTime,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags in hourly_data:
				temp_eflag, prcp_eflag, lwet_eflag, rhum_eflag, wspd_eflag, wdir_eflag, srad_eflag, st4i_eflag = eflags
				this_date = DateTime.DateTime(*theTime)
				if this_date >= start_date and this_date <= end_date:
					if temp != miss:
						if temp > base: dly_sum = dly_sum + (temp-base)
					else:
						dly_msg = dly_msg+1
		#			save daily values
					if theTime[3] == 23:
						if dly_msg < 2: 
							dly_dd = dly_sum/(24.-dly_msg)
						else:
							dly_dd = miss
						degday_data.append((theTime[:3],miss,miss,dly_dd,miss))
						dly_sum = 0.
						dly_msg = 0
		#	get last partial day
			if theTime[3] != 23:
				dly_dd = dly_sum/(24.-dly_msg)
				degday_data.append((theTime[:3],miss,miss,dly_dd,miss))
				
		except:
			print 'Error calculating degree days'
			print_exception()
		return degday_data

	#--------------------------------------------------------------------------------------------		
	#	accum degree days up to threshold (biofix_dd) or specified end date
	def accum_degday (self, temp_data, start_date_dt, end_date_dt, dd_type, biofix_dd, stn, station_name):
		bf_date = None
		ddaccum = 0.
		ddmiss = 0
		try:
			if dd_type == 'dd4714hi':	# hourly integrated degree days (temp_data is hourly)
				degday_dict = self.hidd_calcs(temp_data, start_date_dt, end_date_dt, dd_type)
			else:						# all others (temp_data is daily)
				degday_dict = self.degday_calcs(temp_data, start_date_dt, end_date_dt, dd_type, "accum")
			if degday_dict:
				for i in range(len(degday_dict)):
					dly_dd = degday_dict[i][3]
					if dly_dd != miss:
						ddaccum = ddaccum + dly_dd
					else:
						ddmiss = ddmiss + 1							
					if round(ddaccum,0) >= biofix_dd:
						bf_date = DateTime.DateTime(degday_dict[i][0][0],degday_dict[i][0][1],degday_dict[i][0][2],0)
						break
			else:
				return self.nodata(stn, station_name, start_date_dt, end_date_dt)
		except:
			print_exception()
		return bf_date, round(ddaccum,0), ddmiss

	#--------------------------------------------------------------------------------------------		
	# determine wet and dry periods from hourly data provided
	def get_wet_periods (self,hourly_data):
		wet_periods = []
		try:
			wet_hrs = 0
			last_wet = miss
			rain_start = miss
			temp_sum = 0.	#entire period
			temp_cnt = 0.	#entire period
			temp_sum2 = 0.	#after rain
			temp_cnt2 = 0.	#after rain
			prcp_sum = 0.
			prcp_cnt = 0.
			for theTime,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags in hourly_data:
				temp_eflag, prcp_eflag, pop12_eflag, rhum_eflag, wspd_eflag, wdir_eflag, srad_eflag, st4i_eflag = eflags
				# don't use precip estimated from pop12
				if prcp_eflag == "P":
					prcp = miss			
				if lwet == miss and rhum != miss:
					if rhum >= 90 or prcp > 0.00:
						lwet = 60
					else:
						lwet = 0
				if lwet >=  30 or prcp > 0.00:
					wet_hrs = wet_hrs + 1
					last_wet = theTime
					if wet_hrs == 1: 
						wet_start = theTime
					if prcp > 0.00 and rain_start == miss:
						rain_start = theTime
						temp_sum2 = 0.
						temp_cnt2 = 0.
					if temp != miss:
						temp_sum = temp_sum + temp
						temp_cnt = temp_cnt + 1
						temp_sum2 = temp_sum2 + temp
						temp_cnt2 = temp_cnt2 + 1
					if prcp != miss:
						prcp_sum = prcp_sum + prcp
						prcp_cnt = prcp_cnt + 1
				elif wet_hrs > 0: 
					wet_end = last_wet
					if temp_cnt > 0:
						temp_ave = temp_sum/temp_cnt
					else:
						temp_ave = miss
					if temp_cnt2 > 0:
						temp_ave2 = temp_sum2/temp_cnt2
					else:
						temp_ave2 = miss
					if prcp_cnt > 0:
						prcp_tot = prcp_sum
					else:
						prcp_tot = miss
					wet_periods.append((wet_start,wet_end,wet_hrs,temp_ave,prcp_tot,rain_start,temp_cnt2,temp_ave2))
					wet_hrs = 0
					last_wet = miss
					rain_start = miss
					temp_sum = 0.
					temp_cnt = 0.
					temp_sum2 = 0.
					temp_cnt2 = 0.
					prcp_sum = 0.
					prcp_cnt = 0.					
	#		end period in progress
			if wet_hrs > 0:
				wet_end = theTime
				if temp_cnt > 0:
					temp_ave = temp_sum/temp_cnt
				else:
					temp_ave = miss
				if temp_cnt2 > 0:
					temp_ave2 = temp_sum2/temp_cnt2
				else:
					temp_ave2 = miss
				if prcp_cnt > 0:
					prcp_tot = prcp_sum
				else:
					prcp_tot = miss
				wet_periods.append((wet_start,wet_end,wet_hrs,temp_ave,prcp_tot,rain_start,temp_cnt2,temp_ave2))
		except:
			print_exception()
		return wet_periods
		
	#--------------------------------------------------------------------------------------------
	# combine wet periods into infection events
	def combine_wet_periods (self,wet_periods):
		combined_events = []
		try:
			look_for_start = 1
			combo_start = miss
			combo_end = miss
			last_end_dt = miss
			combo_hrs = 0.
			temp_sum = 0.
			prcp_sum = 0.
			combo = 0
			for start,end,length,temp,prcp,rain_start,rain_length,rain_temp in wet_periods:
#				print '----- Evaluate -----',start,end,length,temp,prcp,rain_start,rain_length,rain_temp
				if look_for_start:
					if prcp > 0.00:
#						print 'New wet period starts:',rain_start
						look_for_start = 0
						combo = 0
						combo_start = rain_start		#first period in combo must start with rain
						combo_end = end
						combo_hrs = combo_hrs + rain_length
						temp_sum = temp_sum + (rain_temp*rain_length)
						prcp_sum = prcp_sum + prcp
						last_end_dt = DateTime.DateTime(*end)
					else:
#						print 'Skip event - does not start with rain'
						continue
				else:
					this_start_dt = DateTime.DateTime(*start)
					dry_period = (this_start_dt-last_end_dt).hours - 1
#					print 'Checking for combination; dry period=',dry_period
					if dry_period <= 24:
#						print 'Dry period less than or equal to 24 hours; combine through',end
						combo = 1
						combo_end = end
						combo_hrs = combo_hrs + length
						temp_sum = temp_sum + (temp*length)
						prcp_sum = prcp_sum + prcp
						last_end_dt = DateTime.DateTime(*end)
					if dry_period > 24 or prcp == 0.00:
#						print 'End of event found; save stored event as',combo_start,combo_end,combo_hrs,(temp_sum/combo_hrs),prcp_sum
						combined_events.append((combo_start,combo_end,combo_hrs,(temp_sum/combo_hrs),prcp_sum,combo))
						if dry_period > 24:
							#process current
							if prcp > 0.00:
#								print 'New wet period starts:',rain_start
								look_for_start = 0
								combo = 0
								combo_start = rain_start		#first period in combo must start with rain
								combo_end = end
								combo_hrs = rain_length
								temp_sum = (rain_temp*rain_length)
								prcp_sum = prcp
								last_end_dt = DateTime.DateTime(*end)
							else:
#								print 'This period does not start with rain; skip'
								continue
						else:
#							print 'Last period in combination above; move on'
							#already processed current
							look_for_start = 1
							combo_start = miss
							combo_end = miss
							last_end_dt = miss
							combo_hrs = 0.
							temp_sum = 0.
							prcp_sum = 0.
							combo = 0
			if combo_hrs > 0:		#event in progress
#				print 'Saving event in progress at end of file as',combo_start,combo_end,combo_hrs,(temp_sum/combo_hrs),prcp_sum				
				combined_events.append((combo_start,combo_end,combo_hrs,(temp_sum/combo_hrs),prcp_sum,combo))
		except:
			print_exception()
		return combined_events

	#--------------------------------------------------------------------------------------------	
	# get biofix date from file 
	def get_biofix (self,stn,fix,year):
		fix_date = None
		try:
			outfil = open(biofixfile[0:-4]+'_%s'%year+biofixfile[-4:],'r')
			for line in outfil.readlines():
				line = line.strip()
				key,val = line.split(',')
				id,typ = key.split('-')
				if id == stn and typ == fix:
					mm,dd = val.split('/')
					fix_date = DateTime.DateTime(year,int(mm),int(dd))
					break
			outfil.close
		except:
#			print 'Error obtaining biofix from file'
			pass
		return fix_date
		
	#--------------------------------------------------------------------------------------------	
	# get biofix for nearest station
	def nearest_biofix (self, base_stn, id_type, fixtype, year):
		closest = (999,None,None)
		try:
			lat0,lon0 = self.get_latlon (base_stn,id_type)
			fixfile = open(biofixfile[0:-4]+'_%s'%year+biofixfile[-4:],'r')
			for line in fixfile.readlines():
				line = line.strip()
				key,val = line.split(',')
				id,typ = key.split('-')
				if typ == fixtype:
					tlat,tlon = self.get_latlon (id,'newa')
					dist = self.lldis (lat0,lon0,tlat,tlon)
					if dist < closest[0]: 
						mm,dd = val.split('/')
						fix_date = DateTime.DateTime(year,int(mm),int(dd))
						closest = (dist,id,fix_date)
			fixfile.close
		except:
#			print 'Error obtaining nearest biofix from file'
			pass
		return closest
		
	#--------------------------------------------------------------------------------------------	
	# get time of last qpf in hourly data
	def getLastPrecip(self, hourly_data):
		last_pcpn = None
		for theTime,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags in hourly_data:
			if prcp != miss:
				last_pcpn = theTime
		return last_pcpn


#--------------------------------------------------------------------------------------------		
class Apple (Base,Models):

	# calculate wetness events from hourly values
	def wetness_event_calcs (self,hourly_data,start_date,end_date,start_fcst,stn,estimate="no"):
		wetness_data = []
		try:
			dly_rain = 0.
			dly_rain_msg = 0
			dly_lwet = 0.
			dly_lwet_msg = 0
			dly_dew = 0.
			dly_dew_msg = 0
			start_date = start_date + DateTime.RelativeDate(days=+1)		#start wetness calcs day after biofix
			start_date = start_date + DateTime.RelativeDate(hour=0,minute=0,second=0)
			end_date = end_date + DateTime.RelativeDate(hour=23,minute=59,second=59)
			for theTime,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags in hourly_data:
				temp_eflag, prcp_eflag, lwet_eflag, rhum_eflag, wspd_eflag, wdir_eflag, srad_eflag, st4i_eflag = eflags
				########################################################################
				# only thing different when estimate is "yes" - always estimate lwet   #
				########################################################################
				if estimate == "yes":
					if rhum == miss:
						lwet = miss
					elif rhum >= 90 or prcp > 0.00:
						lwet = 60
					else:
						lwet = 0
				else:
					if lwet == miss and rhum != miss:
						if rhum >= 90 or prcp > 0.00:
							lwet = 60
						else:
							lwet = 0
				this_date = DateTime.DateTime(*theTime)
				if this_date >= start_date and this_date <= end_date:
					if prcp != miss:
						dly_rain = dly_rain+prcp
					else:
						dly_rain_msg = dly_rain_msg+1
					if lwet != miss:
						if lwet > 0: dly_lwet = dly_lwet+1
					else:
						dly_lwet_msg = dly_lwet_msg+1
						
					# determine if there was dew formation		
					#  First, adjust relative humidity for icao stations and forecast values for all stations
					if (this_date >= start_fcst or (len(stn) == 4 and stn[0:1].upper() == 'K')) and rhum != miss:
						rh = rhum/(rhum*0.0047+0.53)
					else:
						rh = rhum
					# determine dewpoint temperature
					dwpt = self.calc_dewpoint(temp,rh)
					# estimate dew formation if difference between temp and dewpoint is <= 3 degrees and it is not raining
					if dwpt != miss and temp != miss:
						if temp-dwpt <= 3 and prcp == 0.00:
							dly_dew = dly_dew+1
					else:
						dly_dew_msg = dly_dew_msg+1
						
		#			save daily values
					if theTime[3] == 23:
						if dly_rain_msg >= 5: dly_rain = miss
						if dly_lwet_msg >= 2: dly_lwet = miss
						if dly_dew_msg >= 2: dly_dew = miss
						wetness_data.append((theTime[:3],dly_rain,dly_lwet,dly_dew))
						dly_rain = 0.
						dly_rain_msg = 0
						dly_lwet = 0.
						dly_lwet_msg = 0
						dly_dew = 0.
						dly_dew_msg = 0
		#	get last partial day
			if theTime[3] != 23:
				wetness_data.append((theTime[:3],dly_rain,dly_lwet,dly_dew))
		except:
			print 'Error calculating degree hours'
			print_exception()
		return wetness_data
		
	# calculate wetness events from hourly values - include more variables in the return
	def wetness_moreevent_calcs (self,hourly_data,start_date,end_date,start_fcst,stn,estimate="no"):
		wetness_data = []
		try:
			dly_rain = 0.
			dly_rain_msg = 0
			dly_lwet = 0.
			dly_lwet_msg = 0
			dly_dew = 0.
			dly_dew_msg = 0
			cnt_rhum = 0
			max_rhum = -999
			min_rhum = 999
			dly_rhum_msg = 0
###			dly_temp = 0.
			dly_temp_cnt = 0
			dly_maxt = -9999
			dly_mint = 9999
##			start_date = start_date + DateTime.RelativeDate(days=+1)		#start wetness calcs day after biofix
			start_date = start_date + DateTime.RelativeDate(hour=0,minute=0,second=0)
			end_date = end_date + DateTime.RelativeDate(hour=23,minute=59,second=59)
			for theTime,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags in hourly_data:
				temp_eflag, prcp_eflag, lwet_eflag, rhum_eflag, wspd_eflag, wdir_eflag, srad_eflag, st4i_eflag = eflags
				########################################################################
				# only thing different when estimate is "yes" - always estimate lwet   #
				########################################################################
				if estimate == "yes":
					if rhum == miss:
						lwet = miss
					elif rhum >= 90 or prcp > 0.00:
						lwet = 60
					else:
						lwet = 0
				else:
					if lwet == miss and rhum != miss:
						if rhum >= 90 or prcp > 0.00:
							lwet = 60
						else:
							lwet = 0
				this_date = DateTime.DateTime(*theTime)
				if this_date >= start_date and this_date <= end_date:
					if prcp != miss:
						dly_rain = dly_rain+prcp
					else:
						dly_rain_msg = dly_rain_msg+1
					if lwet != miss:
						if lwet > 0: dly_lwet = dly_lwet+1
					else:
						dly_lwet_msg = dly_lwet_msg+1
						
					# determine if there was dew formation		
					#  First, adjust relative humidity for icao stations and forecast values for all stations
					if (this_date >= start_fcst or (len(stn) == 4 and stn[0:1].upper() == 'K')) and rhum != miss:
						rh = rhum/(rhum*0.0047+0.53)
					else:
						rh = rhum
					# determine dewpoint temperature
					dwpt = self.calc_dewpoint(temp,rh)
					# estimate dew formation if difference between temp and dewpoint is <= 3 degrees and it is not raining
					if dwpt != miss and temp != miss:
						if temp-dwpt <= 3 and prcp == 0.00:
							dly_dew = dly_dew+1
					else:
						dly_dew_msg = dly_dew_msg+1
					if temp != miss:
						if temp > dly_maxt:
							dly_maxt = copy.deepcopy(temp)
						if temp < dly_mint:
							dly_mint = copy.deepcopy(temp)
###						dly_temp += temp
						dly_temp_cnt += 1
					if rhum != miss:
						if rhum > 90: cnt_rhum += 1
						if rhum > max_rhum: max_rhum = copy.deepcopy(rhum)
						if rhum < min_rhum: min_rhum = copy.deepcopy(rhum)
					else:
						dly_rhum_msg += 1
						
		#			save daily values
					if theTime[3] == 23:
						if dly_rain_msg >= 5: dly_rain = miss
						if dly_lwet_msg >= 2: dly_lwet = miss
						if dly_dew_msg >= 2: dly_dew = miss
						if dly_rhum_msg >= 2:
							cnt_rhum = miss
							max_rhum = miss
							min_rhum = miss
						if dly_temp_cnt >= 22:
							avg_temp = (dly_maxt + dly_mint) / 2.0
###							avg_temp = dly_temp / dly_temp_cnt
						else:
							avg_temp = miss
						wetness_data.append((theTime[:3],dly_rain,dly_lwet,dly_dew,max_rhum,min_rhum,cnt_rhum,avg_temp))
						dly_rain = 0.
						dly_rain_msg = 0
						dly_lwet = 0.
						dly_lwet_msg = 0
						dly_dew = 0.
						dly_dew_msg = 0
						cnt_rhum = 0
						max_rhum = -999
						min_rhum = 999
						dly_rhum_msg = 0
###						dly_temp = 0.
						dly_temp_cnt = 0
						dly_maxt = -9999
						dly_mint = 9999
		#	get last partial day
			if theTime[3] != 23:
				if dly_temp_cnt > 0:
					avg_temp = (dly_maxt + dly_mint) / 2.0
###					avg_temp = dly_temp / dly_temp_cnt
				else:
					avg_temp = miss
				wetness_data.append((theTime[:3],dly_rain,dly_lwet,dly_dew,max_rhum,min_rhum,cnt_rhum,avg_temp))
		except:
			print 'Error calculating wetness more events'
			print_exception()
		return wetness_data		

	# calculate wetting variables and avg temp during wet hours from hourly values
	def wettemp_event_calcs (self,hourly_data,start_date,end_date,start_fcst,stn,estimate="no"):
		wetness_data = []
		try:
			dly_rain = 0.
			dly_rain_msg = 0
			dly_lwet = 0.
			dly_lwet_msg = 0
			dly_dew = 0.
			dly_dew_msg = 0
			dly_temp = 0.
			dly_temp_cnt = 0.
			dly_temp_msg = 0
			dly_rhum_cnt = 0
			dly_rhum_msg = 0
			start_date = start_date + DateTime.RelativeDate(days=+1)		#start wetness calcs day after biofix
			start_date = start_date + DateTime.RelativeDate(hour=0,minute=0,second=0)
			end_date = end_date + DateTime.RelativeDate(hour=23,minute=59,second=59)
			for theTime,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags in hourly_data:
				temp_eflag, prcp_eflag, lwet_eflag, rhum_eflag, wspd_eflag, wdir_eflag, srad_eflag, st4i_eflag = eflags
				########################################################################
				# only thing different when estimate is "yes" - always estimate lwet   #
				########################################################################
				if estimate == "yes":
					if rhum == miss:
						lwet = miss
					elif rhum >= 90 or prcp > 0.00:
						lwet = 60
					else:
						lwet = 0
				else:
					if lwet == miss and rhum != miss:
						if rhum >= 90 or prcp > 0.00:
							lwet = 60
						else:
							lwet = 0
				this_date = DateTime.DateTime(*theTime)
				if this_date >= start_date and this_date <= end_date:
					if prcp != miss:
						dly_rain = dly_rain+prcp
					else:
						dly_rain_msg = dly_rain_msg+1
					if lwet != miss:
						if lwet > 0:
							dly_lwet = dly_lwet+1
							if temp != miss:
								dly_temp = dly_temp + temp
								dly_temp_cnt = dly_temp_cnt + 1
							else:
								dly_temp_msg = dly_temp_msg + 1
					else:
						dly_lwet_msg = dly_lwet_msg + 1
						dly_temp_msg = dly_temp_msg + 1
						
					# determine if there was dew formation		
					#  First, adjust relative humidity for icao stations and forecast values for all stations
					if (this_date >= start_fcst or (len(stn) == 4 and stn[0:1].upper() == 'K')) and rhum != miss:
						rh = rhum/(rhum*0.0047+0.53)
					else:
						rh = rhum
					# determine dewpoint temperature
					dwpt = self.calc_dewpoint(temp,rh)
					# estimate dew formation if difference between temp and dewpoint is <= 3 degrees and it is not raining
					if dwpt != miss and temp != miss:
						if temp-dwpt <= 3 and prcp == 0.00:
							dly_dew = dly_dew+1
					else:
						dly_dew_msg = dly_dew_msg+1
					if rhum != miss:
						if rhum >= 90: dly_rhum_cnt += 1
					else:
						dly_rhum_msg += 1
						
		#			save daily values
					if theTime[3] == 23:
						if dly_rain_msg >= 5: dly_rain = miss
						if dly_lwet_msg >= 2: dly_lwet = miss
						if dly_dew_msg >= 2: dly_dew = miss
						if dly_rhum_msg >= 2: dly_rhum_cnt = miss
						if dly_temp_msg >= 2 or dly_temp_cnt == 0:
							dly_temp = miss
						else:
							dly_temp = dly_temp / dly_temp_cnt
						
						wetness_data.append((theTime[:3],dly_rain,dly_lwet,dly_dew,dly_temp,dly_rhum_cnt))
						dly_rain = 0.
						dly_rain_msg = 0
						dly_lwet = 0.
						dly_lwet_msg = 0
						dly_dew = 0.
						dly_dew_msg = 0
						dly_temp = 0.
						dly_temp_cnt = 0.
						dly_temp_msg = 0
						dly_rhum_cnt = 0
						dly_rhum_msg = 0
		#	get last partial day
			if theTime[3] != 23:
				wetness_data.append((theTime[:3],dly_rain,dly_lwet,dly_dew,dly_rhum_cnt))
		except:
			print 'Error calculating degree hours'
			print_exception()
		return wetness_data

	#--------------------------------------------------------------------------------------------		
	# add wetness events to dictionary
	def add_wetness (self,smry_dict,wetness,start_date_dt,end_date_dt):
		try:
			day0 =  end_date_dt + DateTime.RelativeDate(hour=0,minute=0,second=0)
			pday1 = day0 + DateTime.RelativeDate(days=-1)
			pday2 = day0 + DateTime.RelativeDate(days=-2)
			fday1 = day0 + DateTime.RelativeDate(days=+1)
			fday2 = day0 + DateTime.RelativeDate(days=+2)
			fday3 = day0 + DateTime.RelativeDate(days=+3)
			fday4 = day0 + DateTime.RelativeDate(days=+4)
			fday5 = day0 + DateTime.RelativeDate(days=+5)

			smry_dict['day0']['wetness']  = (miss,miss,miss)
			smry_dict['pday1']['wetness'] = (miss,miss,miss)
			smry_dict['pday2']['wetness'] = (miss,miss,miss)
			smry_dict['fday1']['wetness'] = (miss,miss,miss)
			smry_dict['fday2']['wetness'] = (miss,miss,miss)
			smry_dict['fday3']['wetness'] = (miss,miss,miss)
			smry_dict['fday4']['wetness'] = (miss,miss,miss)
			smry_dict['fday5']['wetness'] = (miss,miss,miss)

			# add wetness events for last three days, forecast next 5 days
			for theDate,dly_rain,dly_lwet,dly_dew,max_rhum,min_rhum,cnt_rhum,avg_temp in wetness:
				theDate_dt = DateTime.DateTime(*theDate) + DateTime.RelativeDate(hour=0,minute=0,second=0)
				if day0 == theDate_dt:
					smry_dict['day0']['wetness'] =  (dly_rain, dly_lwet, dly_dew, max_rhum, min_rhum, cnt_rhum, avg_temp)
				elif pday1 == theDate_dt:
					smry_dict['pday1']['wetness'] = (dly_rain, dly_lwet, dly_dew, max_rhum, min_rhum, cnt_rhum, avg_temp)
				elif pday2 == theDate_dt:
					smry_dict['pday2']['wetness'] = (dly_rain, dly_lwet, dly_dew, max_rhum, min_rhum, cnt_rhum, avg_temp)
				elif fday1 == theDate_dt:
					smry_dict['fday1']['wetness'] = (dly_rain, dly_lwet, dly_dew, max_rhum, min_rhum, cnt_rhum, avg_temp)
				elif fday2 == theDate_dt:
					smry_dict['fday2']['wetness'] = (dly_rain, dly_lwet, dly_dew, max_rhum, min_rhum, cnt_rhum, avg_temp)
				elif fday3 == theDate_dt:
					smry_dict['fday3']['wetness'] = (dly_rain, dly_lwet, dly_dew, max_rhum, min_rhum, cnt_rhum, avg_temp)
				elif fday4 == theDate_dt:
					smry_dict['fday4']['wetness'] = (dly_rain, dly_lwet, dly_dew, max_rhum, min_rhum, cnt_rhum, avg_temp)
				elif fday5 == theDate_dt:
					smry_dict['fday5']['wetness'] = (dly_rain, dly_lwet, dly_dew, max_rhum, min_rhum, cnt_rhum, avg_temp)
		except:
			print_exception()
		return smry_dict

	#--------------------------------------------------------------------------------------------		
	# add wetness events (including avgtemp during wet hours) to dictionary
	def add_wettemp (self,smry_dict,wetness,start_date_dt,end_date_dt):
		try:
			day0 =  end_date_dt + DateTime.RelativeDate(hour=0,minute=0,second=0)
			pday1 = day0 + DateTime.RelativeDate(days=-1)
			pday2 = day0 + DateTime.RelativeDate(days=-2)
			fday1 = day0 + DateTime.RelativeDate(days=+1)
			fday2 = day0 + DateTime.RelativeDate(days=+2)
			fday3 = day0 + DateTime.RelativeDate(days=+3)
			fday4 = day0 + DateTime.RelativeDate(days=+4)
			fday5 = day0 + DateTime.RelativeDate(days=+5)

			smry_dict['day0']['wetness']  = (miss,miss,miss,miss)
			smry_dict['pday1']['wetness'] = (miss,miss,miss,miss)
			smry_dict['pday2']['wetness'] = (miss,miss,miss,miss)
			smry_dict['fday1']['wetness'] = (miss,miss,miss,miss)
			smry_dict['fday2']['wetness'] = (miss,miss,miss,miss)
			smry_dict['fday3']['wetness'] = (miss,miss,miss,miss)
			smry_dict['fday4']['wetness'] = (miss,miss,miss,miss)
			smry_dict['fday5']['wetness'] = (miss,miss,miss,miss)

			# add wetness events for last three days, forecast next 5 days
			for theDate,dly_rain,dly_lwet,dly_dew,dly_temp,dly_rhum in wetness:
				theDate_dt = DateTime.DateTime(*theDate) + DateTime.RelativeDate(hour=0,minute=0,second=0)
				if day0 == theDate_dt:
					smry_dict['day0']['wetness'] =  (dly_rain, dly_lwet, dly_dew, dly_temp, dly_rhum)
				elif pday1 == theDate_dt:
					smry_dict['pday1']['wetness'] = (dly_rain, dly_lwet, dly_dew, dly_temp, dly_rhum)
				elif pday2 == theDate_dt:
					smry_dict['pday2']['wetness'] = (dly_rain, dly_lwet, dly_dew, dly_temp, dly_rhum)
				elif fday1 == theDate_dt:
					smry_dict['fday1']['wetness'] = (dly_rain, dly_lwet, dly_dew, dly_temp, dly_rhum)
				elif fday2 == theDate_dt:
					smry_dict['fday2']['wetness'] = (dly_rain, dly_lwet, dly_dew, dly_temp, dly_rhum)
				elif fday3 == theDate_dt:
					smry_dict['fday3']['wetness'] = (dly_rain, dly_lwet, dly_dew, dly_temp, dly_rhum)
				elif fday4 == theDate_dt:
					smry_dict['fday4']['wetness'] = (dly_rain, dly_lwet, dly_dew, dly_temp, dly_rhum)
				elif fday5 == theDate_dt:
					smry_dict['fday5']['wetness'] = (dly_rain, dly_lwet, dly_dew, dly_temp, dly_rhum)
		except:
			print_exception()
		return smry_dict

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

			smry_dict['day0']['pops']  = {}
			smry_dict['pday1']['pops'] = {}
			smry_dict['pday2']['pops'] = {}
			smry_dict['fday1']['pops'] = {}
			smry_dict['fday2']['pops'] = {}
			smry_dict['fday3']['pops'] = {}
			smry_dict['fday4']['pops'] = {}
			smry_dict['fday5']['pops'] = {}
			smry_dict['day0']['pops']['am']  = miss
			smry_dict['pday1']['pops']['am'] = miss
			smry_dict['pday2']['pops']['am'] = miss
			smry_dict['fday1']['pops']['am'] = miss
			smry_dict['fday2']['pops']['am'] = miss
			smry_dict['fday3']['pops']['am'] = miss
			smry_dict['fday4']['pops']['am'] = miss
			smry_dict['fday5']['pops']['am'] = miss
			smry_dict['day0']['pops']['pm']  = miss
			smry_dict['pday1']['pops']['pm'] = miss
			smry_dict['pday2']['pops']['pm'] = miss
			smry_dict['fday1']['pops']['pm'] = miss
			smry_dict['fday2']['pops']['pm'] = miss
			smry_dict['fday3']['pops']['pm'] = miss
			smry_dict['fday4']['pops']['pm'] = miss
			smry_dict['fday5']['pops']['pm'] = miss

			# add pops for today and forecast next 5 days
			for theDate,qpf,pop in pops_list:
				pop = int(pop)
				if pop != miss:
					theDate_dt = DateTime.DateTime(*theDate) + DateTime.RelativeDate(hour=0,minute=0,second=0)
					if theDate[3] < 12:
						which = 'am'
					else:
						which = 'pm'
					if day0 == theDate_dt:
						smry_dict['day0']['pops'][which] = pop
					elif fday1 == theDate_dt:
						smry_dict['fday1']['pops'][which] = pop
					elif fday2 == theDate_dt:
						smry_dict['fday2']['pops'][which] = pop
					elif fday3 == theDate_dt:
						smry_dict['fday3']['pops'][which] = pop
					elif fday4 == theDate_dt:
						smry_dict['fday4']['pops'][which] = pop
					elif fday5 == theDate_dt:
						smry_dict['fday5']['pops'][which] = pop
		except:
			print_exception()
		return smry_dict

	#--------------------------------------------------------------------------------------------		
	# add average temps
	def add_temprain (self,smry_dict,end_date_dt,daily_data,getpops=True):
		try:
			day0 =  end_date_dt + DateTime.RelativeDate(hour=0,minute=0,second=0)
			pday1 = day0 + DateTime.RelativeDate(days=-1)
			pday2 = day0 + DateTime.RelativeDate(days=-2)
			fday1 = day0 + DateTime.RelativeDate(days=+1)
			fday2 = day0 + DateTime.RelativeDate(days=+2)
			fday3 = day0 + DateTime.RelativeDate(days=+3)
			fday4 = day0 + DateTime.RelativeDate(days=+4)
			fday5 = day0 + DateTime.RelativeDate(days=+5)

			smry_dict['day0']['avgtemp']  = miss
			smry_dict['pday1']['avgtemp'] = miss
			smry_dict['pday2']['avgtemp'] = miss
			smry_dict['fday1']['avgtemp'] = miss
			smry_dict['fday2']['avgtemp'] = miss
			smry_dict['fday3']['avgtemp'] = miss
			smry_dict['fday4']['avgtemp'] = miss
			smry_dict['fday5']['avgtemp'] = miss
			smry_dict['day0']['qpf']  = miss
			smry_dict['pday1']['qpf'] = miss
			smry_dict['pday2']['qpf'] = miss
			smry_dict['fday1']['qpf'] = miss
			smry_dict['fday2']['qpf'] = miss
			smry_dict['fday3']['qpf'] = miss
			smry_dict['fday4']['qpf'] = miss
			smry_dict['fday5']['qpf'] = miss
			smry_dict['day0']['pops']  = {}
			smry_dict['pday1']['pops'] = {}
			smry_dict['pday2']['pops'] = {}
			smry_dict['fday1']['pops'] = {}
			smry_dict['fday2']['pops'] = {}
			smry_dict['fday3']['pops'] = {}
			smry_dict['fday4']['pops'] = {}
			smry_dict['fday5']['pops'] = {}
			smry_dict['day0']['pops']['am']  = miss
			smry_dict['pday1']['pops']['am'] = miss
			smry_dict['pday2']['pops']['am'] = miss
			smry_dict['fday1']['pops']['am'] = miss
			smry_dict['fday2']['pops']['am'] = miss
			smry_dict['fday3']['pops']['am'] = miss
			smry_dict['fday4']['pops']['am'] = miss
			smry_dict['fday5']['pops']['am'] = miss
			smry_dict['day0']['pops']['pm']  = miss
			smry_dict['pday1']['pops']['pm'] = miss
			smry_dict['pday2']['pops']['pm'] = miss
			smry_dict['fday1']['pops']['pm'] = miss
			smry_dict['fday2']['pops']['pm'] = miss
			smry_dict['fday3']['pops']['pm'] = miss
			smry_dict['fday4']['pops']['pm'] = miss
			smry_dict['fday5']['pops']['pm'] = miss

			for i in range(len(daily_data)):
				dly_dt,tave_hr,tmax,tmin,prcp,pop12,rhum,wspd,srad,qpf,st4x,st4n,dflags = daily_data[i]
				theDate_dt = DateTime.DateTime(dly_dt[0],dly_dt[1],dly_dt[2],0,0,0)
				if not getpops:
					pop12 = []
					qpf = prcp
				if day0 == theDate_dt:
					smry_dict['day0']['avgtemp'] = tave_hr
					smry_dict['day0']['qpf'] = qpf
					for hr,pop in pop12:
						if hr < 12:
							which = 'am'
						else:
							which = 'pm'
						smry_dict['day0']['pops'][which] = pop
				elif pday1 == theDate_dt:
					smry_dict['pday1']['avgtemp'] = tave_hr
					smry_dict['pday1']['qpf'] = qpf
					for hr,pop in pop12:
						if hr < 12:
							which = 'am'
						else:
							which = 'pm'
						smry_dict['pday1']['pops'][which] = pop
				elif pday2 == theDate_dt:
					smry_dict['pday2']['avgtemp'] = tave_hr
					smry_dict['pday2']['qpf'] = qpf
					for hr,pop in pop12:
						if hr < 12:
							which = 'am'
						else:
							which = 'pm'
						smry_dict['pday2']['pops'][which] = pop
				elif fday1 == theDate_dt:
					smry_dict['fday1']['avgtemp'] = tave_hr
					smry_dict['fday1']['qpf'] = qpf
					for hr,pop in pop12:
						if hr < 12:
							which = 'am'
						else:
							which = 'pm'
						smry_dict['fday1']['pops'][which] = pop
				elif fday2 == theDate_dt:
					smry_dict['fday2']['avgtemp'] = tave_hr
					smry_dict['fday2']['qpf'] = qpf
					for hr,pop in pop12:
						if hr < 12:
							which = 'am'
						else:
							which = 'pm'
						smry_dict['fday2']['pops'][which] = pop
				elif fday3 == theDate_dt:
					smry_dict['fday3']['avgtemp'] = tave_hr
					smry_dict['fday3']['qpf'] = qpf
					for hr,pop in pop12:
						if hr < 12:
							which = 'am'
						else:
							which = 'pm'
						smry_dict['fday3']['pops'][which] = pop
				elif fday4 == theDate_dt:
					smry_dict['fday4']['avgtemp'] = tave_hr
					smry_dict['fday4']['qpf'] = qpf
					for hr,pop in pop12:
						if hr < 12:
							which = 'am'
						else:
							which = 'pm'
						smry_dict['fday4']['pops'][which] = pop
				elif fday5 == theDate_dt:
					smry_dict['fday5']['avgtemp'] = tave_hr
					smry_dict['fday5']['qpf'] = qpf
					for hr,pop in pop12:
						if hr < 12:
							which = 'am'
						else:
							which = 'pm'
						smry_dict['fday5']['pops'][which] = pop
		except:
			print_exception()
		return smry_dict

##### APPLE SCAB #####
	#--------------------------------------------------------------------------------------------		
	# build Revised Mills Table as python dictionary
	def build_mills_table(self):
		mills_list = [(34,41,0),(36,35,0),(37,30,0),(39,28,0),(41,21,0),(43,18,17),(45,15,17),
			(46,13,17),(48,12,17),(50,11,16),(52,9,15),(54,8,14),(57,7,12),(61,6,9),(77,8,0),(79,11,0)]
		mills_chart = {}
		t,h,d = mills_list[0]
		mills_chart[t] = (h,d)
		for i in range (1,len(mills_list)):
			t,h,d = mills_list[i]
			for temp in range(mills_list[i-1][0]+1,t):
				mills_chart[temp] = (mills_list[i-1][1],mills_list[i-1][2])
			mills_chart[t] = (h,d)
		return mills_chart
	
	#--------------------------------------------------------------------------------------------		
	# determine wet and dry periods from hourly data provided
	def get_wetdry (self,hourly_data,download_time,estimate="no"):
		wd_periods = []
		try:
			wet_hrs = 0
			dry_hrs = 0
			temp_sum = 0.
			temp_cnt = 0.
			prcp_sum = 0.
			prcp_cnt = 0.
			for theTime,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags in hourly_data:
				temp_eflag, prcp_eflag, lwet_eflag, rhum_eflag, wspd_eflag, wdir_eflag, srad_eflag, st4i_eflag = eflags
				########################################################################
				# only thing different when estimate is "yes" - always estimate lwet   #
				########################################################################
				if estimate == "yes":
					if rhum == miss:
						lwet = miss
					elif rhum >= 90 or prcp > 0.00:
						lwet = 60
					else:
						lwet = 0
				else:
					if lwet == miss and rhum != miss:
						if rhum >= 90 or prcp > 0.00:
							lwet = 60
						else:
							lwet = 0
				if lwet == miss: continue
				if lwet > 0 and wet_hrs == 0 and (prcp == 0 or prcp == miss): lwet=0	#wetting period must start with prcp
				if lwet > 0:
					if dry_hrs > 0:
						dry_end = (DateTime.DateTime(*theTime) + DateTime.RelativeDate(hours=-1)).tuple()[:4]
						if temp_cnt > 0:
							temp_ave = temp_sum/temp_cnt
						else:
							temp_ave = miss
						wd_periods.append(('dry',dry_start,dry_end,dry_hrs,temp_ave,0.0))
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
						wd_periods.append(('wet',wet_start,wet_end,wet_hrs,temp_ave,prcp_tot))
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
				wet_end = download_time
				if temp_cnt > 0:
					temp_ave = temp_sum/temp_cnt
				else:
					temp_ave = miss
				if prcp_cnt > 0:
					prcp_tot = prcp_sum
				else:
					prcp_tot = miss
				wd_periods.append(('wet',wet_start,wet_end,wet_hrs,temp_ave,prcp_tot))
			elif dry_hrs > 0:
				dry_end = download_time
				if temp_cnt > 0:
					temp_ave = temp_sum/temp_cnt
				else:
					temp_ave = miss
				wd_periods.append(('dry',dry_start,dry_end,dry_hrs,temp_ave,0.0))	
		except:
			print_exception()
		return wd_periods

	#--------------------------------------------------------------------------------------------		
	# fill in current day, if necessary, using data downloaded so far
	def fill_lastday (self,hourly_data, daily_data):
		try:
			dly_dt,tave_hr,tmax,tmin,prcp,lwet,rhum,wspd,srad,st4a,st4x,st4n,dflags = daily_data[-1]
			temp_flag,prcp_flag,lwet_flag,rhum_flag,wspd_flag,wdir_flag,srad_flag,st4i_flag = dflags
			hly_dt,htemp,hprcp,hlwet,hrhum,hwspd,hwdir,hsrad,hst4i,eflags = hourly_data[-1]
			if hly_dt != dly_dt:
				last_in_daily = DateTime.DateTime(*dly_dt)
				nd = last_in_daily + DateTime.RelativeDate(days=+1)
				temp_sum = 0.
				temp_cnt = 0.
				temp_max = -9999.
				temp_min = 9999.
				prcp_sum = 0.
				prcp_cnt = 0.
				temp_dflag = ' '
				prcp_dflag = ' '
				for theTime,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags in hourly_data:
					temp_eflag, prcp_eflag, lwet_eflag, rhum_eflag, wspd_eflag, wdir_eflag, srad_eflag, st4i_eflag = eflags
					if theTime[0]==nd.year and theTime[1]==nd.month and theTime[2]==nd.day:
						if temp != miss:
							temp_sum = temp_sum + temp
							if temp > temp_max: temp_max = copy.deepcopy(temp)
							if temp < temp_min: temp_min = copy.deepcopy(temp)
							temp_cnt = temp_cnt + 1
							if temp_eflag in ['S','I']: temp_dflag = 'E'
						if prcp != miss:
							prcp_sum = prcp_sum + prcp
							prcp_cnt = prcp_cnt + 1
							if prcp_eflag in ['S','I']: prcp_dflag = 'E'
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
				if temp_cnt > 0 or prcp_cnt > 0:
					dflags = (temp_dflag, prcp_dflag, ' ', ' ', ' ', ' ', ' ', ' ')
					last_day_data = ([nd.year,nd.month,nd.day],dly_temp_ave,dly_temp_max,dly_temp_min,dly_prcp_tot,miss,miss,miss,miss,miss,miss,miss,dflags)
					daily_data.append(last_day_data)			
		except:
			print_exception()
		return daily_data
		
	#--------------------------------------------------------------------------------------------		
	# check Mills Table for infection events and, if present, number of days to lesion appearance
	def check_table (self,avg_temp,wet_hrs,mills_chart):
		infect = miss
		ldys = None
		try:
			temp = int(round(avg_temp,0))
			if temp < 34 or temp > 79:
				infect = 0
				ldys = None
			else:
				req_hrs,ldys = mills_chart[temp]
				if wet_hrs >= req_hrs:
					infect = 1
				else:
					infect = 0
					ldys = None
		except:
			print_exception()
		return infect,ldys

	#--------------------------------------------------------------------------------------------		
	# combine wet events and check for infection. also report current status
	def get_infection (self,periods,mills_chart):
		infection_events = []
		try:
			temp_sum = 0.
			prec_sum = 0.
			wet_hrs = 0.
			wet_event = 0
			combined = 0
			for wd,start,end,length,temp,prec in periods:
				if wd == 'wet':
					if not wet_event:
						wet_start = start
						wet_event = 1
						combined = 0
					else:
						combined = 1
					wet_end = end
					wet_hrs = wet_hrs + length
					temp_sum = temp_sum + (temp*length)
					prec_sum = prec_sum + prec
				elif wd == 'dry' and length >= 24 and wet_event:
					avg_temp = temp_sum/wet_hrs
					# use Mills chart to determine if this is an infection event
					infect,ldys = self.check_table(avg_temp,wet_hrs,mills_chart)
					if infect:
						infection_events.append((wet_start,wet_end,wet_hrs,avg_temp,prec_sum,ldys,combined))
#					else:
#						print 'no infection:',avg_temp,wet_hrs
					wet_event = 0
					combined = 0
					temp_sum = 0.
					prec_sum = 0.
					wet_hrs = 0.				
				elif wd not in ['wet','dry']:
					print '***** Unexpected error: period is not wet or dry *****'
					infection_events = []
					break
			# check for event still in progress
			if wet_event:
				avg_temp = temp_sum/wet_hrs
				infect,ldys = self.check_table(avg_temp,wet_hrs,mills_chart)
				if infect:
					infection_events.append((wet_start,wet_end,wet_hrs,avg_temp,prec_sum,ldys,combined))
#				else:
#					print 'no infection:',avg_temp,wet_hrs
			if wd == 'wet': 
				stat = ('Wet',wet_hrs)
			elif wd == 'dry':
				stat = ('Dry',length)
		except:
			print_exception()
		return infection_events, stat

	#--------------------------------------------------------------------------------------------		
#	get infection information for today, yesterday and day before
	def check_infection (self,infection_events,end_date_dt,last_data_dt,smry_dict):
		try:
			# today (day0), yesterday (pday1), day before (pday2)
			day0 = end_date_dt
			day0 = day0 + DateTime.RelativeDate(hour=0,minute=0,second=0)
			pday1 = day0 + DateTime.RelativeDate(days=-1)
			pday2 = day0 + DateTime.RelativeDate(days=-2)
			fday1 = day0 + DateTime.RelativeDate(days=+1)
			fday2 = day0 + DateTime.RelativeDate(days=+2)
			fday3 = day0 + DateTime.RelativeDate(days=+3)
			fday4 = day0 + DateTime.RelativeDate(days=+4)
			fday5 = day0 + DateTime.RelativeDate(days=+5)

			# build list of dates with infection (listed by end date)
			event_list = []
			for istart,iend,ihrs,itemp,iprec,ldys,icomb in infection_events:
				istart_dt = DateTime.DateTime(*istart)
				iend_dt = DateTime.DateTime(*iend)
				event_list.append((istart_dt,iend_dt,ldys))
				
#				print istart,iend,ihrs,itemp,iprec,ldys,icomb
				
			smry_dict['day0']['infection']  = ('-','-')
			smry_dict['pday1']['infection']  = ('-','-')
			smry_dict['pday2']['infection']  = ('-','-')
			smry_dict['fday1']['infection']  = ('-','-')
			smry_dict['fday2']['infection']  = ('-','-')
			smry_dict['fday3']['infection']  = ('-','-')
			smry_dict['fday4']['infection']  = ('-','-')
			smry_dict['fday5']['infection']  = ('-','-')
						
			if day0 <= last_data_dt:
				smry_dict['day0']['infection']  = ('No','-')
			if pday1 <= last_data_dt:
				smry_dict['pday1']['infection']  = ('No','-')
			if pday2 <= last_data_dt:
				smry_dict['pday2']['infection']  = ('No','-')
			if fday1 <= last_data_dt:
				smry_dict['fday1']['infection']  = ('No','-')
			if fday2 <= last_data_dt:
				smry_dict['fday2']['infection']  = ('No','-')
			if fday3 <= last_data_dt:
				smry_dict['fday3']['infection']  = ('No','-')
			if fday4 <= last_data_dt:
				smry_dict['fday4']['infection']  = ('No','-')
			if fday5 <= last_data_dt:
				smry_dict['fday5']['infection']  = ('No','-')
			
			# check for infections 
			for istart_dt,iend_dt,ldys in event_list:
				start_ymd = istart_dt + DateTime.RelativeDate(hour=0,minute=0,second=0)
				end_ymd = iend_dt + DateTime.RelativeDate(hour=0,minute=0,second=0)
				if ldys == 9:
					ldystr = "9-10"
				elif ldys == 12:
					ldystr = "12-13"
				elif ldys == 0:
					ldystr = "-"
				else:
					ldystr = "%d"%ldys
					
				for td,std in [(day0,'day0'),(pday1,'pday1'),(pday2,'pday2'),(fday1,'fday1'),(fday2,'fday2'),(fday3,'fday3'),(fday4,'fday4'),(fday5,'fday5')]:
					if td == end_ymd:
						smry_dict[std]['infection'] = ('Yes',ldystr)
						continue
					elif td >= start_ymd and td < end_ymd:
						smry_dict[std]['infection'] = ('Combined','-')
						continue
		except:
			print_exception()
		return smry_dict

	#--------------------------------------------------------------------------------------------
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
	#	check ascospore maturity (percent)
	def ascospore_calcs (self,dd_data,daily_data):
		ascospore_dict = {}
		date95 = None
		try:
			daily_prec = []
			# need precip for six days preceding greentip (first day in dd_data)
			first_dt = DateTime.DateTime(dd_data[0][0][0],dd_data[0][0][1],dd_data[0][0][2])
			minus6_dt = first_dt + DateTime.RelativeDate(days=-6)
			minus6_list = [minus6_dt.year,minus6_dt.month,minus6_dt.day]
			for i in range(len(daily_data)):
				dly_dt,tave_hr,tmax,tmin,prcp,lwet,rhum,wspd,srad,st4a,st4x,st4n,dflags = daily_data[i]
				if dly_dt == minus6_list:
					daily_prec.append(daily_data[i][4])
					daily_prec.append(daily_data[i+1][4])
					daily_prec.append(daily_data[i+2][4])
					daily_prec.append(daily_data[i+3][4])
					daily_prec.append(daily_data[i+4][4])
					daily_prec.append(daily_data[i+5][4])
			accum_dd = 0.
			for dly_dt,tmax,tmin,ddval,prec in dd_data:
				if prec != miss:
					daily_prec.append(prec)
				else:
					daily_prec.append(0.)
				if len(daily_prec) > 7:
					del daily_prec[0]
					prec7dy = sum(daily_prec)
				else:
					prec7dy = miss
				if prec7dy > 0.00 or prec7dy == miss:
					if ddval != miss: accum_dd = accum_dd + ddval
				else:
					pass	#don't accumulate anything during dry period
				if ddval != miss:
					comp = math.exp((math.pi/math.sqrt(3))*((2.51+(0.01*accum_dd))-5.))
					maturity = 100.*(comp)/(1.+comp)
					ascospore_dict[tuple(dly_dt)] = (maturity,miss,miss)
				else:
					maturity = miss
					ascospore_dict[tuple(dly_dt)] = (miss,miss,miss)
				if round(maturity,0) >= 95 and not date95:
					date95 = dly_dt
					prec95 = 0.
		except:
			print_exception()
		return ascospore_dict, date95
		
	#--------------------------------------------------------------------------------------------		
	# acsospore depletion model
	def depleteascospores(self, ascospore_dict, hourly_data):
		all_released = None
		day_temp_sum = 0.
		day_temp_cnt = 0
		day_prcp_sum = 0.
		night_prcp_sum = 0.
		accum_deplete = 0.
		for theTime,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags in hourly_data:
			temp_eflag, prcp_eflag, lwet_eflag, rhum_eflag, wspd_eflag, wdir_eflag, srad_eflag, st4i_eflag = eflags
			#theTime = (y,m,d,h)
			theHour = theTime[3]
			if theHour >= 7 and theHour <= 19:
				if prcp != miss and round(prcp,2) >= 0.01:
					day_prcp_sum = day_prcp_sum + prcp
					if temp != miss:
						day_temp_sum = day_temp_sum + temp
						day_temp_cnt = day_temp_cnt + 1
			elif prcp != miss and round(prcp,2) >= 0.01:
				night_prcp_sum = night_prcp_sum + prcp
			if theHour == 19:
				ymd = theTime[:3]
				if ascospore_dict.has_key(ymd) and ascospore_dict[ymd][0] != miss:
					dly_asp = ascospore_dict[ymd][0]
					### do ascospore depletion for the day and seasonal accumulation
					day_temp_avg = miss  #FOR DEGUBBING ONLY
					if night_prcp_sum > 0:
						#night rain depletion
						deplete_pct_night = 0.05
						dly_deplete_night = (dly_asp - accum_deplete) * deplete_pct_night
						accum_deplete += dly_deplete_night
					else:
						deplete_pct_night = 0
						dly_deplete_night = 0.0
					if day_prcp_sum > 0:
						#day rain depletion
						if day_temp_cnt > 0:
							day_temp_avg = day_temp_sum/day_temp_cnt
						else:
							day_temp_avg = miss
						#daytime rain events
						if day_temp_avg != miss and day_temp_avg >= 50 and round(day_prcp_sum,2) >= 0.10:
							deplete_pct_day = 0.90
						elif day_temp_avg != miss and day_temp_avg >= 50 and round(day_prcp_sum,2) < 0.10:
							deplete_pct_day = 0.50
						elif day_temp_avg != miss and day_temp_avg < 50 and round(day_prcp_sum,2) >= 0.10:
							deplete_pct_day = 0.50
						elif day_temp_avg != miss and day_temp_avg < 50 and round(day_prcp_sum,2) < 0.10:
							deplete_pct_day = 0.25
						else:
							deplete_pct_day = 0.0
						dly_deplete_day = (dly_asp - accum_deplete) * deplete_pct_day
						accum_deplete += dly_deplete_day
					else:
						deplete_pct_day = 0
						dly_deplete_day = 0.0
					ascospore_dict[ymd] = (dly_asp, (dly_deplete_night+dly_deplete_day), accum_deplete)
##					print ymd,dly_asp,night_prcp_sum,deplete_pct_night,dly_deplete_night,day_prcp_sum,day_temp_avg,deplete_pct_day,dly_deplete_day,accum_deplete
					# check for all released
					if not all_released and round(dly_asp,0) >= 95 and round(day_prcp_sum,2) >= 0.10 and day_temp_avg >= 50:
						all_released = ymd
				day_temp_sum = 0.
				day_temp_cnt = 0
				day_prcp_sum = 0.
				night_prcp_sum = 0.
		return ascospore_dict, all_released

	#--------------------------------------------------------------------------------------------		
	# add acsospore maturity to dictionary for today, yesterday and day before
	def addascospore (self, ascospore_dict, smry_dict):
		try:
			for k in ['day0','pday1','pday2','fday1','fday2','fday3','fday4','fday5']:
				ymd = smry_dict[k]['ymd']
				if ascospore_dict.has_key(ymd):
					if ascospore_dict[ymd][0] != miss:
						smry_dict[k]['ascomatur']  = ascospore_dict[ymd][0]
						smry_dict[k]['ascodlydpt'] = ascospore_dict[ymd][1]
						smry_dict[k]['ascoaccdpt'] = ascospore_dict[ymd][2]
					else:
						smry_dict[k]['ascomatur']  = miss
						smry_dict[k]['ascodlydpt'] = miss
						smry_dict[k]['ascoaccdpt'] = miss
				else:
					smry_dict[k]['ascomatur']  = miss
					smry_dict[k]['ascodlydpt'] = miss
					smry_dict[k]['ascoaccdpt'] = miss
		except:
			print_exception()
		return smry_dict


##### FIRE BLIGHT #####	
	#--------------------------------------------------------------------------------------------		
	def get_dhr (self, temp):
		dhr = None
		dhr_dict = {60: 0.0, 61: 0.45, 62: 1.09, 63: 1.9, 64: 2.7, 65: 3.6, 66: 4.5, 67: 5.5, 68: 6.6, 69: 8.0, 
			70: 9.3, 71: 11.1, 72: 12.7, 73: 14.4, 74: 16.4, 75: 18.5, 76: 20.5, 77: 22.2, 78: 23.8, 79: 25.1, 
			80: 26.0, 81: 26.5, 82: 27.0, 83: 27.45, 84: 27.7, 85: 27.9, 86: 28.0, 87: 28.0, 88: 28.0, 89: 27.5, 
			90: 27.0, 91: 26.2, 92: 25.1, 93: 23.5, 94: 21.5, 95: 19.3, 96: 16.6, 97: 13.3, 98: 10.2, 99: 7.5, 
			100: 5.3, 101: 3.6, 102: 2.0, 103: 1.2, 104: 0.7, 105: 0.0}
		try:
			temp = int(round(temp,0))
			if temp <= 60 or temp >= 105:
				dhr = 0.
			else:
				dhr = dhr_dict[temp]
		except:
			print_exception()
		return dhr

	#--------------------------------------------------------------------------------------------		
	# calculate accumulated degree hours from hourly temperature values
	def deghr_calcs (self,hourly_data,start_date,end_date):
		deghr_data = []
		try:
			dly_sum = 0.
			dly_msg = 0.
			start_date = start_date + DateTime.RelativeDate(days=+1)		#start deghr accumulation day after biofix
			start_date = start_date + DateTime.RelativeDate(hour=0,minute=0,second=0)
			end_date = end_date + DateTime.RelativeDate(hour=23,minute=59,second=59)
			for theTime,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags in hourly_data:
				temp_eflag, prcp_eflag, lwet_eflag, rhum_eflag, wspd_eflag, wdir_eflag, srad_eflag, st4i_eflag = eflags
				this_date = DateTime.DateTime(*theTime)
				if this_date >= start_date and this_date <= end_date:
					if temp != miss:
						ddval = self.get_dhr(temp)
						dly_sum = dly_sum + ddval
					else:
						dly_msg = dly_msg+1
		#			save daily values
					if theTime[3] == 23:
						if dly_msg >= 2: dly_sum = miss
						deghr_data.append((theTime[:3],dly_sum))
						dly_sum = 0.
						dly_msg = 0
		#	get last partial day
			if theTime[3] != 23:
				deghr_data.append((theTime[:3],dly_sum))
		except:
			print 'Error calculating degree hours'
			print_exception()
		return deghr_data

	#--------------------------------------------------------------------------------------------		
	# calculate EIP for fire blight
	def eip_calcs (self,hourly_data,wetness_dict,start_date,end_date,strep_spray):
		risk_level = {0: 'Low', 1: 'Moderate', 2: 'High', 3: 'Infection'}
		dly_data = {}
		eip_results = {}
		wetness_data = {}
		try:
			if strep_spray:
				strep_tuple = (strep_spray.year,strep_spray.month,strep_spray.day)
				strep_nxtdy_dt = strep_spray + DateTime.RelativeDate(days=+1)
			else:
				strep_tuple = None
		#	convert wetness_dict to object keyed on date
			for item in wetness_dict:
				#(theTime[:3],dly_rain,dly_lwet,dly_dew,max_rhum,min_rhum,cnt_rhum,avg_temp)
				wetness_data[item[0]] = {
					'dly_pcpn': item[1],
					'dly_lwet': item[2],
					'dly_dew': item[3]
				}
		#	process hourly data
			dly_dh65 = 0
			dly_msg = 0.
			dly_max = -9999
			dly_min = 9999
			start_date = start_date + DateTime.RelativeDate(hour=0,minute=0,second=0)
			end_date = end_date + DateTime.RelativeDate(hour=23,minute=59,second=59)
		#	get daily maxt, mint, gdd (base 40), and gdh (base 65)
			for theTime,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags in hourly_data:
				this_date = DateTime.DateTime(*theTime)
				temp = round(temp, 0)
				if this_date >= start_date and this_date <= end_date:
					if temp != miss:
						if temp > dly_max:
							dly_max = copy.deepcopy(temp)
						if temp < dly_min:
							dly_min = copy.deepcopy(temp)
						if temp > 65:
							dly_dh65 += (temp - 65)
					else:
						dly_msg = dly_msg + 1
		#			save daily values
					if theTime[3] == 23:
						if dly_msg >= 5:
							dly_dd40 = miss
							dly_dh65 = miss
							dly_max = miss
							dly_avg = miss
						else:
							dly_avgt = round(((dly_max + dly_min) / 2.0), 0)
							if dly_avgt  > 40:
								dly_dd40 = dly_avgt - 40
							else:
								dly_dd40 = 0
						dly_data[theTime[:3]] = {'dly_max':dly_max, 'dly_min':dly_min, 'dly_avgt':dly_avgt, 'dly_dd40':dly_dd40, 'dly_dh65':dly_dh65}
						dly_dh65 = 0
						dly_msg = 0.
						dly_max = -9999
						dly_min = 9999
		#	get last partial day
			if theTime[3] != 23:
				dly_avgt = round(((dly_max + dly_min) / 2.0), 0)
				dly_data[theTime[:3]] = {'dly_max':dly_max, 'dly_min':dly_min, 'dly_avgt':dly_avgt, 'dly_dd40':dly_dd40, 'dly_dh65':dly_dh65}
				
		#	now calculate eip for each day
			dys = dly_data.keys()
			dys.sort()
			dh_start_date = start_date	#start of eip calculation window
			accum_dd40 = 0
			for this_date in dys:
##				print this_date,'Daily data:',dly_data[this_date]
		#		when accumulated gdd exceed 80, shift window one day until it is less than 80; accumulation thru yesterday
##				print 'dd>40 accum',accum_dd40
				while accum_dd40 >= 80:
					dh_start_tuple = (dh_start_date.year,dh_start_date.month,dh_start_date.day)
					accum_dd40 -= dly_data[dh_start_tuple]["dly_dd40"]
					dh_start_date = dh_start_date + DateTime.RelativeDate(days=+1)
##					print 'dd>40 reduced to',accum_dd40,'and window moved to',(dh_start_date.year,dh_start_date.month,dh_start_date.day)
					
		#		accumulate dh over epi calculation period
				accum_dh65 = 0
				this_date_dt = DateTime.DateTime(*this_date)
				this_date_dt = this_date_dt + DateTime.RelativeDate(hour=0,minute=0,second=1)
				td = dh_start_date + DateTime.RelativeDate(hour=0,minute=0,second=0)
				while td <= this_date_dt:
					td_tuple = (td.year,td.month,td.day)
					yest_dt = td + DateTime.RelativeDate(days=-1)
					yest_tuple = (yest_dt.year,yest_dt.month,yest_dt.day)
					yest2_dt = td + DateTime.RelativeDate(days=-2)
					yest2_tuple = (yest2_dt.year,yest2_dt.month,yest2_dt.day)

		#			max <65 for three consecutive days; reset window to current day					
					if dly_data[td_tuple]["dly_max"] <= 65 and \
					   dly_data.has_key(yest2_tuple) and dly_data[yest2_tuple]["dly_max"] <= 65 and \
					   dly_data.has_key(yest_tuple) and dly_data[yest_tuple]["dly_max"] <= 65:
						dh_start_date = this_date_dt
						td = this_date_dt
						td_tuple = (td.year,td.month,td.day)
						yest_dt = td + DateTime.RelativeDate(days=-1)
						yest_tuple = (yest_dt.year,yest_dt.month,yest_dt.day)
						yest2_dt = td + DateTime.RelativeDate(days=-2)
						yest2_tuple = (yest2_dt.year,yest2_dt.month,yest2_dt.day)
						accum_dd40 = 0
						accum_dh65 = 0
##						print 'dh>65 for three days; moved window to',(dh_start_date.year,dh_start_date.month,dh_start_date.day)
							
					accum_dh65 += dly_data[td_tuple]["dly_dh65"]
##					print 'Adding',dly_data[td_tuple]["dly_dh65"],'for',td_tuple,'accum is',accum_dh65
		#			apply reduction rules; don't reduce once value tops 400 (unless min temp below 24)
					if dly_data[td_tuple]["dly_min"] < 24:
##						print accum_dh65,'reduced to zero (min < 24)'
						accum_dh65 = 0
					elif dly_data[td_tuple]["dly_min"] < 33 and accum_dh65 < 400:
##						print accum_dh65,'reduced to zero (min < 33)'
						accum_dh65 = 0
					elif dly_data[td_tuple]["dly_max"] <= 65 and accum_dh65 < 400:
						if dly_data.has_key(yest2_tuple) and dly_data[yest2_tuple]["dly_max"] <= 65 and \
						   dly_data.has_key(yest_tuple) and dly_data[yest_tuple]["dly_max"] <= 65:
##							print accum_dh65,'reduced to zero (3 max < 65)'
							accum_dh65 = 0
						elif dly_data.has_key(yest_tuple) and dly_data[yest_tuple]["dly_max"] <= 65:
##							print accum_dh65,'reduced by 1/2'
							accum_dh65 *= 0.50
						else:
##							print accum_dh65,'reduced by 1/3'
							accum_dh65 *= 0.667
					td = td + DateTime.RelativeDate(days=+1)
		#		strep spray resets everything
				if this_date == strep_tuple:
					dh_start_date = strep_nxtdy_dt
					accum_dd40 = 0
					accum_dh65 = 0
##					print 'strep applied; moved window to',(dh_start_date.year,dh_start_date.month,dh_start_date.day)
				else:
					accum_dd40 += dly_data[this_date]["dly_dd40"]				
		#		calculate risk
				risk_pts = 0
				twd = wetness_data[this_date]
				yest_dt = this_date_dt + DateTime.RelativeDate(days=-1)
				yest_tuple = (yest_dt.year,yest_dt.month,yest_dt.day)
				eip = int(round((accum_dh65/198.0) * 100, 0))
				if eip > 100: risk_pts += 1
				if dly_data[this_date]["dly_avgt"] > 60: risk_pts += 1
				if twd['dly_pcpn'] > 0 or twd['dly_lwet'] > 0 or twd['dly_dew'] > 0 or (wetness_data.has_key(yest_tuple) and wetness_data[yest_tuple]['dly_pcpn'] > 0.10):
					risk_pts += 1
		#		update results for the day	
				eip_results[this_date] = {	
					'eip_start': (dh_start_date.year,dh_start_date.month,dh_start_date.day),
					'accum_dh65': round(accum_dh65, 0),
					'eip': eip,
					'eip_risk': risk_level[risk_pts]
				}
##				print this_date,'Results:',eip_results[this_date]
		except:
			print 'Error calculating eip'
			print_exception()
		return eip_results

	#--------------------------------------------------------------------------------------------		
	# accumulate 4-day degree hour totals and blight risk
	def fbrisk (self,d4_dh,dly_dh,orchard_history):
		bl_threshold = {'Low':      [300,150,100],
						'Caution':  [500,300,200],
						'High':     [800,500,300] }
		sum_dh = miss
		d4_risk = "NA"
		try:
			if len(d4_dh) == 4: del d4_dh[0]
			d4_dh.append(dly_dh)
			if len(d4_dh) >= 1 and len(d4_dh) <= 4 and d4_dh.count(miss) == 0: 
				sum_dh = sum(d4_dh)
				if sum_dh < bl_threshold['Low'][orchard_history-1]:
					d4_risk = "Low"
				elif sum_dh >= bl_threshold['Low'][orchard_history-1] and sum_dh < bl_threshold['Caution'][orchard_history-1]:
					d4_risk = "Caution"
				elif sum_dh >= bl_threshold['Caution'][orchard_history-1] and sum_dh < bl_threshold['High'][orchard_history-1]:
					d4_risk = "High"
				elif sum_dh >= bl_threshold['High'][orchard_history-1]:
					d4_risk = "Extreme"
				else:
					d4_risk = "NA"
				if len(d4_dh) <= 3:
					d4_risk = "%d-day/"%len(d4_dh) + d4_risk
			else:
				sum_dh = miss
				d4_risk = "-"
		except:
			print_exception()
		return sum_dh,d4_risk,d4_dh

	#--------------------------------------------------------------------------------------------		
	# check blight risk for today, yesterday and day before, and 5-day forecast
	def add_risks (self,smry_dict,deghrs,eip_dict,end_date_dt,orchard_history,start_date_dt,strep_spray):
		smry_dict['day0'] = {}
		smry_dict['pday1'] = {}
		smry_dict['pday2'] = {}
		smry_dict['fday1'] = {}
		smry_dict['fday2'] = {}
		smry_dict['fday3'] = {}
		smry_dict['fday4'] = {}
		smry_dict['fday5'] = {}
		d4_dh = []
		try:
			# today (day0), yesterday (pday1), day before (pday2)
			day0 = end_date_dt + DateTime.RelativeDate(hour=0,minute=0,second=0)
			smry_dict['day0']['ymd']  = (day0.year,day0.month,day0.day)
			pday1 = day0 + DateTime.RelativeDate(days=-1)
			pday2 = day0 + DateTime.RelativeDate(days=-2)
			fday1 = day0 + DateTime.RelativeDate(days=+1)
			fday2 = day0 + DateTime.RelativeDate(days=+2)
			fday3 = day0 + DateTime.RelativeDate(days=+3)
			fday4 = day0 + DateTime.RelativeDate(days=+4)
			fday5 = day0 + DateTime.RelativeDate(days=+5)
			smry_dict['day0']['risk']  = ('-',miss)
			smry_dict['pday1']['risk'] = ('-',miss)
			smry_dict['pday2']['risk'] = ('-',miss)
			smry_dict['fday1']['risk'] = ('-',miss)
			smry_dict['fday2']['risk'] = ('-',miss)
			smry_dict['fday3']['risk'] = ('-',miss)
			smry_dict['fday4']['risk'] = ('-',miss)
			smry_dict['fday5']['risk'] = ('-',miss)
			smry_dict['day0']['eip']  = ('-',miss)
			smry_dict['pday1']['eip'] = ('-',miss)
			smry_dict['pday2']['eip'] = ('-',miss)
			smry_dict['fday1']['eip'] = ('-',miss)
			smry_dict['fday2']['eip'] = ('-',miss)
			smry_dict['fday3']['eip'] = ('-',miss)
			smry_dict['fday4']['eip'] = ('-',miss)
			smry_dict['fday5']['eip'] = ('-',miss)
			
			if strep_spray:
				strep_spray_dt = strep_spray + DateTime.RelativeDate(hour=0,minute=0,second=0)  #for comparisons
			else:
				strep_spray_dt = end_date_dt + DateTime.RelativeDate(days=-15)	#out of the way of useful calculations

			# check for risk last three days, forecast next 5 days
			for theDate,dly_dhr in deghrs:
				theDate_dt = DateTime.DateTime(*theDate) + DateTime.RelativeDate(hour=0,minute=0,second=0)
				if theDate_dt == strep_spray_dt:
					d4_dh = []	#restart count
					d4_sum = miss
					d4_risk = '-'
				elif theDate_dt < start_date_dt:
					d4_sum,d4_risk,d4_dh = self.fbrisk(d4_dh,miss,orchard_history)
				else:
					d4_sum,d4_risk,d4_dh = self.fbrisk(d4_dh,dly_dhr,orchard_history)
					
				if day0 == theDate_dt:
					smry_dict['day0']['risk'] =  (d4_risk, d4_sum)
					if eip_dict.has_key(theDate):
						smry_dict['day0']['eip'] = (eip_dict[theDate]['eip_risk'],eip_dict[theDate]['eip'])
				elif pday1 == theDate_dt:
					smry_dict['pday1']['risk'] = (d4_risk, d4_sum)
					if eip_dict.has_key(theDate):
						smry_dict['pday1']['eip'] = (eip_dict[theDate]['eip_risk'],eip_dict[theDate]['eip'])
				elif pday2 == theDate_dt:
					smry_dict['pday2']['risk'] = (d4_risk, d4_sum)
					if eip_dict.has_key(theDate):
						smry_dict['pday2']['eip'] = (eip_dict[theDate]['eip_risk'],eip_dict[theDate]['eip'])
				elif fday1 == theDate_dt:
					smry_dict['fday1']['risk'] = (d4_risk, d4_sum)
					if eip_dict.has_key(theDate):
						smry_dict['fday1']['eip'] = (eip_dict[theDate]['eip_risk'],eip_dict[theDate]['eip'])
				elif fday2 == theDate_dt:
					smry_dict['fday2']['risk'] = (d4_risk, d4_sum)
					if eip_dict.has_key(theDate):
						smry_dict['fday2']['eip'] = (eip_dict[theDate]['eip_risk'],eip_dict[theDate]['eip'])
				elif fday3 == theDate_dt:
					smry_dict['fday3']['risk'] = (d4_risk, d4_sum)
					if eip_dict.has_key(theDate):
						smry_dict['fday3']['eip'] = (eip_dict[theDate]['eip_risk'],eip_dict[theDate]['eip'])
				elif fday4 == theDate_dt:
					smry_dict['fday4']['risk'] = (d4_risk, d4_sum)
					if eip_dict.has_key(theDate):
						smry_dict['fday4']['eip'] = (eip_dict[theDate]['eip_risk'],eip_dict[theDate]['eip'])
				elif fday5 == theDate_dt:
					smry_dict['fday5']['risk'] = (d4_risk, d4_sum)
					if eip_dict.has_key(theDate):
						smry_dict['fday5']['eip'] = (eip_dict[theDate]['eip_risk'],eip_dict[theDate]['eip'])
		except:
			print_exception()
		return smry_dict

	#--------------------------------------------------------------------------------------------		
	#	accumulate degree days and determine shoot blight recommendation
	def shoot_infection(self, degday_data):
		ddaccum = None
		last_day = None
		recommend = None
		try:
			ddaccum = 0.
			for i in range(len(degday_data)):
				dly_dt,tmax,tmin,ddval,prcp = degday_data[i]
				if ddval != miss:
					ddaccum = ddaccum + ddval
					last_day = dly_dt
					if ddaccum >= 90: break
			if ddaccum >= 90:
				recommend = "Check for trauma blight symptoms starting on %s %d" % (month_names[last_day[1]],last_day[2])
			else:
				recommend = "No symptoms yet"
		except:
			print_exception()
		return ddaccum, last_day, recommend

	#--------------------------------------------------------------------------------------------		
	#	find approx date of shoot blight infection
	def shoot_symptoms (self, degday_data):
		ddaccum = None
		est_day = None
		last_day = None
		try:
			ddaccum = 0.
			for i in range(len(degday_data)-1,-1,-1):
				dly_dt,tmax,tmin,ddval,prcp = degday_data[i]
				if ddval != miss: 
					ddaccum = ddaccum + ddval
					if not last_day: last_day = dly_dt
				if ddaccum >= 90:
					est_day = dly_dt
					break
			else:
				ddaccum = None
				est_day = None
		except:
			print_exception()
		return ddaccum, est_day, last_day

##### SOOTY BLOTCH #####	
	#--------------------------------------------------------------------------------------------		
	# determine sootyblotch risk for the day
	def get_sootyblotch_risk(self,days_since_petalfall,days_since_fungicide,alwh,rain_since_fungicide):
		risk = 'NA'
		if days_since_fungicide > 0:
			ndays = days_since_fungicide
		else:
			ndays = days_since_petalfall
		if alwh == miss:
			risk = 'NA'
		elif alwh < 100:
			if ndays < 10:
				risk = "No Risk"
			else:
				risk = "Low"
		elif alwh >= 100 and alwh < 130:
			if ndays < 21:
				risk = "Low"
			else:
				risk = "Moderate"
		elif alwh >= 130 and alwh <= 170:
			if ndays < 14 and rain_since_fungicide <= 1.5:
				risk = "Low"
			else:
				risk = "Moderate"
		else:
			if ndays < 14:
				if rain_since_fungicide <= 1.5:
					risk = "Low"
				elif rain_since_fungicide <= 2.0:
					risk = "Moderate"
				else:
					risk = "High"
			elif ndays >= 14 and ndays < 21:
				if rain_since_fungicide <= 2.0:
					risk = "Moderate"
				else:
					risk = "High"
			else:
				risk = "High"
		return risk

	#--------------------------------------------------------------------------------------------		
	# check sooty blotch risk for today, yesterday and day before, and 5-day forecast
	def process_sooty_blotch (self,smry_dict,wetness_dict,petalfall,fungicide,end_date_dt,start_date_dt):
		for key in ['day0','pday1','pday2','fday1','fday2','fday3','fday4','fday5']:
			smry_dict[key] = {'risk':miss, 'alwh':'-', 'pfdys':miss, 'fadys':miss, 'rain':'-', 'farain':miss}
		try:
			# today (day0), yesterday (pday1), day before (pday2)
			day0 = end_date_dt + DateTime.RelativeDate(hour=0,minute=0,second=0)
			smry_dict['day0']['ymd']  = (day0.year,day0.month,day0.day)
			pday1 = day0 + DateTime.RelativeDate(days=-1)
			pday2 = day0 + DateTime.RelativeDate(days=-2)
			fday1 = day0 + DateTime.RelativeDate(days=+1)
			fday2 = day0 + DateTime.RelativeDate(days=+2)
			fday3 = day0 + DateTime.RelativeDate(days=+3)
			fday4 = day0 + DateTime.RelativeDate(days=+4)
			fday5 = day0 + DateTime.RelativeDate(days=+5)

			petalfall = petalfall + DateTime.RelativeDate(hour=0)		#needed for "days since" calculations below
			if fungicide: fungicide = fungicide + DateTime.RelativeDate(hour=0)		#ditto
			alwh = 0
			rain_since_fungicide = miss
			# for desired days, get items of interest and calculate risk
			for theDate,dly_rain,dly_lw,dly_dew in wetness_dict:
				theDate_dt = DateTime.DateTime(*theDate) + DateTime.RelativeDate(hour=0,minute=0,second=0)
				if dly_lw != miss and alwh != miss:
					alwh = alwh + dly_lw
				else:
					alwh = miss
				if petalfall:
					days_since_petalfall = (theDate_dt - petalfall).days
				else:
					days_since_petalfall = miss
				if fungicide and theDate_dt > fungicide:
					days_since_fungicide = (theDate_dt - fungicide).days
					if days_since_fungicide == 1: rain_since_fungicide = 0.0
					if rain_since_fungicide != miss and dly_rain != miss:
						rain_since_fungicide = rain_since_fungicide + dly_rain
					else:
						rain_since_fungicide = miss
				else:
					days_since_fungicide = miss
					rain_since_fungicide = '-'
				risk = self.get_sootyblotch_risk(days_since_petalfall,days_since_fungicide,alwh,rain_since_fungicide)
				
				if day0 == theDate_dt:
					smry_dict['day0']['risk'] = risk
					smry_dict['day0']['alwh'] =  alwh
					smry_dict['day0']['pfdys'] =  days_since_petalfall
					smry_dict['day0']['fadys'] =  days_since_fungicide
					smry_dict['day0']['rain'] = dly_rain
					smry_dict['day0']['farain'] = rain_since_fungicide
				elif pday1 == theDate_dt:
					smry_dict['pday1']['risk'] = risk
					smry_dict['pday1']['alwh'] =  alwh
					smry_dict['pday1']['pfdys'] =  days_since_petalfall
					smry_dict['pday1']['fadys'] =  days_since_fungicide
					smry_dict['pday1']['rain'] = dly_rain
					smry_dict['pday1']['farain'] = rain_since_fungicide
				elif pday2 == theDate_dt:
					smry_dict['pday2']['risk'] = risk
					smry_dict['pday2']['alwh'] =  alwh
					smry_dict['pday2']['pfdys'] =  days_since_petalfall
					smry_dict['pday2']['fadys'] =  days_since_fungicide
					smry_dict['pday2']['rain'] = dly_rain
					smry_dict['pday2']['farain'] = rain_since_fungicide
				elif fday1 == theDate_dt:
					smry_dict['fday1']['risk'] = risk
					smry_dict['fday1']['alwh'] =  alwh
					smry_dict['fday1']['pfdys'] =  days_since_petalfall
					smry_dict['fday1']['fadys'] =  days_since_fungicide
					smry_dict['fday1']['rain'] = dly_rain
					smry_dict['fday1']['farain'] = rain_since_fungicide
				elif fday2 == theDate_dt:
					smry_dict['fday2']['risk'] = risk
					smry_dict['fday2']['alwh'] =  alwh
					smry_dict['fday2']['pfdys'] =  days_since_petalfall
					smry_dict['fday2']['fadys'] =  days_since_fungicide
					smry_dict['fday2']['rain'] = dly_rain
					smry_dict['fday2']['farain'] = rain_since_fungicide
				elif fday3 == theDate_dt:
					smry_dict['fday3']['risk'] = risk
					smry_dict['fday3']['alwh'] =  alwh
					smry_dict['fday3']['pfdys'] =  days_since_petalfall
					smry_dict['fday3']['fadys'] =  days_since_fungicide
					smry_dict['fday3']['rain'] = dly_rain
					smry_dict['fday3']['farain'] = rain_since_fungicide
				elif fday4 == theDate_dt:
					smry_dict['fday4']['risk'] = risk
					smry_dict['fday4']['alwh'] =  alwh
					smry_dict['fday4']['pfdys'] =  days_since_petalfall
					smry_dict['fday4']['fadys'] =  days_since_fungicide
					smry_dict['fday4']['rain'] = dly_rain
					smry_dict['fday4']['farain'] = rain_since_fungicide
				elif fday5 == theDate_dt:
					smry_dict['fday5']['risk'] = risk
					smry_dict['fday5']['alwh'] =  alwh
					smry_dict['fday5']['pfdys'] =  days_since_petalfall
					smry_dict['fday5']['fadys'] =  days_since_fungicide
					smry_dict['fday5']['rain'] = dly_rain
					smry_dict['fday5']['farain'] = rain_since_fungicide
		except:
			print_exception()
		return smry_dict


##### RUN PROGRAMS #####
	#	obtain everything necessary for apple scab summary
	def run_apple_scab (self,stn,end_date_dt,greentip,output,estimate):
		try:
			now = DateTime.now()
			from phen_events import phen_events_dict		
			from applescab_dict import disease_cycle_management		
			smry_dict = {}
			smry_dict['output'] = output
			smry_dict['stn'] = stn
			if not estimate:
				estimate = "no"
			if not end_date_dt: end_date_dt = now
			smry_dict['accend'] = end_date_dt
			end_date_tuple = (end_date_dt.year,end_date_dt.month,end_date_dt.day)
			
			if end_date_dt >= DateTime.DateTime(end_date_dt.year,11,1):		#November 1-December 31
				ucanid,smry_dict['station_name'] = get_metadata(stn)
				smry_dict['cycle'] = disease_cycle_management['overwinter']['cycle']
				smry_dict['manage'] = disease_cycle_management['overwinter']['management']
				return newaModel_io.apple_scab_overwinter(smry_dict)
			
			# greentip can either be passed into this program, read from a file, or estimated from degree day accumulation
			if not greentip:
				jan1_dt = DateTime.DateTime(end_date_dt.year,1,1)						
				daily_data, station_name = self.get_daily (stn, jan1_dt, end_date_dt)
				biofix_dd = phen_events_dict['macph_greentip_43']['dd'][2]					#by degree day accumulation
				ret_bf_date, ddaccum, ddmiss = self.accum_degday(daily_data, jan1_dt, end_date_dt, 'dd43be', biofix_dd, stn, station_name)
				if ret_bf_date: 
					greentip = ret_bf_date
				else:
					# before beginning of season
					smry_dict['station_name'] = station_name
					if ddmiss <= 2:
						smry_dict['message'] = 'You are approximately %d degree days (base 43F) from green tip. ' % (phen_events_dict['macph_greentip_43']['dd'][2]-ddaccum)
					else:
						smry_dict['message'] = ''
					smry_dict['ddaccum'] = int(round(ddaccum,0))
					smry_dict['ddmiss'] = ddmiss
					smry_dict['last_time'] = daily_data[-1][0]
					smry_dict['cycle'] = disease_cycle_management['early']['cycle']
					smry_dict['manage'] = disease_cycle_management['early']['management']
					return newaModel_io.apple_scab_early(smry_dict)

			smry_dict['greentip'] = greentip + DateTime.RelativeDate(hour=23)
			smry_dict = self.setup_dates (smry_dict,end_date_dt)
			start_date_dt = DateTime.DateTime(end_date_dt.year,3,1,1)	#Leave this March 1			
			
			# build Mills Table as dictionary
			mills_chart = self.build_mills_table()

			# just use observed data (no forecast) in years other than the current
			if end_date_dt.year != now.year:
				smry_dict['this_year'] = False
#				end_date_dt = end_date_dt + DateTime.RelativeDate(days = +6)
			else:
				smry_dict['this_year'] = True
#			# obtain hourly and daily data
#			hourly_data, daily_data, download_time, station_name, avail_vars = self.get_hddata2 (stn, start_date_dt, end_date_dt)
#			smry_dict['avail_vars'] = avail_vars
#			smry_dict['station_name'] = station_name
#			smry_dict['last_time'] = download_time
			### do calculations using only the observed data for table 3 ###
#			if len(hourly_data) > 0:
#				# pick out wet and dry periods
#				obs_wd_periods = self.get_wetdry(hourly_data,download_time,estimate)
#			else:
#				return self.nodata (stn, station_name, start_date_dt, end_date_dt)
#			if len(obs_wd_periods) > 0:
#				# combine wet periods and determine infection events
#				obs_infection_events, stat = self.get_infection(obs_wd_periods,mills_chart)
#				smry_dict['infection_events'] = obs_infection_events
#				smry_dict['stat'] = stat
#			else:
#				return newaCommon_io.errmsg('Insufficient data for model calculations.')
#			### now add the forecast data and do calculations again using observed and forecast data (current year)
#			if smry_dict['this_year']:
#				start_fcst_dt = DateTime.DateTime(*download_time) + DateTime.RelativeDate(hours = +1)
#				end_fcst_dt = end_date_dt + DateTime.RelativeDate(days = +6)
#				hourly_data = self.add_hrly_fcst(stn,hourly_data,start_fcst_dt,end_fcst_dt,True)
#				daily_data = self.hrly_to_dly(hourly_data)
#				wd_periods = self.get_wetdry(hourly_data,download_time,estimate)
#				if len(wd_periods) > 0:
#					# combine wet periods and determine infection events
#					infection_events, restat = self.get_infection(wd_periods,mills_chart)
#			else:
#				start_fcst_dt = end_date_dt + DateTime.RelativeDate(hours = +1)
#				end_fcst_dt = end_date_dt	
#				end_date_dt = end_date_dt + DateTime.RelativeDate(days = -6)
#				wd_periods = obs_wd_periods			
#				if len(wd_periods) > 0:
#					# combine wet periods and determine infection events
#					infection_events = obs_infection_events

			# obtain all hourly data for station (new method - get as much actual as available)
			end_fcst_dt = end_date_dt + DateTime.RelativeDate(days = +6) + DateTime.RelativeDate(hour=23,minute=0,second=0)
			hourly_data, download_time, station_name, avail_vars = self.get_hourly2 (stn, start_date_dt, end_fcst_dt)
			smry_dict['avail_vars'] = avail_vars
			smry_dict['station_name'] = station_name
			smry_dict['last_time'] = download_time
			start_fcst_dt = DateTime.DateTime(*download_time) + DateTime.RelativeDate(hours = +1)
			# append any available forecast data after end of observed data
			if end_fcst_dt >= start_fcst_dt:
				hourly_data = self.add_hrly_fcst(stn,hourly_data,start_fcst_dt,end_fcst_dt,True)
			# get last (forecast) value with precip amt
			smry_dict['lastqpf'] = self.getLastPrecip(hourly_data)
			# find when data ends
			last_data_dt = start_date_dt + DateTime.RelativeDate(hours = -1)
			for i in range(len(hourly_data), 0, -1):
				theTime,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags = hourly_data[i-1]
				if temp != miss or prcp != miss or lwet != miss or rhum != miss:
					last_data_dt = DateTime.DateTime(*theTime)
					break

			### do calculations for infection event table ###
			if len(hourly_data) > 0:
				# pick out wet and dry periods
				wd_periods = self.get_wetdry(hourly_data,download_time,estimate)
			else:
				return self.nodata (stn, station_name, start_date_dt, end_date_dt)
			if len(wd_periods) > 0:
				# combine wet periods and determine infection events
				infection_events, stat = self.get_infection(wd_periods,mills_chart)
				smry_dict['infection_events'] = infection_events
				smry_dict['stat'] = stat
#			else:
#				return newaCommon_io.errmsg('Insufficient data for model calculations.')

			smry_dict = self.check_infection(infection_events,end_date_dt,last_data_dt,smry_dict)

			# summary hourly data into daily
			daily_data = self.hrly_to_dly(hourly_data)
			# calculate base 0C degree days for ascospore maturity
			dd_data = self.degday_calcs(daily_data,greentip,end_fcst_dt,'dd0c', "prcp")
			
			if len(dd_data) > 0:
				# calculate ascospore maturity
				ascospore_dict,smry_dict['date95'] = self.ascospore_calcs(dd_data,daily_data)
				# add depletion
				ascospore_dict,smry_dict['all_released'] = self.depleteascospores(ascospore_dict, hourly_data)
				# don't use forecast 95% maturity and all-release dates
				if smry_dict['all_released'] and tuple(smry_dict['all_released']) > end_date_tuple:
					smry_dict['all_released'] = None
				if smry_dict['date95'] and tuple(smry_dict['date95']) > end_date_tuple:
					smry_dict['date95'] = None
				# add ascospore info to summary dictionary
				smry_dict = self.addascospore(ascospore_dict, smry_dict)
				# get wetness events for output
				wetness_dict = self.wettemp_event_calcs(hourly_data,start_date_dt,end_fcst_dt,start_fcst_dt,stn,estimate)
				smry_dict = self.add_wettemp(smry_dict,wetness_dict,start_date_dt,end_date_dt)
				# add daily average temperatures (no longer used in output), rain amount and pops to output
				smry_dict = self.add_temprain(smry_dict,end_date_dt,daily_data,smry_dict['this_year'])
			else:
				return self.nodata(stn, station_name, start_date_dt, end_date_dt)
				
			if smry_dict['all_released']:
				dayAfterAllReleased = DateTime.DateTime(*smry_dict['all_released']) + DateTime.RelativeDate(days=+1,hour=23,minute=0)
			else:
				dayAfterAllReleased = None
			if dayAfterAllReleased and dayAfterAllReleased <= end_date_dt:
				smry_dict['late_season'] = True
				smry_dict['cycle'] = disease_cycle_management['secondary']['cycle']
				ar_14days = DateTime.DateTime(*smry_dict['all_released']) + DateTime.RelativeDate(days=+14)
				ar_14days_str = "%s %s" % (month_names[ar_14days.month], ar_14days.day)
				smry_dict['manage'] = disease_cycle_management['secondary']['management'].replace("xxx14daysxxx",ar_14days_str)
			else:
				smry_dict['late_season'] = False
				smry_dict['cycle'] = disease_cycle_management['inseason']['cycle']
				smry_dict['manage'] = disease_cycle_management['inseason']['management']

#			write out summary table and chart of infection events
			return newaModel_io.apple_scab_log(smry_dict)
		except:
			print_exception()
			return newaCommon_io.errmsg('An error occurred attempting to process this request. Check inputs.')

	#--------------------------------------------------------------------------------------------		
	#	obtain everything necessary for apple fire blight summary
	def run_fire_blight (self,stn,end_date_dt,firstblossom,strep_spray,orchard_history,selbutton,output):
		try:
			smry_dict = {}
			smry_dict['output'] = output
			smry_dict['stn'] = stn
			if not end_date_dt: end_date_dt = DateTime.now()
			smry_dict['accend'] = end_date_dt
			jan1_dt = DateTime.DateTime(end_date_dt.year,1,1)						
			if not orchard_history: orchard_history = 2    #default
			smry_dict['orchard_history'] = orchard_history
			from phen_events import phen_events_dict
			from fireblight_dict import disease_cycle_management		
			
			# "fall" branch runs 9/16 to 10/31
			if end_date_dt >= DateTime.DateTime(end_date_dt.year,9,16) and end_date_dt <= DateTime.DateTime(end_date_dt.year,10,31,23):
				ucanid,smry_dict['station_name'] = get_metadata(stn)
				smry_dict['cycle'] = disease_cycle_management['fall']['cycle']
				smry_dict['manage'] = disease_cycle_management['fall']['management']
				smry_dict['fall'] = True
				return newaModel_io.fire_blight_late(smry_dict)

			# "dormant" branch runs from 11/1 to 3/1
			if end_date_dt >= DateTime.DateTime(end_date_dt.year,11,1) or end_date_dt < DateTime.DateTime(end_date_dt.year,3,1,0):		#off-season
				ucanid,smry_dict['station_name'] = get_metadata(stn)
				smry_dict['cycle'] = disease_cycle_management['dormant']['cycle']
				smry_dict['manage'] = disease_cycle_management['dormant']['management']
				return newaModel_io.fire_blight_dormant(smry_dict)

			# do not take these branches if a first blossom date is in the request (i.e. user input)
			if not firstblossom:
				# "late" branch runs 6/15 or petal fall to 9/15
				if end_date_dt >= DateTime.DateTime(end_date_dt.year,6,15) and end_date_dt <= DateTime.DateTime(end_date_dt.year,9,15):
					ucanid,smry_dict['station_name'] = get_metadata(stn)
					smry_dict['cycle'] = disease_cycle_management['late']['cycle']
					smry_dict['manage'] = disease_cycle_management['late']['management']
					smry_dict['fall'] = False
					return newaModel_io.fire_blight_late(smry_dict)
				else:
					daily_data, station_name = self.get_daily (stn, jan1_dt, end_date_dt)
					smry_dict['station_name'] = station_name
					if len(daily_data) > 0:
						biofix_dd = phen_events_dict['macph_pf_43']['dd'][3]
						ret_bf_date, ddaccum, ddmiss = self.accum_degday(daily_data, jan1_dt, end_date_dt, 'dd43be', biofix_dd, stn, station_name)
						if ret_bf_date:
							smry_dict['cycle'] = disease_cycle_management['late']['cycle']
							smry_dict['manage'] = disease_cycle_management['late']['management']
							smry_dict['fall'] = False
							return newaModel_io.fire_blight_late(smry_dict)
						else:
							smry_dict['ddaccum'] = int(round(ddaccum,0))
							smry_dict['ddmiss'] = ddmiss
							smry_dict['last_time'] = daily_data[-1][0]
					else:
						return self.nodata(stn, station_name, jan1_dt, end_date_dt)

				# check for first blossom open
				biofix_dd = phen_events_dict['macph_firstblossom_43']['dd'][2]					#by degree day accumulation
				ret_bf_date, ddaccum, ddmiss = self.accum_degday(daily_data, jan1_dt, end_date_dt, 'dd43be', biofix_dd, stn, station_name)
				if ret_bf_date: 
					firstblossom = ret_bf_date + DateTime.RelativeDate(hour=23)
				else:
					# "early branch" - before 6/15 and first blossom open
					ucanid,smry_dict['station_name'] = get_metadata(stn)
					dd_from_bloom = int(round(phen_events_dict['macph_firstblossom_43']['dd'][2]-ddaccum,0))
					smry_dict['cycle'] = disease_cycle_management['early']['cycle']
					smry_dict['manage'] = disease_cycle_management['early']['management'].replace("xxxdddiffxxx",str(dd_from_bloom))
					return newaModel_io.fire_blight_early(smry_dict)
			else:
				# need degree day accumulation through current date
				daily_data, station_name = self.get_daily (stn, jan1_dt, end_date_dt)
				if len(daily_data) > 0:
					ret_bf_date, ddaccum, ddmiss = self.accum_degday(daily_data, jan1_dt, end_date_dt, 'dd43be', 99999, stn, station_name)
					smry_dict['ddaccum'] = int(round(ddaccum,0))
					smry_dict['ddmiss'] = ddmiss
					smry_dict['last_time'] = daily_data[-1][0]

			# now "in season" - between first blossom and petal fall
			start_date_dt = firstblossom
			data_start = min(start_date_dt, smry_dict['accend'] + DateTime.RelativeDate(days=-2))
			data_start = data_start + DateTime.RelativeDate(hour=0)

			# obtain all hourly data for station (new method - get as much actual as available)
			end_fcst_dt = end_date_dt + DateTime.RelativeDate(days = +6) + DateTime.RelativeDate(hour=23,minute=0,second=0)
			hourly_data, download_time, station_name, avail_vars = self.get_hourly2 (stn, data_start, end_fcst_dt)
			smry_dict['download_time'] = download_time
			start_fcst_dt = DateTime.DateTime(*download_time) + DateTime.RelativeDate(hours = +1)
			# append any available forecast data after end of observed data
			if end_fcst_dt >= start_fcst_dt:
				hourly_data = self.add_hrly_fcst(stn,hourly_data,start_fcst_dt,end_fcst_dt)
			# get last (forecast) value with precip amt
			smry_dict['lastqpf'] = self.getLastPrecip(hourly_data)

			if len(hourly_data) > 0:
				# calculate degree hours using Tim Smith's table
				deghrs = self.deghr_calcs(hourly_data,start_date_dt,end_fcst_dt)
				# obtain wetness events for output
				wetness_dict = self.wetness_moreevent_calcs(hourly_data,data_start,end_fcst_dt,start_fcst_dt,stn,'no')
				# calculate eip
				eip_results = self.eip_calcs(hourly_data,wetness_dict,start_date_dt,end_fcst_dt,strep_spray)
				# determine risk
				smry_dict = self.add_risks(smry_dict,deghrs,eip_results,end_date_dt,orchard_history,start_date_dt,strep_spray)
				smry_dict = self.add_wetness(smry_dict,wetness_dict,start_date_dt,end_date_dt)
				# get 12-hour pops
				from ndfd.get_precip_forecast import get_precip_forecast
				pops_list = get_precip_forecast (stn,DateTime.now(),end_fcst_dt)
				smry_dict = self.add_pops(smry_dict,end_date_dt,pops_list)
			else:
				return self.nodata(stn, station_name, start_date_dt, end_date_dt)

			# add necessary information for display to dictionary
			smry_dict['firstblossom'] = firstblossom
			smry_dict['strep_spray'] = strep_spray
			smry_dict['selbutton'] = selbutton
			smry_dict['station_name'] = station_name
			smry_dict['cycle'] = disease_cycle_management['inseason']['cycle']
			smry_dict['manage'] = disease_cycle_management['inseason']['management']
			smry_dict['avail_vars'] = avail_vars

#			write out summary table 
			return newaModel_io.fire_blight_log(smry_dict)
		except:
			print_exception()
			return newaCommon_io.errmsg('An error occurred attempting to process this request. Check inputs.')
			
	#--------------------------------------------------------------------------------------------		
	#	obtain everything necessary for shoot blight summary
	def run_shoot_blight(self,stn,end_date_dt,infection_event,symptoms,selbutton,output):
		try:
			smry_dict = {}
			smry_dict['output'] = output
			# setup determined by button selected
			if selbutton and selbutton in ['infect','symptoms']:
				if selbutton == 'infect':
					if not infection_event: return newaCommon_io.errmsg('Error processing form; enter Infection Event Date')
					smry_dict['infection_event'] = infection_event
					smry_dict['symptoms'] = None
					symptoms = None
					smry_dict['infection_est'] = None
				elif selbutton == 'symptoms':
					if not symptoms: return newaCommon_io.errmsg('Error processing form; enter Symptom Occurrence Date')
					smry_dict['symptoms'] = symptoms
					smry_dict['infection_event'] = None
					infection_event = None
					smry_dict['recommend'] = None
			else:
				return newaCommon_io.errmsg('Error processing form; check input')
				
			# determine start and end dates of degree days needed for calculations
			if infection_event:
				start_date_dt = infection_event
				end_date_dt = DateTime.DateTime(infection_event.year,12,31,23)
			else:
				start_date_dt = DateTime.DateTime(symptoms.year,1,1,1)
				end_date_dt = symptoms

			# obtain daily data
			daily_data, station_name = self.get_daily (stn, start_date_dt, end_date_dt)

			if len(daily_data) > 0:
				# calculate degree days for period
				degday_dict = self.degday_calcs(daily_data, start_date_dt, end_date_dt, 'dd55be', "accum")
				if infection_event:
					# get accumulation and recommendation
					smry_dict['ddaccum'], smry_dict['last_day_accum'], smry_dict['recommend'] = self.shoot_infection(degday_dict)
					return newaModel_io.shoot_blight_infection_log(smry_dict)
				else:
					# work back to find infection date
					smry_dict['ddaccum'], smry_dict['infection_est'], smry_dict['last_day_accum'] = self.shoot_symptoms(degday_dict)
					return newaModel_io.shoot_blight_symptoms_log(smry_dict)
			else:
				# no data returns
				if infection_event:
					smry_dict['ddaccum'] = None
					smry_dict['last_day_accum'] = None
					smry_dict['recommend'] = "No symptoms yet"
					return newaModel_io.shoot_blight_infection_log(smry_dict)
				else:
					smry_dict['ddaccum'] = None
					smry_dict['last_day_accum'] = None
					smry_dict['infection_est'] = None
					return newaModel_io.shoot_blight_symptoms_log(smry_dict)
		except:
			print_exception()

	#--------------------------------------------------------------------------------------------		
	#	obtain everything necessary for apple fire blight summary
	def run_sooty_blotch (self,stn,end_date_dt,petalfall,fungicide,harvest,selbutton,output):
		try:
			smry_dict = {}
			smry_dict['output'] = output
			from phen_events import phen_events_dict		
			if not end_date_dt: end_date_dt = DateTime.now()
			
			if end_date_dt >= DateTime.DateTime(end_date_dt.year,9,16):		#off-season#################### CHECK DORMANT DATE ##########
				return newaModel_io.sooty_blotch_dormant(smry_dict)
			
			smry_dict['stn'] = stn
			smry_dict['accend'] = end_date_dt
			ddaccum = miss
			ddmiss = miss

			# biofix can either be passed into this program, read from a file, or estimated from degree day accumulation
			if not petalfall:
				petalfall = self.get_biofix(stn,'pf',end_date_dt.year)					#from file
				if not petalfall:
					jan1_dt = DateTime.DateTime(end_date_dt.year,1,1)						
					daily_data, station_name = self.get_daily (stn, jan1_dt, end_date_dt)
					biofix_dd = phen_events_dict['macph_pf_43']['dd'][2]					#by degree day accumulation
					ret_bf_date, ddaccum, ddmiss = self.accum_degday(daily_data, jan1_dt, end_date_dt, 'dd43be', biofix_dd, stn, station_name)
					if ret_bf_date: 
						petalfall = ret_bf_date + DateTime.RelativeDate(hour=23)
					else:
						# before beginning of season
						smry_dict['station_name'] = station_name
						if ddmiss <= 2:
							smry_dict['message'] = 'You are approximately %d degree days from petal fall - the point at which apples and pears become susceptible to infection.' % (phen_events_dict['macph_pf_43']['dd'][2]-ddaccum)
						else:
							smry_dict['message'] = 'You are approximately %d degree days from petal fall, but 2 or more days of GDD are missing; accumulation could be low.' % (phen_events_dict['macph_pf_43']['dd'][2]-ddaccum)
						smry_dict['ddaccum'] = int(round(ddaccum,0))
						smry_dict['ddmiss'] = ddmiss
						smry_dict['last_time'] = daily_data[-1][0]
						return newaModel_io.sooty_blotch_early(smry_dict)
			
			start_date_dt = petalfall

			# obtain hourly data
			hourly_data, download_time, station_name, avail_vars = self.get_hourly2 (stn, start_date_dt, end_date_dt)

			if len(hourly_data) > 0:
				# append forecast data
				start_fcst_dt = DateTime.DateTime(*download_time) + DateTime.RelativeDate(hours = +1)
				end_fcst_dt = end_date_dt + DateTime.RelativeDate(days = +6)
				hourly_data = self.add_hrly_fcst(stn,hourly_data,start_fcst_dt,end_fcst_dt)
				#get daily rain, leaf wetness and dew
				wetness_dict = self.wetness_event_calcs(hourly_data,start_date_dt,end_fcst_dt,start_fcst_dt,stn,'no')
				# determine risk and add required output to smry_dict
				smry_dict = self.process_sooty_blotch (smry_dict,wetness_dict,petalfall,fungicide,end_date_dt,start_date_dt)
				# get 12-hour pops and add to dictionary
				from ndfd.get_precip_forecast import get_precip_forecast
				pops_list = get_precip_forecast (stn,DateTime.now(),end_fcst_dt)
				smry_dict = self.add_pops(smry_dict,end_date_dt,pops_list)
			else:
				return self.nodata(stn, station_name, start_date_dt, end_date_dt)
				
			# add necessary information for display to dictionary
			smry_dict['petalfall'] = petalfall
			smry_dict['fungicide'] = fungicide
			smry_dict['harvest'] = harvest
			smry_dict['selbutton'] = selbutton
			smry_dict['station_name'] = station_name
			smry_dict['last_time'] = download_time
			smry_dict['ddaccum'] = ddaccum
			smry_dict['ddmiss'] = ddmiss
			smry_dict['message'] = 'At petal fall, apples and pears become susceptible to Sooty Blotch/Flyspeck. Petal fall usually occurs once %d to %d degree days (DD) base 43 have accumulated from January 1.' % (phen_events_dict['macph_pf_43']['dd'][2],phen_events_dict['macph_pf_43']['dd'][3])
			smry_dict['avail_vars'] = avail_vars

#			write out summary table 
			return newaModel_io.sooty_blotch_log(smry_dict)
		except:
			print_exception()
			return newaCommon_io.errmsg('An error occurred attempting to process this request. Check inputs.')
			
	#--------------------------------------------------------------------------------------------		
	#	obtain everything necessary for apple pest summary
	def run_apple_pest(self,stn, pest, accend, bf_date, bf2_date, bf3_date, output):
		try:
			smry_dict = {}
			smry_dict['output'] = output
			smry_dict['pest'] = pest
			if not accend:
				accend = DateTime.now()
				
			smry_dict['stn'] = stn
			smry_dict['accend'] = accend

			from phen_events import phen_events_dict

			# determine information needed for calculations for particular pest
			if pest == 'apple-pc':
				from pc_info_dict import pest_status_management	
				biofix_dd = 303			#updated from 580 for base 50 petal fall  3/2016
				biofix2_dd = 99999
			elif pest == 'apple-oblr':
				from oblr_info_dict import pest_status_management	
				biofix_dd = 1212 		#updated from phen_events_dict['oblr_catch1_43']['dd'][3]  4/2016
				biofix2_dd = 99999
			elif pest == 'apple-stlm':
				from stlm_info_dict import pest_status_management	
				biofix_dd = 274			#updated from 701 (use phenology through 700 degree days)  4/2016
				biofix2_dd = 977		#updated from 1200  4/2016
				biofix3_dd = 99999
			elif pest == 'apple-cm':
				from cm_info_dict import pest_status_management	
				biofix_dd = 404			#updated from 611 for base 50 3/2016
				biofix2_dd = 1501
				biofix3_dd = 99999
			elif pest == 'apple-ofm':
				from ofm_info_dict import pest_status_management	
				biofix_dd = 378			#updated from 450  4/2016
				biofix2_dd = 1241		#updated from 1100  4/2016, not 1066
				biofix3_dd = 1820		#updated from 1500  4/2016, not 2436
				biofix4_dd = 99999
			elif pest == 'apple-maggot':
				from am_info_dict import pest_status_management	
				biofix_dd = 1297		#updated from 2116 for base 50 3/2016
				biofix2_dd = 99999
			elif pest == 'apple-sjs':
				from sjs_info_dict import pest_status_management	
				biofix_dd = 340
				biofix2_dd = 1057
				biofix3_dd = 99999
			else:
				return newaCommon_io.errmsg('A model is not available for the pest you selected.')
				
			biofix_phenology = pest_status_management['biofix_phenology']
			smry_dict['biofix_phenology'] = biofix_phenology
			if pest_status_management.has_key('biofix2_phenology'):
				biofix2_phenology = pest_status_management['biofix2_phenology']
				smry_dict['biofix2_phenology'] = biofix2_phenology
			else:
				biofix2_phenology = None
				smry_dict['biofix2_phenology'] = None
			if pest_status_management.has_key('biofix3_phenology'):
				biofix3_phenology = pest_status_management['biofix3_phenology']
				smry_dict['biofix3_phenology'] = biofix3_phenology
			else:
				biofix3_phenology = None
				smry_dict['biofix3_phenology'] = None
			smry_dict['pest_name'] = pest_status_management['pest_name']
			start_date_dt = DateTime.DateTime(accend.year,1,1)
			end_date_dt = accend

			if bf3_date and bf3_date <= end_date_dt:
				start_date_dt = bf3_date
				phenology = biofix3_phenology
				biofix_status = "post_biofix3"
				bf_miss = None
			elif bf3_date and bf3_date > end_date_dt:
				start_date_dt = bf2_date
				phenology = biofix2_phenology
				biofix_status = "post_biofix2"
				bf_miss = None
			else:
				if bf2_date and bf2_date <= end_date_dt:
					start_date_dt = bf2_date
					phenology = biofix2_phenology
					biofix_status = "post_biofix2"
					bf_miss = None
				elif bf2_date and bf2_date > end_date_dt:
					start_date_dt = bf_date
					phenology = biofix_phenology
					biofix_status = "post_biofix"
					bf_miss = None
				else:
#					biofix file no longer maintained, so comment following 2 lines
#					if not bf_date and pest_status_management['biofix_abbrev']:
#						bf_date = self.get_biofix(stn,pest_status_management['biofix_abbrev'],start_date_dt.year)	#check file
					if bf_date and bf_date <= end_date_dt:
						start_date_dt = bf_date
						phenology = biofix_phenology
						biofix_status = "post_biofix"
						bf_miss = None
					elif bf_date and bf_date > end_date_dt:
						phenology = None
						biofix_status = "pre_biofix"
						bf_miss = 0
					else:
						phenology = None
						biofix_status = 'pre_biofix'
						bf_miss = None

			# obtain daily data
			daily_data, station_name = self.get_daily (stn, start_date_dt, end_date_dt)
			smry_dict['station_name'] = station_name

			if len(daily_data) > 0:
				# calculate base 43 degree days for phenology
				if biofix_status == 'pre_biofix':
					if pest in ['apple-pc', 'apple-maggot', 'apple-cm', 'apple-sjs']:
						smry_dict['basetemp'] = 50
					else:
						smry_dict['basetemp'] = 43
					dd_type = 'dd%dbe' % smry_dict['basetemp']
					ret_bf_date, ddaccum, ddmiss = self.accum_degday(daily_data, start_date_dt, end_date_dt, dd_type, biofix_dd, stn, station_name)
					if ret_bf_date and not bf_date:
						bf_miss = ddmiss
						bf_date = ret_bf_date
						biofix_status = 'post_biofix'
						phenology = biofix_phenology
					else:
						ret_date, pddaccum, ddmiss = self.accum_degday(daily_data, start_date_dt, end_date_dt, 'dd43be', biofix_dd, stn, station_name)
						phen_stages = []		#order latest to earliest
						if pest == 'apple-stlm':
							phen_list = ['macph_pink_43','macph_tightcluster_43','macph_halfgreen_43','macph_greentip_43','macph_st_43','macph_dormant_43']
						elif pest == 'apple-ofm':
							phen_list = ['macph_bloom_43','macph_pink_43','macph_tightcluster_43','macph_halfgreen_43','macph_greentip_43','macph_st_43','macph_dormant_43']
						else:
							phen_stages.append(("Post Petal Fall",580))
							phen_list = ['macph_pf_43','macph_bloom_43','macph_pink_43','macph_tightcluster_43','macph_halfgreen_43','macph_greentip_43','macph_st_43','macph_dormant_43']
						for phen in phen_list:
							phen_stages.append((phen_events_dict[phen]['name'],phen_events_dict[phen]['dd'][2]))
						for stage,stage_dd in phen_stages:
							if pddaccum >= stage_dd:
								phenology = stage
								break

				# calculate degree days for period after biofix, might be different base
				if biofix_status == 'post_biofix':
					smry_dict['basetemp'] = pest_status_management['basetemp']
					dd_type = 'dd%dbe' % smry_dict['basetemp']
					start_date_dt = bf_date
					ret_bf2_date, ddaccum, ddmiss = self.accum_degday(daily_data, start_date_dt, end_date_dt, dd_type, biofix2_dd, stn, station_name)
					if biofix2_phenology and ret_bf2_date and not bf2_date:
						bf2_date = ret_bf2_date
						biofix_status = 'post_biofix2'
						phenology = biofix2_phenology

				# calculate degree days for period after second biofix
				if biofix_status == 'post_biofix2':
					smry_dict['basetemp'] = pest_status_management['basetemp']
					dd_type = 'dd%dbe' % smry_dict['basetemp']
					start_date_dt = bf2_date
					ret_bf3_date, ddaccum, ddmiss = self.accum_degday(daily_data, start_date_dt, end_date_dt, dd_type, biofix3_dd, stn, station_name)
					if biofix3_phenology and ret_bf3_date and not bf3_date:
						bf3_date = ret_bf3_date
						biofix_status = 'post_biofix3'
						phenology = biofix3_phenology
							
				# calculate degree days for period after third biofix
				if biofix_status == 'post_biofix3':
					smry_dict['basetemp'] = pest_status_management['basetemp']
					dd_type = 'dd%dbe' % smry_dict['basetemp']
					start_date_dt = bf3_date
					unused_date, ddaccum, ddmiss = self.accum_degday(daily_data, start_date_dt, end_date_dt, dd_type, biofix4_dd, stn, station_name)
							
				# get status and recommendation
				for k in pest_status_management[biofix_status].keys():
					psmk = pest_status_management[biofix_status][k]
					if psmk.has_key('ddlo'):
						if ddaccum >= int(psmk['ddlo']) and ddaccum <= int(psmk['ddhi']):
							smry_dict['stage']  = psmk['stage']
							smry_dict['status'] = psmk['status']
							smry_dict['manage'] = psmk['management']
							if psmk.has_key('pesticide_link'):
								smry_dict['manage'] = '%s <a href="%s" target="_blank">Pesticide information</a>' % (psmk['management'],psmk['pesticide_link'])
							break
					elif psmk.has_key('datelo'):
						if isinstance(psmk['datelo'],tuple):
							datelo = DateTime.DateTime(accend.year,*psmk['datelo'])
						else:
							datelo = bf_date + DateTime.RelativeDate(days=psmk['datelo'],hour=0)
						if isinstance(psmk['datehi'],tuple):
							datehi = DateTime.DateTime(accend.year,*psmk['datehi'])
						else:
							datehi = bf_date + DateTime.RelativeDate(days=psmk['datehi'],hour=23)
						if accend >= datelo and accend <= datehi:
							smry_dict['stage']  = psmk['stage']
							smry_dict['status'] = psmk['status']
							smry_dict['manage'] = psmk['management']
							if psmk.has_key('pesticide_link'):
								smry_dict['manage'] = '%s <a href="%s" target="_blank">Pesticide information</a>' % (psmk['management'],psmk['pesticide_link'])
							break
					else:
						return newaCommon_io.errmsg('Error determining recommendations')
				else:
					smry_dict['stage']  = "Not defined"
					smry_dict['status'] = "Not defined"
					smry_dict['manage'] = "Not defined"

				# get other information needed for display
				smry_dict['last_day'] = daily_data[-1][0]
				if biofix_status == 'pre_biofix':
					smry_dict['phenology'] = phenology
					if phenology != "Post Petal Fall":
						smry_dict['phen_pic'] = ('Apple_'+phenology).replace(" ","_")
					else:
						smry_dict['phen_pic'] = None
					smry_dict['phen_stages'] = phen_stages
					smry_dict['pest_stages'] = None
				else:
					smry_dict['phenology'] = None
					smry_dict['phen_pic'] = None
					smry_dict['phen_stages'] = None
					# build pest stage list
					smry_dict['pest_stages'] = []
					for bfs in ['post_biofix','post_biofix2','post_biofix3']:
						if pest_status_management.has_key(bfs):
							for k in pest_status_management[bfs].keys():
								psmk = pest_status_management[bfs][k]
								smry_dict['pest_stages'].append((psmk['altref'][0],psmk['stage']))	
					if smry_dict['stage']  == "Not defined":
						smry_dict['pest_stages'].append(("Not defined","Not defined"))	
					
				if bf_date:
					smry_dict['bf_date'] = [bf_date.year,bf_date.month,bf_date.day]
				else:
					smry_dict['bf_date'] = None
				if bf2_date:
					smry_dict['bf2_date'] = [bf2_date.year,bf2_date.month,bf2_date.day]
				else:
					smry_dict['bf2_date'] = None
				if bf3_date:
					smry_dict['bf3_date'] = [bf3_date.year,bf3_date.month,bf3_date.day]
				else:
					smry_dict['bf3_date'] = None

				if (smry_dict['bf_date'] and biofix_status == 'pre_biofix') or (smry_dict['bf2_date'] and biofix_status == 'post_biofix') or\
				   (smry_dict['bf3_date'] and biofix_status == 'post_biofix2'):
					smry_dict['ddaccum'] = miss
					smry_dict['ddmiss']  = miss
				else:
					smry_dict['ddaccum'] = int(ddaccum)
					smry_dict['ddmiss']  = ddmiss
				smry_dict['bf_miss'] = bf_miss

				# send results for display
				return newaModel_io.apple_pest_results(smry_dict)
			else:
				return self.nodata(stn, station_name, start_date_dt, end_date_dt)
		except:
			print_exception()						

	#--------------------------------------------------------------------------------------------		
	#	obtain everything necessary for apple pest update
	def run_pest_update (self,pest,altref,output):
		try:
			smry_dict = {}
			# determine information needed for calculations for particular pest
			if pest == 'apple-pc':
				from pc_info_dict import pest_status_management	
			elif pest == 'apple-oblr':
				from oblr_info_dict import pest_status_management	
			elif pest == 'apple-stlm':
				from stlm_info_dict import pest_status_management	
			elif pest == 'apple-ofm':
				from ofm_info_dict import pest_status_management	
			elif pest == 'apple-cm':
				from cm_info_dict import pest_status_management	
			elif pest == 'apple-maggot':
				from am_info_dict import pest_status_management	
			elif pest == 'apple-sjs':
				from sjs_info_dict import pest_status_management	
			else:
				return newaCommon_io.errmsg('A model is not available for the pest you selected.')
							
			# get status and recommendation
			for biofix_status in ['pre_biofix','post_biofix','post_biofix2','post_biofix3']:
				if pest_status_management.has_key(biofix_status):
					for k in pest_status_management[biofix_status].keys():
						psmk = pest_status_management[biofix_status][k]
						if altref in psmk['altref']:
							smry_dict['stage']  = psmk['stage']
							smry_dict['status'] = psmk['status']
							smry_dict['manage'] = psmk['management']
							if psmk.has_key('pesticide_link'):
								smry_dict['manage'] = '%s <a href="%s" target="_blank">Pesticide information</a>' % (psmk['management'],psmk['pesticide_link'])

							if biofix_status == 'pre_biofix':
								smry_dict['pest_stages'] = None
							else:
								# build pest stage list
								smry_dict['pest_stages'] = []
								for bfs in ['post_biofix','post_biofix2','post_biofix3']:
									if pest_status_management.has_key(bfs):
										for k in pest_status_management[bfs].keys():
											psmk = pest_status_management[bfs][k]
											smry_dict['pest_stages'].append((psmk['altref'][0],psmk['stage']))	
							return newaModel_io.apple_status_results(smry_dict)
			else:
				smry_dict['stage']  = "Not applicable"
				smry_dict['status'] = "Not applicable"
				smry_dict['manage'] = "Not applicable"
				smry_dict['pest_stages'] = None
				return newaModel_io.apple_status_results(smry_dict)
		except:
			print_exception()

#--------------------------------------------------------------------------------------------		
class Grape (Base,Apple,Models):

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
				if lwet == miss and rhum != miss:
					if rhum >= 90 or prcp > 0.00:
						lwet = 60
					else:
						lwet = 0
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
	# combine wet events and check for infection
	def get_grape_infection (self,periods):
		infection_events = []
		try:
			wet_end = None
			for start,end,length,temp,prec,ph,br in periods:
				start_dt = DateTime.DateTime(*start)
				if not wet_end or (start_dt-wet_end_dt).hours > 11:
					if wet_end:
 						# process last event
						avg_temp = temp_sum/wet_hrs
						ph_infect = self.get_phomop(wet_hrs,avg_temp,prec_sum)
						br_infect = self.get_blackrot(wet_hrs,avg_temp,prec_sum)
						if ph_infect == 'Infection' or br_infect == 'Infection':
							infection_events.append((wet_start,wet_end,wet_hrs,avg_temp,prec_sum,combined,ph_infect,br_infect))
					temp_sum = 0.
					prec_sum = 0.
					wet_hrs = 0.				
					wet_start = start
					combined = 0
				else:
					combined = 1
				wet_end = end
				if wet_end != miss: 			#should only be missing if last period is "in progress"
					wet_end_dt = DateTime.DateTime(*wet_end)
				else:
					wet_end_dt = None
				wet_hrs = wet_hrs + length
				temp_sum = temp_sum + (temp*length)
				prec_sum = prec_sum + prec
			# process last event in list
			avg_temp = temp_sum/wet_hrs
			ph_infect = self.get_phomop(wet_hrs,avg_temp,prec_sum)
			br_infect = self.get_blackrot(wet_hrs,avg_temp,prec_sum)
			if ph_infect == 'Infection' or br_infect == 'Infection':
				infection_events.append((wet_start,wet_end,wet_hrs,avg_temp,prec_sum,combined,ph_infect,br_infect))
		except:
			print_exception()
		return infection_events

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
	# determine whether or not there was a powdery mildew infection during this wet period
	def get_pmildew (self,prcp,tave):
		try:
			if prcp == miss or tave == miss:
				pm = '-----'
			elif prcp >= 0.10 and tave >= 50:
				pm = "Infection"
			else:
				pm = "No infection"	
		except:
			print_exception()
		return pm
		
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
	# add infection events to dictionary
	def add_infection_events (self,smry_dict,pmildew_list,infect_list,start_date_dt,end_date_dt,download_time,last_prcp_dt):
		try:
			no_prcp_day = last_prcp_dt + DateTime.RelativeDate(days = +1,hour=0,minute=0,second=0)
			day0 =  end_date_dt + DateTime.RelativeDate(hour=0,minute=0,second=0)
			pday1 = day0 + DateTime.RelativeDate(days=-1)
			pday2 = day0 + DateTime.RelativeDate(days=-2)
			fday1 = day0 + DateTime.RelativeDate(days=+1)
			fday2 = day0 + DateTime.RelativeDate(days=+2)
			fday3 = day0 + DateTime.RelativeDate(days=+3)
			fday4 = day0 + DateTime.RelativeDate(days=+4)
			fday5 = day0 + DateTime.RelativeDate(days=+5)
			smry_dict['day0']['pmil']  = 'NA'
			smry_dict['pday1']['pmil'] = 'NA'
			smry_dict['pday2']['pmil'] = 'NA'
			smry_dict['fday1']['pmil'] = 'NA'
			smry_dict['fday2']['pmil'] = 'NA'
			smry_dict['fday3']['pmil'] = 'NA'
			smry_dict['fday4']['pmil'] = 'NA'
			smry_dict['fday5']['pmil'] = 'NA'
			smry_dict['day0']['phom']  = 'NA'
			smry_dict['pday1']['phom'] = 'NA'
			smry_dict['pday2']['phom'] = 'NA'
			smry_dict['fday1']['phom'] = 'NA'
			smry_dict['fday2']['phom'] = 'NA'
			smry_dict['fday3']['phom'] = 'NA'
			smry_dict['fday4']['phom'] = 'NA'
			smry_dict['fday5']['phom'] = 'NA'
			smry_dict['day0']['brot']  = 'NA'
			smry_dict['pday1']['brot'] = 'NA'
			smry_dict['pday2']['brot'] = 'NA'
			smry_dict['fday1']['brot'] = 'NA'
			smry_dict['fday2']['brot'] = 'NA'
			smry_dict['fday3']['brot'] = 'NA'
			smry_dict['fday4']['brot'] = 'NA'
			smry_dict['fday5']['brot'] = 'NA'

			download_dt = DateTime.DateTime(*download_time)
			if day0 < no_prcp_day and day0 <= download_dt:
				smry_dict['day0']['phom']  = 'No infection'
				smry_dict['day0']['brot']  = 'No infection'
				smry_dict['day0']['pmil']  = 'No infection'
			if pday1 < no_prcp_day and pday1 <= download_dt:
				smry_dict['pday1']['phom'] = 'No infection'
				smry_dict['pday1']['brot'] = 'No infection'
				smry_dict['pday1']['pmil'] = 'No infection'
			if pday2 < no_prcp_day and pday2 <= download_dt:
				smry_dict['pday2']['phom'] = 'No infection'
				smry_dict['pday2']['brot'] = 'No infection'
				smry_dict['pday2']['pmil'] = 'No infection'
			if fday1 < no_prcp_day and fday1 <= download_dt:
				smry_dict['fday1']['phom'] = 'No infection'
				smry_dict['fday1']['brot'] = 'No infection'
				smry_dict['fday1']['pmil'] = 'No infection'
			if fday2 < no_prcp_day and fday2 <= download_dt:
				smry_dict['fday2']['phom'] = 'No infection'
				smry_dict['fday2']['brot'] = 'No infection'
				smry_dict['fday2']['pmil'] = 'No infection'
			if fday3 < no_prcp_day and fday3 <= download_dt:
				smry_dict['fday3']['phom'] = 'No infection'
				smry_dict['fday3']['brot'] = 'No infection'
				smry_dict['fday3']['pmil'] = 'No infection'
			if fday4 < no_prcp_day and fday4 <= download_dt:
				smry_dict['fday4']['phom'] = 'No infection'
				smry_dict['fday4']['brot'] = 'No infection'
				smry_dict['fday4']['pmil'] = 'No infection'
			if fday5 < no_prcp_day and fday5 <= download_dt:
				smry_dict['fday5']['phom'] = 'No infection'
				smry_dict['fday5']['brot'] = 'No infection'
				smry_dict['fday5']['pmil'] = 'No infection'
				
			# add pmildew for last three days, forecast next 5 days
			for dt,pm in pmildew_list:
				theDate_dt = DateTime.DateTime(*dt) + DateTime.RelativeDate(hour=0,minute=0,second=0)
				for td,std in [(day0,'day0'),(pday1,'pday1'),(pday2,'pday2'),(fday1,'fday1'),(fday2,'fday2'),(fday3,'fday3'),(fday4,'fday4'),(fday5,'fday5')]:
					if td == theDate_dt: 
						smry_dict[std]['pmil'] = pm
						continue
			# same for phomopsis and black rot
			for wet_start,wet_end,wet_hrs,avg_temp,prec_sum,combined,ph_infect,br_infect in infect_list:
#				print wet_start,wet_end,wet_hrs,avg_temp,prec_sum,combined,ph_infect,br_infect
				start_dt = DateTime.DateTime(*wet_start) + DateTime.RelativeDate(hour=0,minute=0,second=0)
				if wet_end == miss:
					theDate_dt = download_dt + DateTime.RelativeDate(hour=0,minute=0,second=0)
				else:
					theDate_dt = DateTime.DateTime(*wet_end) + DateTime.RelativeDate(hour=0,minute=0,second=0)
				for td,std in [(day0,'day0'),(pday1,'pday1'),(pday2,'pday2'),(fday1,'fday1'),(fday2,'fday2'),(fday3,'fday3'),(fday4,'fday4'),(fday5,'fday5')]:
					if td == theDate_dt: 
						if smry_dict[std]['phom'] != "Infection": smry_dict[std]['phom'] = ph_infect
						if smry_dict[std]['brot'] != "Infection": smry_dict[std]['brot'] = br_infect
						continue
					elif td >= start_dt and td < theDate_dt:
						if ph_infect == "Infection": smry_dict[std]['phom'] = "Combined"
						if br_infect == "Infection": smry_dict[std]['brot'] = "Combined"
						continue						
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
	#	obtain everything necessary for dmcast
	def run_dmcast(self,stn,end_date_dt,cultivar,output):
		from dmcast import downy_mildew
		from newaCommon.sister_info import sister_info
		from newaCommon.stn_info import stn_info

		try:
			smry_dict = {}
			smry_dict['output'] = output
			smry_dict['stn'] = stn
			if not end_date_dt: end_date_dt = DateTime.now()			
			smry_dict['accend'] = end_date_dt
			if not cultivar: cultivar = "Concord"
			smry_dict['cultivar'] = cultivar
			smry_dict['station_name'] = stn_info[stn]["name"]
			smry_dict['sister'] = sister_info[stn]
				
			# add necessary information for display to dictionary
			obj = downy_mildew.general_dm(smry_dict)
			smry_dict = obj.run_dm()
	
			# write out results
			return newaModel_io.dmcast_results(smry_dict)
		except:
			print_exception()
			return newaCommon_io.errmsg('An error occurred attempting to process this request. Check inputs.')

	#--------------------------------------------------------------------------------------------		
	#	obtain everything necessary for grape berry moth summary
	def run_berry_moth(self,stn, accend, bf_date, output):
		pest = "berry_moth"
		try:
			smry_dict = {}
			smry_dict['output'] = output
			smry_dict['pest'] = pest
			if not accend:
				accend = DateTime.now()
				
			if output == 'standalone':
				smry_dict['stn'] = stn
				smry_dict['accend'] = accend

			from phen_events import phen_events_dict

			# determine information needed for calculations for particular disease
			if pest == 'berry_moth':
				from gbm_info_dict import pest_status_management	
				if accend >= DateTime.DateTime(accend.year,11,1):
					smry_dict['pest_name'] = pest_status_management['pest_name']
					smry_dict['status'] = pest_status_management['pre_biofix'][0]['status']
					smry_dict['manage'] = pest_status_management['pre_biofix'][0]['management']
					return newaModel_io.berry_moth_dormant(smry_dict)
				biofix_dd = phen_events_dict['gbm_bloom_50']['dd'][3]
				biofix2_dd = 99999
			else:
				return newaCommon_io.errmsg('A model is not available for the disease you selected.')
				
			biofix_phenology = pest_status_management['biofix_phenology']
			smry_dict['biofix_phenology'] = biofix_phenology
			smry_dict['pest_name'] = pest_status_management['pest_name']
			start_date_dt = DateTime.DateTime(accend.year,1,1)
			end_date_dt = accend

			if bf_date and bf_date <= end_date_dt:
				start_date_dt = bf_date
				biofix_status = "post_biofix"
				bf_miss = None
			elif bf_date and bf_date > end_date_dt:
				biofix_status = "pre_biofix"
				bf_miss = 0
			else:
				biofix_status = 'pre_biofix'
				bf_miss = None

			# obtain daily data
			hourly_data, daily_data, download_time, station_name, avail_vars = self.get_hddata2 (stn, start_date_dt, end_date_dt)
			smry_dict['station_name'] = station_name
			smry_dict['last_time'] = download_time

			if len(daily_data) > 0:
				# calculate base 50 degree days for phenology
				if biofix_status == 'pre_biofix':
					smry_dict['basetemp'] = 50					#always 50 for phenology
					dd_type = 'dd%dbe' % smry_dict['basetemp']
					# add daily forecast data
					start_fcst_dt = DateTime.DateTime(*daily_data[-1][0]) + DateTime.RelativeDate(days = +1)
					end_fcst_dt = end_date_dt + DateTime.RelativeDate(days = +5)
					daily_data = self.add_dly_fcst(stn,daily_data,start_fcst_dt,end_fcst_dt)
					ret_bf_date, ddaccum, ddmiss = self.accum_degday(daily_data, start_date_dt, end_date_dt, dd_type, biofix_dd, stn, station_name)
					if ret_bf_date and not bf_date:
						bf_miss = ddmiss
						bf_date = ret_bf_date
						biofix_status = 'post_biofix'
					else:
						# add daily forecast data
						degday_dict = self.degday_calcs(daily_data, start_date_dt, end_fcst_dt, dd_type, "accum")

				# calculate degree days for period after biofix, might be different base
				if biofix_status == 'post_biofix':
					smry_dict['basetemp'] = pest_status_management['basetemp']
					dd_type = 'dd4714hi' # hourly integrated degree days (base 47.14)
					start_date_dt = bf_date
					hourly_data, download_time, station_name, avail_vars = self.get_hourly2 (stn, start_date_dt, end_date_dt)
					if len(hourly_data) > 0:
						biofix2_dd = 1620			#we want to know if this amount occurred before August 5
						ret_bf2_date, bogus_accum, bogus_miss = self.accum_degday(hourly_data, start_date_dt, end_date_dt, dd_type, biofix2_dd, stn, station_name)
						biofix2_dd = 99999			#we also want to know current accum
						bogus_date, ddaccum, ddmiss = self.accum_degday(hourly_data, start_date_dt, end_date_dt, dd_type, biofix2_dd, stn, station_name)
					else:
						return self.nodata(stn, station_name, start_date_dt, end_date_dt)

					# add hourly forecast data
					start_fcst_dt = DateTime.DateTime(*download_time) + DateTime.RelativeDate(hours = +1)
					end_fcst_dt = end_date_dt + DateTime.RelativeDate(days = +6)
					hourly_data = self.add_hrly_fcst(stn,hourly_data,start_fcst_dt,end_fcst_dt)
					degday_dict = self.hidd_calcs(hourly_data, start_date_dt, end_fcst_dt, dd_type)
				else:
					ret_bf2_date = False

				# get status and recommendation
				if ret_bf2_date and ret_bf2_date <= DateTime.DateTime(ret_bf2_date.year,8,5,1):
					smry_dict['stage']  = "Continuous pressure through harvest"
					smry_dict['status'] = "If 1620 DD occurs prior to August 5, you can expect continuous pressure from grape berry moth through harvest. Model results are not good predictors of timing of population pressures."
					smry_dict['manage'] = "Multiple additional insecticide applications may be necessary in high pressure vineyards to address the extended egg-laying and overlapping generations.  Continuous coverage is necessary to avoid excessive crop loss.  NOTE:  Insecticide applications after mid September will have limited effectiveness in preventing damage."
				else:
					for k in pest_status_management[biofix_status].keys():
						psmk = pest_status_management[biofix_status][k]
						if psmk.has_key('ddlo'):
							if ddaccum >= int(psmk['ddlo']) and ddaccum <= int(psmk['ddhi']):
								smry_dict['stage']  = psmk['stage']
								smry_dict['status'] = psmk['status']
								smry_dict['manage'] = psmk['management']
								break
						else:
							return newaCommon_io.errmsg('Error determining recommendations')
					else:
						smry_dict['stage']  = "Not defined"
						smry_dict['status'] = "Not defined"
						smry_dict['manage'] = "Not defined"
	
				# get dates for gdd table
				smry_dict = self.setup_dates(smry_dict,end_date_dt)
				# get dd for days of interest (including forecast)
				smry_dict = self.add_ddays(smry_dict,degday_dict,start_date_dt,end_date_dt)

				# get other information needed for display
				if bf_date:
					smry_dict['bf_date'] = [bf_date.year,bf_date.month,bf_date.day]
				else:
					smry_dict['bf_date'] = None

				if smry_dict['bf_date'] and biofix_status == 'pre_biofix':
					smry_dict['ddaccum'] = miss
					smry_dict['ddmiss']  = miss
				else:
					smry_dict['ddaccum'] = int(ddaccum)
					smry_dict['ddmiss']  = ddmiss
				smry_dict['bf_miss'] = bf_miss

				# send results for display
				return newaModel_io.berry_moth_results(smry_dict)
			else:
				return self.nodata(stn, station_name, start_date_dt, end_date_dt)
		except:
			print_exception()						
			return newaCommon_io.errmsg('An error occurred attempting to process this request. Check inputs.')

	#--------------------------------------------------------------------------------------------		
	#	obtain everything necessary for grape disease summary
	def run_grape_dis(self,stn,end_date_dt,output):
		from phomopsis_info_dict import pest_status_management as phomopsis_status_management
		from blackrot_info_dict import pest_status_management as blackrot_status_management
		from pmildew_info_dict import pest_status_management as pmildew_status_management
		from grape_phen_events import phen_events_dict

		phen_stages = [('dormant','Dormant'), ('harvest','Harvest'), ('veraison','Veraison'), ('bunch_closure','Bunch closure'), 
        		       ('2nd_postbloom','2nd postbloom'), ('1st_postbloom','1st postbloom'), ('bloom','Bloom'),
     		           ('imm_prebloom','Immediate pre-bloom'),('10in_shoot','10 inch shoot'),('3in_shoot','3-5 inch shoot'),
            		   ('1in_shoot','1 inch shoot'),('bud_swell','Bud swell'),('early','Preseason')]  #ordered latest to earliest

		try:
			now = DateTime.now()
			smry_dict = {}
			pmildew_list = []
			smry_dict['output'] = output
			smry_dict['stn'] = stn
			if not end_date_dt: end_date_dt = now
			start_date_dt = DateTime.DateTime(end_date_dt.year,3,25,1)
			smry_dict['accend'] = end_date_dt
			
			if end_date_dt < start_date_dt:
				return newaModel_io.grape_dis_dormant(smry_dict)
			
			#get dates for summary table
			smry_dict = self.setup_dates (smry_dict,end_date_dt)

			#get phenological stage based on date
			for stage,stage_name in phen_stages:
				pdate = phen_events_dict[stage]
				pdate_dt = DateTime.DateTime(end_date_dt.year,pdate[0],pdate[1],pdate[2])
				if end_date_dt >= pdate_dt:
					phenology = stage
					break
			else:
				phenology = 'dormant'
			smry_dict['phenology'] = phenology
			smry_dict['phen_stages'] = phen_stages
	
			#get management message based on phenology
			for stat in phomopsis_status_management['messages'].keys():
				if phenology in phomopsis_status_management['messages'][stat]['stages']:
					smry_dict['phomopsis_manage'] = phomopsis_status_management['messages'][stat]['management']
					break
			else:
				smry_dict['phomopsis_manage'] = None		
			for stat in blackrot_status_management['messages'].keys():
				if phenology in blackrot_status_management['messages'][stat]['stages']:
					smry_dict['blackrot_manage'] = blackrot_status_management['messages'][stat]['management']
					break
			else:
				smry_dict['blackrot_manage'] = None
			for stat in pmildew_status_management['messages'].keys():
				if phenology in pmildew_status_management['messages'][stat]['stages']:
					smry_dict['pmildew_manage'] = pmildew_status_management['messages'][stat]['management']
					break
			else:
				smry_dict['pmildew_manage'] = None
				
			# just use observed data (no forecast) in years other than the current
			if end_date_dt.year != now.year:
				smry_dict['this_year'] = False
				end_date_dt = end_date_dt + DateTime.RelativeDate(days = +6)
			else:
				smry_dict['this_year'] = True

			# obtain hourly and daily data
			hourly_data, daily_data, download_time, station_name, avail_vars = self.get_hddata2 (stn, start_date_dt, end_date_dt)
			smry_dict['station_name'] = station_name
			smry_dict['last_time'] = download_time
			
			# build observed wet_periods and infection_list based only on observed data
			if len(hourly_data) > 0:
				# pick out wet periods and combine them into combined events
				indiv_list = self.get_wet_periods(hourly_data)
				combined_list = self.combine_wet_periods(indiv_list)
				
				# calc phomopsis and black rot for each wet period
				wet_periods = []
				for wet_start,wet_end,wet_hrs,avg_temp,prec_sum,rain_start,rain_length,rain_temp in indiv_list:
					ph_infect = self.get_phomop(wet_hrs,avg_temp,prec_sum)
					br_infect = self.get_blackrot(wet_hrs,avg_temp,prec_sum)
					wet_periods.append((wet_start,wet_end,wet_hrs,avg_temp,prec_sum,ph_infect,br_infect))
				smry_dict['wet_periods'] = wet_periods

				# determine which combined events are infection events
				infect_list = []
				for wet_start,wet_end,wet_hrs,avg_temp,prec_sum,combined in combined_list:
					ph_infect = self.get_phomop(wet_hrs,avg_temp,prec_sum)
					br_infect = self.get_blackrot(wet_hrs,avg_temp,prec_sum)
					if ph_infect == 'Infection' or br_infect == 'Infection':
						infect_list.append((wet_start,wet_end,wet_hrs,avg_temp,prec_sum,combined,ph_infect,br_infect))
				smry_dict['infect_list'] = infect_list
			else:
				return self.nodata(stn, station_name, start_date_dt, end_date_dt)

			# now add in the forecast data
			if smry_dict['this_year']:
				start_fcst_dt = DateTime.DateTime(*download_time) + DateTime.RelativeDate(hours = +1)
				end_fcst_dt = end_date_dt + DateTime.RelativeDate(days = +6)
				hourly_data = self.add_hrly_fcst(stn,hourly_data,start_fcst_dt, end_fcst_dt,False)
				daily_data = self.hrly_to_dly(hourly_data)
			else:
				start_fcst_dt = end_date_dt + DateTime.RelativeDate(hours = +1)
				end_fcst_dt = end_date_dt
				end_date_dt = end_date_dt + DateTime.RelativeDate(days = -6)

			# check for powdery mildew infections
			if len(daily_data) > 0:
				# add daily forecast data
				#start_fcst_dt = DateTime.DateTime(*daily_data[-1][0]) + DateTime.RelativeDate(days = +1)
				#end_fcst_dt = end_date_dt + DateTime.RelativeDate(days = +5)
				#daily_data = self.add_dly_fcst(stn,daily_data,start_fcst_dt,end_fcst_dt)
				for dt,tave,tmax,tmin,prcp,pop12,rhum,miss,miss,qpf,miss,miss,dflags in daily_data:
					pm = self.get_pmildew(prcp,(tmax+tmin)/2.)
					pmildew_list.append((dt,pm))
			else:
				return self.nodata(stn, station_name, start_date_dt, end_date_dt)
			
			# now do calculations with hourly forecast data included		
			if len(hourly_data) > 0:
				# pick out wet periods and combine them into combined events
				indiv_list = self.get_wet_periods(hourly_data)
				combined_list = self.combine_wet_periods(indiv_list)
				
				# determine which combined events are infection events
				infect_list = []
				for wet_start,wet_end,wet_hrs,avg_temp,prec_sum,combined in combined_list:
					ph_infect = self.get_phomop(wet_hrs,avg_temp,prec_sum)
					br_infect = self.get_blackrot(wet_hrs,avg_temp,prec_sum)
					if ph_infect == 'Infection' or br_infect == 'Infection':
						infect_list.append((wet_start,wet_end,wet_hrs,avg_temp,prec_sum,combined,ph_infect,br_infect))
			else:
				return self.nodata(stn, station_name, start_date_dt, end_date_dt)

			# build dictionary for infection event table
			last_prcp_dt = start_date_dt + DateTime.RelativeDate(hours = -1)
			for i in range(len(hourly_data), 0, -1):
				theTime,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags = hourly_data[i-1]
				temp_eflag, prcp_eflag, pop12_eflag, rhum_eflag, wspd_eflag, wdir_eflag, srad_eflag, st4i_eflag = eflags
				if prcp != miss and prcp_eflag != "P":
					last_prcp_dt = DateTime.DateTime(*theTime)
					break
			smry_dict = self.add_infection_events(smry_dict,pmildew_list,infect_list,start_date_dt,end_date_dt,hourly_data[-1][0],last_prcp_dt)

			# send results for display
			return newaModel_io.grape_disease_results(smry_dict)
		except:
			print_exception()						
			return newaCommon_io.errmsg('An error occurred attempting to process this request. Check inputs.')
			
	#--------------------------------------------------------------------------------------------		
	#	obtain everything necessary for grape status update
	def run_grape_update (self,altref,output):
		from phomopsis_info_dict import pest_status_management as phomopsis_status_management
		from blackrot_info_dict import pest_status_management as blackrot_status_management
		from pmildew_info_dict import pest_status_management as pmildew_status_management

		phen_stages = [('dormant','Dormant'), ('harvest','Harvest'), ('veraison','Veraison'), ('bunch_closure','Bunch closure'), 
        		       ('2nd_postbloom','2nd postbloom'), ('1st_postbloom','1st postbloom'), ('bloom','Bloom'),
     		           ('imm_prebloom','Immediate pre-bloom'),('10in_shoot','10 inch shoot'),('3in_shoot','3-5 inch shoot'),
            		   ('1in_shoot','1 inch shoot'),('bud_swell','Bud swell'),('early','Preseason')]  #ordered latest to earliest

		try:
			smry_dict = {}
			smry_dict['phenology'] = altref
			smry_dict['phen_stages'] = phen_stages
		
			for stat in phomopsis_status_management['messages'].keys():
				if altref in phomopsis_status_management['messages'][stat]['stages']:
					smry_dict['phomopsis_manage'] = phomopsis_status_management['messages'][stat]['management']
					break
			else:
				smry_dict['phomopsis_manage'] = None		
			for stat in blackrot_status_management['messages'].keys():
				if altref in blackrot_status_management['messages'][stat]['stages']:
					smry_dict['blackrot_manage'] = blackrot_status_management['messages'][stat]['management']
					break
			else:
				smry_dict['blackrot_manage'] = None
			for stat in pmildew_status_management['messages'].keys():
				if altref in pmildew_status_management['messages'][stat]['stages']:
					smry_dict['pmildew_manage'] = pmildew_status_management['messages'][stat]['management']
					break
			else:
				smry_dict['pmildew_manage'] = None

			return newaModel_io.grape_status_results(smry_dict)
		except:
			print_exception()
			return newaCommon_io.errmsg('An error occurred attempting to process this request. Check inputs.')

##### DIRECTORS #####
#--------------------------------------------------------------------------------------------					
def updateStatus (request,path):
	try:
		pest = None
		altref = None
		output = 'tab'
#	 	retrieve input
		if path is None:
			if request and request.form:
				try:
					if request.form.has_key('pest'): pest = request.form['pest']
					if request.form.has_key('altref'): altref = request.form['altref']
					if request.form.has_key('output'): output = request.form['output']
				except:
					print_exception()
					raise program_exit('Error processing request')
			else:
				return newaCommon_io.errmsg('Error processing form; check input')
		else:
			return newaCommon_io.errmsg('Error processing input')
			
# 		send input to appropriate routine
		if pest and altref:
			return Apple().run_pest_update(pest,altref,output)
		else:
			return newaCommon_io.errmsg('Error processing input')
	except program_exit,msg:
		print msg
		return newaCommon_io.errmsg('Error processing input')
	except:
		print_exception()
		return newaCommon_io.errmsg('Unexpected error')

#--------------------------------------------------------------------------------------------					
def update_grape_status (request,path):
	try:
		altref = None
		output = 'tab'
#	 	retrieve input
		if path is None:
			if request and request.form:
				try:
					if request.form.has_key('altref'): altref = request.form['altref']
					if request.form.has_key('output'): output = request.form['output']
				except:
					print_exception()
					raise program_exit('Error processing request')
			else:
				return newaCommon_io.errmsg('Error processing form; check input')
		else:
			return newaCommon_io.errmsg('Error processing input')
			
# 		send input to appropriate routine
		if altref:
			return Grape().run_grape_update(altref,output)
		else:
			return newaCommon_io.errmsg('Error processing input')
	except program_exit,msg:
		print msg
		return newaCommon_io.errmsg('Error processing input')
	except:
		print_exception()
		return newaCommon_io.errmsg('Unexpected error')

#--------------------------------------------------------------------------------------------					
def process_help (request,path):
	try:
		smry_type = None
		pest = None
#	 	retrieve input
		if path is None:
			if request and request.form:
				try:
					smry_type = request.form['type'].strip()
					if request.form.has_key('pest'): pest = request.form['pest']
				except:
					print_exception()
					raise program_exit('Error processing request')
			else:
				return newaCommon_io.errmsg('Error processing form; check input')
		elif path[0] in ['apple_scab','apple_scab2','fire_blight','sooty_blotch','berry_moth','dmcast','grape_dis']:
			try:
				smry_type = path[0]
			except IndexError:
				raise program_exit('Error processing request - index error')
			except:
				print_exception()
				raise program_exit('Error processing request')
		elif path[0] in ['apple_pest','apple_disease','grape_disease']:
			try:
				smry_type = path[0]
				pest = path[1]
			except IndexError:
				raise program_exit('Error processing request - index error')
			except:
				print_exception()
				raise program_exit('Error processing request')
		else:
			return newaCommon_io.errmsg('Error processing input')
			
# 		send input to appropriate routine
		if smry_type == 'apple_scab2':
			return newaModel_io.helppage(None)
		elif smry_type == 'apple_scab_estlw':
			return newaModel_io.helppage(None)
		elif smry_type == 'apple_scab' or (smry_type == 'apple_disease' and pest == 'apple_scab'):
			return newaModel_io.helppage([("Pest Management Guidelines for Commercial Tree Fruit Production","http://ipmguidelines.org"),
										   ("Apple Scab Fact Sheet","http://nysipm.cornell.edu/factsheets/treefruit/diseases/as/as.asp"),
			                               ("Cornell Fruit Resources - Tree Fruit IPM","https://blogs.cornell.edu/treefruit/ipm/"),
			                               ("NEWA Default Biofix Dates","http://newa.cornell.edu/index.php?page=default-biofix-dates"),
			                               ("Season-long Leaf Wetness Events","http://newa.cornell.edu/index.php?page=apple-lw"),
			                               ("NEWA Model References","http://newa.cornell.edu/index.php?page=newa-pest-forecast-model-references")
										   ])
		elif smry_type == 'fire_blight' or (smry_type == 'apple_disease' and pest == 'fire_blight'):
			return newaModel_io.helppage([ ("Notes on first blossom open biofix","/appfbnotes_pop.htm"),
										   ("Highly susceptible apple varieties and rootstocks","http://newa.cornell.edu/index.php?page=fire-blight-susceptible-cultivars-and-rootstocks"),
										   ("Pest Management Guidelines for Commercial Tree Fruit Production","http://ipmguidelines.org"),
										   ("Fire Blight Fact Sheet (pdf)","https://ecommons.cornell.edu/handle/1813/43095"),
			                               ("NEWA Default Biofix Dates","http://newa.cornell.edu/index.php?page=default-biofix-dates"),
			                               ("To download Maryblyt v 7.1 (Windows only), email Alan Biggs, Professor Emeritus of Plant Pathology at West Virginia University, who developed the first functional Windows version of this fire blight prediction software.","mailto:Alan.Biggs@mail.wvu.edu"),
			                               ("NEWA Model References","http://newa.cornell.edu/index.php?page=newa-pest-forecast-model-references")
										])
		elif smry_type == 'sooty_blotch' or (smry_type == 'apple_disease' and pest == 'sooty_blotch'):
			return newaModel_io.helppage([
#											("Notes on petal fall biofix - not available",""),
										   ("Pest Management Guidelines for Commercial Tree Fruit Production","http://ipmguidelines.org"),
										   ("Sooty Blotch/Flyspeck Fact Sheet (html)","http://hdl.handle.net/1813/43129"),
										   ("Sooty Blotch/Flyspeck Fact Sheet (pdf)","https://ecommons.cornell.edu/bitstream/handle/1813/43129/sooty-blotch-flyspeck-FS-NYSIPM.pdf?sequence=1&isAllowed=y"),
#										   ("More information about Sooty Blotch/Flyspeck - not available",""),
										   ("Cornell Fruit Resources - Tree Fruit IPM","https://blogs.cornell.edu/treefruit/ipm/"),
			                               ("NEWA Default Biofix Dates","http://newa.cornell.edu/index.php?page=default-biofix-dates"),
			                               ("NEWA Model References","http://newa.cornell.edu/index.php?page=newa-pest-forecast-model-references")
											])
		elif smry_type == 'shoot_blight':
			return newaModel_io.helppage(None)
		elif smry_type == 'apple_pest':		
			pest_names = {"stlm": "Spotted Tentiform Leafminer", "ofm":"Oriental Fruit Moth", "cm":"Codling Moth",
						  "pc":"Plum Curculio", "oblr":"Obliquebanded Leafroller", "sjs":"San Jose Scale", "am":"Apple Maggot"}
			pest_id = {"stlm": 43130, "ofm":43112, "cm":43086, "sjs":43128, "pc":43118, "oblr":43111, "am":43071}
			pest_abb = pest[pest.find('-')+1:]
			if pest_abb == 'maggot': pest_abb = 'am'
			help_list = [("Pest Management Guidelines","http://ipmguidelines.org"),
			             ("%s Fact Sheet"%(pest_names[pest_abb]),"http://hdl.handle.net/1813/%s"%(pest_id[pest_abb])),
			             ("Cornell Fruit Resources - Tree Fruit IPM","https://blogs.cornell.edu/treefruit/ipm/"),
						 ("Pesticide Information","https://cropandpestguides.cce.cornell.edu/"),
			             ("NEWA Default Biofix Dates","http://newa.cornell.edu/index.php?page=default-biofix-dates"),
			             ("Degree Day Accumulations Table","http://newa.cornell.edu/index.php?page=degree-days"),
			             ("Hudson Valley Scouting Reports and Trap Data","http://www.hudsonvalleyresearchlab.org/"),
			             ("NEWA Model References","http://newa.cornell.edu/index.php?page=newa-pest-forecast-model-references")
						 ]
			return newaModel_io.helppage(help_list)
		elif smry_type == 'berry_moth' or (smry_type == 'grape_disease' and pest == 'berry_moth'):
			return newaModel_io.helppage([("Risk Assessment of Grape Berry Moth and Guidelines for Management of the Eastern Grape Leafhopper (pdf)","http://hdl.handle.net/1813/5202"),
										   ("Grape Berry Moth IPM fact sheet","http://hdl.handle.net/1813/43096"),
										   ("Grape Berry Moth IPM fact sheet (pdf)","https://ecommons.cornell.edu/bitstream/handle/1813/43096/grape-berry-moth-FS-NYSIPM.pdf?sequence=1&isAllowed=y"),
										   ("New York and Pennsylvania Pest Management Guidelines for Grapes","http://ipmguidelines.org"),
										   ("Production Guide for Organic Grapes (pdf)","https://ecommons.cornell.edu/bitstream/handle/1813/42888/2016-org-grapes-NYSIPM.pdf?sequence=5&isAllowed=y"),
										   ("Elements of IPM for Grapes in New York State","http://hdl.handle.net/1813/42720"),
			                               ("NEWA Model References","http://newa.cornell.edu/index.php?page=newa-pest-forecast-model-references")
										   ])
		elif smry_type == 'grape_dis' or (smry_type == 'grape_disease' and pest == 'grape_dis'):
			return newaModel_io.helppage([("New York and Pennsylvania Pest Management Guidelines for Grapes","http://ipmguidelines.org"),
										   ("Black Rot IPM Fact Sheet","http://hdl.handle.net/1813/43076"),
										   ("Phomopsis Cane and Leaf Spot IPM Fact Sheet","http://hdl.handle.net/1813/43104"),
										   ("Grapevine Powdery Mildew IPM Fact Sheet","http://hdl.handle.net/1813/43121"),
										   ("Cornell Fruit Resources - Grapes","https://blogs.cornell.edu/grapes/ipm/"),
			                               ("NEWA Model References","http://newa.cornell.edu/index.php?page=newa-pest-forecast-model-references")
										   ])
		elif smry_type == 'dmcast' or (smry_type == 'grape_disease' and pest == 'dmcast'):
			return newaModel_io.helppage([("DMCast Notes","/dmcast/dmcast_notes.html"),
			                               ("NEWA Model References","http://newa.cornell.edu/index.php?page=newa-pest-forecast-model-references")
			                               ])
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
		stn = None
		year = None
		month = None
		day = None
		greentip = None
		firstblossom = None
		orchard_history = None
		strep_spray = None
		petalfall = None
		fungicide = None
		harvest = None
		infection_event = None
		symptoms = None
		selbutton = None
		accend = None
		pest = None
		bf_date = None
		bf2_date = None
		bf3_date = None
		altref = None
		cultivar = None
		output = "tab"
		estimate = "no"
#	 	retrieve input
#		print 'path:',path

		if path is None:
			newForm = {}
			for k,v in request.form.items() :
				newForm[str(k)] = str(v)
			request.form = newForm
			if request and request.form:
#				print 'form',request.form
				try:
					smry_type = request.form['type'].strip()
					if request.form.has_key('stn'):             stn = request.form['stn'].strip()
					if request.form.has_key('month'):           month = int(request.form['month'])
					if request.form.has_key('year'):            year = int(request.form['year'])
					if request.form.has_key('day'):             day = int(request.form['day'])
					if request.form.has_key('pest'):            pest = request.form['pest']
					if request.form.has_key('orchard_history'): orchard_history = int(request.form['orchard_history'])
					if request.form.has_key('selbutton'):       selbutton = request.form['selbutton']
					if request.form.has_key('output'):          output = request.form['output']
					if request.form.has_key('altref'):          altref = request.form['altref']
					if request.form.has_key('cultivar'):		cultivar = request.form['cultivar']
					if request.form.has_key('estimate'):		estimate = request.form['estimate']
					if request.form.has_key('greentip'):
						try:
							mm,dd,yy = request.form['greentip'].split("/")
							greentip = DateTime.DateTime(int(yy),int(mm),int(dd),23)
						except:
							greentip = None
					if request.form.has_key('firstblossom'):
						try:
							mm,dd,yy = request.form['firstblossom'].split("/")
							firstblossom = DateTime.DateTime(int(yy),int(mm),int(dd),23)
						except:
							firstblossom = None
					if request.form.has_key('petalfall'):
						try:
							mm,dd,yy = request.form['petalfall'].split("/")
							petalfall = DateTime.DateTime(int(yy),int(mm),int(dd),23)
						except:
							petalfall = None
					if request.form.has_key('fungicide'):
						try:
							mm,dd,yy = request.form['fungicide'].split("/")
							fungicide = DateTime.DateTime(int(yy),int(mm),int(dd),23)
						except:
							fungicide = None
					if request.form.has_key('harvest'):
						try:
							mm,dd,yy = request.form['harvest'].split("/")
							harvest = DateTime.DateTime(int(yy),int(mm),int(dd),23)
						except:
							harvest = None
					if request.form.has_key('strep_spray'):
						try:
							mm,dd,yy = request.form['strep_spray'].split("/")
							strep_spray = DateTime.DateTime(int(yy),int(mm),int(dd),23)
						except:
							strep_spray = None
					if request.form.has_key('infection_event'):
						try:
							mm,dd,yy = request.form['infection_event'].split("/")
							infection_event = DateTime.DateTime(int(yy),int(mm),int(dd),23)
						except:
							infection_event = None
					if request.form.has_key('symptoms'):
						try:
							mm,dd,yy = request.form['symptoms'].split("/")
							symptoms = DateTime.DateTime(int(yy),int(mm),int(dd),23)
						except:
							symptoms = None
					if request.form.has_key('accend'):
						try:
							mm,dd,yy = request.form['accend'].split("/")
							accend = DateTime.DateTime(int(yy),int(mm),int(dd),23)
						except:
							accend = None
					if request.form.has_key('bf_date'):
						try:
							mm,dd,yy = request.form['bf_date'].split("/")
							bf_date = DateTime.DateTime(int(yy),int(mm),int(dd),0)
						except:
							bf_date = None
					if request.form.has_key('bf2_date'):
						try:
							mm,dd,yy = request.form['bf2_date'].split("/")
							bf2_date = DateTime.DateTime(int(yy),int(mm),int(dd),0)
						except:
							bf2_date = None
					if request.form.has_key('bf3_date'):
						try:
							mm,dd,yy = request.form['bf3_date'].split("/")
							bf3_date = DateTime.DateTime(int(yy),int(mm),int(dd),0)
						except:
							bf3_date = None
				except:
					print_exception()
					raise program_exit('Error processing request')
			else:
				return newaCommon_io.errmsg('Error processing form; check input')
		elif path[0] in ['apple_scab','apple_scab2','fire_blight','sooty_blotch','berry_moth','dmcast','grape_dis']:
#			print 'path:',path
			try:
				smry_type = path[0]
				if len(path) > 1: stn = path[1]
				output = "standalone"
			except IndexError:
				raise program_exit('Error processing request - index error')
			except:
				print_exception()
				raise program_exit('Error processing request')
		elif path[0] in ['apple_scab_estlw']:
#			print 'path:',path
			try:
				smry_type = path[0]
				estimate = "yes"
				if len(path) > 1: stn = path[1]
				output = "standalone"
			except IndexError:
				raise program_exit('Error processing request - index error')
			except:
				print_exception()
				raise program_exit('Error processing request')
		elif path[0] in ['apple_pest','apple_disease','grape_disease']:
#			print 'path:',path
			try:
				smry_type = path[0]
				pest = path[1]
				stn = path[2]
				output = "standalone"
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

# 		send input to appropriate routine
		if stn:
			if smry_type == 'apple_scab2':
				return Apple().run_apple_scab_old(stn)
			elif smry_type == 'apple_scab':
				return Apple().run_apple_scab(stn,accend,greentip,output,estimate)
			elif smry_type == 'apple_scab_estlw':
				return Apple().run_apple_scab(stn,accend,greentip,output,"yes")
			elif smry_type == 'fire_blight':
				return Apple().run_fire_blight(stn,accend,firstblossom,strep_spray,orchard_history,selbutton,output)
			elif smry_type == 'sooty_blotch':
				return Apple().run_sooty_blotch(stn,accend,petalfall,fungicide,harvest,selbutton,output)
			elif smry_type == 'shoot_blight':
				return Apple().run_shoot_blight(stn,accend,infection_event,symptoms,selbutton,output)
			elif smry_type == 'apple_disease':
				if pest == 'fire_blight':
					return Apple().run_fire_blight(stn,accend,firstblossom,strep_spray,orchard_history,selbutton,output)
				elif pest == 'apple_scab':
					return Apple().run_apple_scab(stn,accend,greentip,output,estimate)
				elif pest == 'sooty_blotch':
					return Apple().run_sooty_blotch(stn,accend,petalfall,fungicide,harvest,selbutton,output)
				else:
					return newaCommon_io.errmsg('Error processing form; check input')
			elif smry_type == 'berry_moth':
				return Grape().run_berry_moth(stn,accend,bf_date,output)
			elif smry_type == 'grape_dis':
				return Grape().run_grape_dis(stn,accend,output)
			elif smry_type == 'dmcast':
				return Grape().run_dmcast(stn,accend,cultivar,output)
			elif smry_type == 'grape_disease':
				if pest == "berry_moth":
					return Grape().run_berry_moth(stn,accend,bf_date,output)
				elif pest == "dmcast":
					return Grape().run_dmcast(stn,accend,cultivar,output)
				elif pest == 'grape_dis':
					return Grape().run_grape_dis(stn,accend,output)
				else:
					return newaCommon_io.errmsg('Error processing form; check input')
			elif smry_type == 'apple_pest':
				return Apple().run_apple_pest(stn,pest,accend,bf_date,bf2_date,bf3_date,output)
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

