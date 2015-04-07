#!/usr/local/bin/python

import sys, os, math
from mx import DateTime
from print_exception import print_exception
import newaGraph_io
if '/Users/keith/kleWeb/newaCommon' not in sys.path: sys.path.insert(1,'/Users/keith/kleWeb/newaCommon')
import newaCommon_io, newaCommon
if '/Users/keith/kleWeb/newaModel/newaModel' not in sys.path: sys.path.insert(1,'/Users/keith/kleWeb/newaModel/newaModel')
import newaModel
from phen_events import phen_events_dict		
if '/Users/keith/NDFD' not in sys.path: sys.path.insert(1,'/Users/keith/NDFD')
from get_daily_forecast import get_daily_forecast

miss = -999

class program_exit (Exception):
	pass

#--------------------------------------------------------------------------------------------		
# gather data for daily (obs and forecast) temp and ppt plots
def tp_for_grf(stn, daily_data, smry_dict, start_date_dt, end_date_dt):
	obs_dict = {}
	forecast_data = None
	try:
		mint = []
		maxt = []
		prcpl = []
		obs_days = []
		first = 1
		for dly_dt,tave_hr,tmax,tmin,prcp,lwet,rhum,wspd,srad,st4a,st4x,st4n,dflags in daily_data:
			this_day_dt = DateTime.DateTime(dly_dt[0],dly_dt[1],dly_dt[2])
			if this_day_dt < start_date_dt: continue
			if tmax != miss and tmin != miss:
				if first:
					first = 0
				mint.append(int(round(tmin,0)))
				maxt.append(int(round(tmax,0)))
				prcpl.append(prcp)
				obs_days.append("%d-%d-%d" % (dly_dt[0],dly_dt[1],dly_dt[2]))
		obs_dict['maxt'] = maxt
		obs_dict['mint'] = mint
		obs_dict['prcp'] = prcpl
		obs_dict['obs_days'] = obs_days

		# get daily forecast data
		fmint = []
		fmaxt = []
		fprcp = []
		fobs_days = []
		start_fcst_dt = DateTime.DateTime(*daily_data[-1][0]) + DateTime.RelativeDate(days = +1)
		end_fcst_dt = end_date_dt + DateTime.RelativeDate(days = +6)
		forecast_data = get_daily_forecast(stn,start_fcst_dt,end_fcst_dt)
		for dly_dt,tave_hr,tmax,tmin,prcp,lwet,rhum,wspd,srad,st4a,st4x,st4n,dflags in forecast_data:
			if tmax != miss and tmin != miss:
				if first:
					first = 0
				fmint.append(int(round(tmin,0)))
				fmaxt.append(int(round(tmax,0)))
				fprcp.append(prcp)
				fobs_days.append("%d-%d-%d" % (dly_dt[0],dly_dt[1],dly_dt[2]))
		obs_dict['fmaxt'] = fmaxt
		obs_dict['fmint'] = fmint
		obs_dict['fprcp'] = fprcp
		obs_dict['frobs_days'] = fobs_days
	except:
		print_exception()
	return obs_dict, smry_dict, forecast_data


#--------------------------------------------------------------------------------------------		
# gather data for daily (obs and forecast) temp and ppt plots
# this version already has forecast data merged
def tp_for_grf2(daily_data, start_date_dt, start_fcst_dt):
	obs_dict = {}
	forecast_data = None
	start_fcst_dt = start_fcst_dt + DateTime.RelativeDate(hour=0,minute=0,second=0)
	try:
		mint = []
		maxt = []
		prcpl = []
		obs_days = []
		fmint = []
		fmaxt = []
		fprcp = []
		fobs_days = []
		for dly_dt,tave_hr,tmax,tmin,prcp,lwet,rhum,wspd,srad,qpf,st4x,st4n,dflags in daily_data:
			this_day_dt = DateTime.DateTime(dly_dt[0],dly_dt[1],dly_dt[2])
			if this_day_dt < start_date_dt: continue
			if tmax != miss and tmin != miss:
				if this_day_dt < start_fcst_dt:
					mint.append(int(round(tmin,0)))
					maxt.append(int(round(tmax,0)))
					prcpl.append(qpf)
					obs_days.append("%d-%d-%d" % (dly_dt[0],dly_dt[1],dly_dt[2]))
				else:
					fmint.append(int(round(tmin,0)))
					fmaxt.append(int(round(tmax,0)))
					fprcp.append(qpf)
					fobs_days.append("%d-%d-%d" % (dly_dt[0],dly_dt[1],dly_dt[2]))

		obs_dict['maxt'] = maxt
		obs_dict['mint'] = mint
		obs_dict['prcp'] = prcpl
		obs_dict['obs_days'] = obs_days
		obs_dict['fmaxt'] = fmaxt
		obs_dict['fmint'] = fmint
		obs_dict['fprcp'] = fprcp
		obs_dict['frobs_days'] = fobs_days
	except:
		print_exception()
	return obs_dict

#--------------------------------------------------------------------------------------------		
# get Fire Blight 4-day degree hour accumulations
def deghr_for_grf (hourly_data,start_date,end_date):
	deghr_dict = {}
	try:
		dly_sum = 0.
		dly_msg = 0.
		d4_dh = []
		dly_d4dh_list = []
		date_list = []
		start_date = start_date + DateTime.RelativeDate(days=+1)		#start deghr accumulation day after biofix
		start_date = start_date + DateTime.RelativeDate(hour=0,minute=0,second=0)
		end_date = end_date + DateTime.RelativeDate(hour=23,minute=59,second=59)
		for theTime,temp,prcp,lwet,rhum,wspd,wdir,srad,st4i,eflags in hourly_data:
			temp_eflag, prcp_eflag, lwet_eflag, rhum_eflag, wspd_eflag, wdir_eflag, srad_eflag, st4i_eflag = eflags
			this_date = DateTime.DateTime(*theTime)
			if this_date >= start_date and this_date <= end_date:
				if temp != miss:
					ddval = newaModel.Apple().get_dhr(temp)
					dly_sum = dly_sum + ddval
				else:
					dly_msg = dly_msg+1
					
	#			save daily values
				if theTime[3] == 23:
					if dly_msg >= 2: dly_sum = miss
					if len(d4_dh) == 4: del d4_dh[0]		#keep total for last 4 days
					d4_dh.append(dly_sum)
					if d4_dh.count(miss) == 0 and len(d4_dh) > 0:
						fdate = "%d-%d-%d" % (theTime[0],theTime[1],theTime[2])
						date_list.append(fdate)
						dly_d4dh_list.append(int(sum(d4_dh)))
					dly_sum = 0.
					dly_msg = 0
	#	get last partial day
		if theTime[3] != 23:
			if dly_msg >= 2: dly_sum = miss
			if len(d4_dh) == 4: del d4_dh[0]		#keep total for last 4 days
			d4_dh.append(dly_sum)
			if d4_dh.count(miss) == 0 and len(d4_dh) > 0:
				fdate = "%d-%d-%d" % (theTime[0],theTime[1],theTime[2])
				date_list.append(fdate)
				dly_d4dh_list.append(int(sum(d4_dh)))
		deghr_dict['dates'] = date_list
		deghr_dict['d4dh'] = dly_d4dh_list
	except:
		print 'Error calculating degree hours'
		print_exception()
	return deghr_dict

#--------------------------------------------------------------------------------------------		
# get Apple Scab ascospore maturity (percent)
def ascospore_for_grf (dd_data,daily_data):
	ascospore_dict = {}
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
		date_list = []
		matur_list = []
		error_list = []
		for dly_dt,tmax,tmin,ddval,prec in dd_data:
			fdate = "%d-%d-%d" % (dly_dt[0],dly_dt[1],dly_dt[2])
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
				comp = math.exp((math.pi/math.sqrt(3))*((-2.49+(0.01*accum_dd))))
				maturity = 100.*(comp)/(1.+comp)
				comp2 = math.exp((math.pi/math.sqrt(3))*((-1.676+(0.01*accum_dd))))
				error = 100. * (comp2/(1.+comp2))-maturity
			else:
				maturity = miss
				error = miss
			if maturity != miss:
				date_list.append(fdate)
				matur_list.append(maturity)
				error_list.append(error)
		ascospore_dict['dates'] = date_list
		ascospore_dict['maturity'] = matur_list
		ascospore_dict['error'] = error_list
	except:
		print_exception()
	return ascospore_dict

#--------------------------------------------------------------------------------------------		
# obtain everything necessary for fire blight plots
def run_fire_blight_plots (stn,end_date_dt,firstblossom,orchard_history,output):
	try:
		smry_dict = {}
		smry_dict['biofix_name'] = 'First blossom open'
		daily_data = None
		hourly_data = None
		if not end_date_dt: end_date_dt = DateTime.now()
		start_date_dt = DateTime.DateTime(end_date_dt.year,4,1,0)	
		
		end_date_dt = min(end_date_dt, DateTime.DateTime(end_date_dt.year,6,15,23))

		# firstblossom can either be passed into this program, read from a file, or estimated from degree day accumulation
		if not firstblossom:
			firstblossom = newaModel.Models().get_biofix(stn,'as',end_date_dt.year)					#from file
			if not firstblossom:
				jan1_dt = DateTime.DateTime(end_date_dt.year,1,1)						
				hourly_data, daily_data, download_time, station_name = newaCommon.Base().get_hddata (stn, jan1_dt, end_date_dt)
				biofix_dd = phen_events_dict['macph_firstblossom_43']['dd'][2]					#by degree day accumulation
				ret_bf_date, ddaccum, ddmiss = newaModel.Models().accum_degday(daily_data, jan1_dt, end_date_dt, 'dd43be', biofix_dd, stn, station_name)
				if ret_bf_date: firstblossom = ret_bf_date + DateTime.RelativeDate(hour=23)
					
		smry_dict['biofix'] = "%s-%s-%s" % (firstblossom.year,firstblossom.month,firstblossom.day)
		if firstblossom < start_date_dt: start_date_dt = firstblossom
		if not orchard_history: orchard_history = 2
		smry_dict['orchard_history'] = orchard_history

		# obtain daily data
		if not daily_data:
			hourly_data, daily_data, download_time, station_name = newaCommon.Base().get_hddata (stn, start_date_dt, end_date_dt)
		smry_dict['station_name'] = station_name
		
		# format for plot routine
		obs_dict, smry_dict, dly_forecast_data = tp_for_grf(stn, daily_data, smry_dict, start_date_dt, end_date_dt)
			
		# add hourly forecast data
		start_fcst_dt = DateTime.DateTime(*download_time) + DateTime.RelativeDate(hours = +1)
		end_fcst_dt = end_date_dt + DateTime.RelativeDate(days = +5)
		hourly_data = newaModel.Models().add_hrly_fcst(stn,hourly_data,start_fcst_dt,end_fcst_dt)
		
		if firstblossom and len(hourly_data) > 0:
			# calculate degree hours using Tim Smith's table
			deghr_dict = deghr_for_grf (hourly_data,firstblossom,end_fcst_dt)
		else:
			deghr_dict = []

		# produce plot
		onLoadFunction = "produce_fireblight_graph(%s, %s, %s);" % (smry_dict, obs_dict, deghr_dict)
		return newaGraph_io.apple_disease_plot(onLoadFunction)
	except:
		print_exception()
						
#--------------------------------------------------------------------------------------------		
# obtain everything necessary for apple scab plots
def run_apple_scab_plots (stn,end_date_dt,greentip,output):
	try:
		smry_dict = {}
		smry_dict['biofix_name'] = 'Greentip'
		daily_data = None
		if not end_date_dt: end_date_dt = DateTime.now()
		start_date_dt = DateTime.DateTime(end_date_dt.year,3,15,0)	

		end_date_dt = min(end_date_dt, DateTime.DateTime(end_date_dt.year,6,15,23))

		# greentip can either be passed into this program, read from a file, or estimated from degree day accumulation
		if not greentip:
			greentip = newaModel.Models().get_biofix(stn,'as',end_date_dt.year)					#from file
			if not greentip:
				jan1_dt = DateTime.DateTime(end_date_dt.year,1,1)						
				daily_data, station_name = newaCommon.Base().get_daily (stn, jan1_dt, end_date_dt)
				biofix_dd = phen_events_dict['macph_greentip_43']['dd'][2]					#by degree day accumulation
				ret_bf_date, ddaccum, ddmiss = newaModel.Models().accum_degday(daily_data, jan1_dt, end_date_dt, 'dd43be', biofix_dd, stn, station_name)
				if ret_bf_date: greentip = ret_bf_date
					
		smry_dict['biofix'] = "%s-%s-%s" % (greentip.year,greentip.month,greentip.day)

		# obtain hourly and daily data
		start_date_dt = DateTime.DateTime(end_date_dt.year,3,1,1)	#Leave this March 1			
		hourly_data, daily_data, download_time, station_name, avail_vars = newaCommon.Base().get_hddata2 (stn, start_date_dt, end_date_dt)
		smry_dict['station_name'] = station_name
		# now add the forecast data
		start_fcst_dt = DateTime.DateTime(*download_time) + DateTime.RelativeDate(hours = +1)
		end_fcst_dt = end_date_dt + DateTime.RelativeDate(days = +6)
		hourly_data = newaModel.Models().add_hrly_fcst(stn,hourly_data,start_fcst_dt,end_fcst_dt,True)
		daily_data = newaModel.Apple().hrly_to_dly(hourly_data)
		
		# format for plot routine
		if greentip:
			start_date_grf = greentip + DateTime.RelativeDate(days = -6)
		else:
			start_date_grf = start_date_dt
		obs_dict = tp_for_grf2(daily_data, start_date_grf, start_fcst_dt)
			
		# calculate base 0C degree days for ascospore maturity
		if greentip:
			dd_data = newaCommon.Base().degday_calcs(daily_data,greentip,end_fcst_dt,'dd0c','prcp')
		else:
			dd_data = []
		
		if len(dd_data) > 0:
			# calculate ascospore maturity and format for plotting
			ascospore_dict = ascospore_for_grf(dd_data,daily_data)
		else:
			ascospore_dict = {}
			ascospore_dict['dates'] = []
			ascospore_dict['maturity'] = []
			ascospore_dict['error'] = []

		# produce plot
		onLoadFunction = "produce_applescab_graph(%s, %s, %s);" % (smry_dict, obs_dict, ascospore_dict)
		return newaGraph_io.apple_disease_plot(onLoadFunction)
	except:
		print_exception()
						
#--------------------------------------------------------------------------------------------					
def process_input (request,path):
	try:
		stn = None
		year = None
		greentip = None
		firstblossom = None
		orchard_history = None
		accend = None
		output = "tab"
#	 	retrieve input
		if path is None:
			if request and request.form:
				try:
					smry_type = request.form['type'].strip()
					if request.form.has_key('stn'):    stn = request.form['stn'].strip()
					if request.form.has_key('orchard_history'):  orchard_history = int(request.form['orchard_history'])
					if request.form.has_key('year'):   year = int(request.form['year'])
					if request.form.has_key('output'): output = request.form['output']
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
					if request.form.has_key('accend'):
						try:
							mm,dd,yy = request.form['accend'].split("/")
							accend = DateTime.DateTime(int(yy),int(mm),int(dd),23)
						except:
							accend = None
				except:
					print_exception()
					raise program_exit('Error processing request')
			else:
				return newaCommon_io.errmsg('Error processing form; check input')
		elif path[0] in ['apple_scab_grf','fire_blight_grf']:
			try:
				smry_type = path[0]
				stn = path[1]
				if len(path) > 2: year = int(path[2])
				output = "standalone"
			except IndexError:
				raise program_exit('Error processing request - index error')
			except:
				print_exception()
				raise program_exit('Error processing request')
		else:
			return newaCommon_io.errmsg('Error processing input')
			
		if not accend:
			now = DateTime.now()
			if year and year != 9999 and year != now.year:
				accend = DateTime.DateTime(year,6,15,23)

# 		send input to appropriate routine
		if stn:
			if smry_type == 'apple_scab_grf':
				return run_apple_scab_plots (stn,accend,greentip,output)
			elif smry_type == 'fire_blight_grf':
				return run_fire_blight_plots (stn,accend,firstblossom,orchard_history,output)
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