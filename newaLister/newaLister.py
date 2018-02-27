#!/usr/local/bin/python

import sys, copy, math
from mx import DateTime
from print_exception import print_exception
import newaLister_io
from newaCommon import newaCommon, newaCommon_io
from newaDisease import newaDisease

miss = -999
month_names = ["","January","February","March","April","May","June","July","August","September","October","November","December"]
class program_exit (Exception):
	pass

#--------------------------------------------------------------------------------------------		
# calculate dewpoint from temp and rh
def calc_dewpoint(temp,rh):
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

#--------------------------------------------------------------------------------------------		
# calculate daily degree day stats from daily values
def degday_summary(daily_data,year,month,smry_type):
	degday_data = []
	degday_miss = None
	try:
		accum_jan1 = 0.
		accum_mar1 = 0.
		accum_apr1 = 0.
		accum_may1 = 0.
		jan1_miss = 0
		mar1_miss = 0
		apr1_miss = 0
		may1_miss = 0
		jan1_flag = ''
		mar1_flag = ''
		apr1_flag = ''
		may1_flag = ''
		for dly_dt,tave_hr,tmax,tmin,prcp,lwet,rhum,wspd,srad,st4a,st4x,st4n,dflags in daily_data:
			temp_flag,prcp_flag,lwet_flag,rhum_flag,wspd_flag,wdir_flag,srad_flag,st4i_flag = dflags
			this_yr,this_mon = int(dly_dt[0]),int(dly_dt[1])
			if this_yr != year:
				continue
			if tmax != miss and tmin != miss:
				if smry_type == 'dd4c':
					tave = (tmax+tmin)/2.
					tave_c = (5./9.) * (tave-32.)
					ddval = tave_c - 4.
				elif smry_type == 'dd143c':
					tave = (tmax+tmin)/2.
					tave_c = (5./9.) * (tave-32.)
					ddval = tave_c - 14.3
				elif smry_type == 'dd0c':
					tave = (tmax+tmin)/2.
					tave_c = (5./9.) * (tave-32.)
					ddval = tave_c - 0.
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
				elif smry_type == 'dd43be' or smry_type == 'dd50be':
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
				elif smry_type == 'dd4714':
					try:
						base = 47.14
						tave = (tmax+tmin)/2.
						ddval = tave - base
					except:
						ddval = miss
				else:
					try:
						base = int(smry_type[2:4])
						tave = (tmax+tmin)/2.
						ddval = tave - float(base)
					except:
						ddval = miss
#				save values above zero and round
				if ddval > 0:
					ddval = round(ddval+.01,1)
				else:
					ddval = 0.
			else:
				ddval = miss
#			now do accumulations
			if this_mon >= 1:
				if ddval != miss: 
					accum_jan1 = accum_jan1 + ddval
					if temp_flag == 'E': jan1_flag = 'E'
				else:
					jan1_miss = jan1_miss + 1
			if this_mon >= 3:
				if ddval != miss: 
					accum_mar1 = accum_mar1 + ddval
					if temp_flag == 'E': mar1_flag = 'E'
				else:
					mar1_miss = mar1_miss + 1
			if this_mon >= 4:
				if ddval != miss: 
					accum_apr1 = accum_apr1 + ddval
					if temp_flag == 'E': apr1_flag = 'E'
				else:
					apr1_miss = apr1_miss + 1
			if this_mon >= 5:
				if ddval != miss: 
					accum_may1 = accum_may1 + ddval
					if temp_flag == 'E': may1_flag = 'E'
				else:
					may1_miss = may1_miss + 1
#			save values for desired month
			if this_yr == year and this_mon == month:
				if this_mon >= 1:
					dacc_jan1 = accum_jan1
				else:
					dacc_jan1 = miss
				if this_mon >= 3:
					dacc_mar1 = accum_mar1
				else:
					dacc_mar1 = miss
				if this_mon >= 4:
					dacc_apr1 = accum_apr1
				else:
					dacc_apr1 = miss
				if this_mon >= 5:
					dacc_may1 = accum_may1
				else:
					dacc_may1 = miss
				ddflags = (temp_flag,jan1_flag,mar1_flag,apr1_flag,may1_flag)
				degday_data.append((dly_dt,tmax,tmin,ddval,dacc_jan1,dacc_mar1,dacc_apr1,dacc_may1,ddflags))
		degday_miss = (jan1_miss,mar1_miss,apr1_miss,may1_miss)
	except:
		print 'Error calculating degree days'
		print_exception()
	return degday_data, degday_miss

#--------------------------------------------------------------------------------------------		
# calculate monthly summary stats from daily values
def monthly_summary(daily_data,year,month):
	monthly_data = None
	try:
		tave_sum = 0.
		tmax_max = -9999.
		tmin_min = 9999.
		prcp_sum = 0.
		lwet_sum = 0.
		rhum_sum = 0.
		tave_cnt = 0.
		tmax_cnt = 0.
		tmin_cnt = 0.
		prcp_cnt = 0.
		lwet_cnt = 0.
		rhum_cnt = 0.
		wspd_sum = 0.
		wspd_cnt = 0.
		srad_sum = 0.
		srad_cnt = 0.
		st4a_sum = 0.
		st4a_cnt = 0.
		st4x_cnt = 0.
		st4n_cnt = 0.
		st4x_max = -9999.
		st4n_min = 9999.
		for dly_dt,tave,tmax,tmin,prcp,lwet,rhum,wspd,srad,st4a,st4x,st4n,dflags in daily_data:
			this_yr,this_mon = int(dly_dt[0]),int(dly_dt[1])
			if this_yr == year and this_mon == month:
				if tave != miss:
					tave_sum = tave_sum + tave
					tave_cnt = tave_cnt + 1
				if tmax != miss:
					if tmax > tmax_max: tmax_max = copy.deepcopy(tmax)
					tmax_cnt = tmax_cnt + 1
				if tmin!= miss:
					if tmin < tmin_min: tmin_min = copy.deepcopy(tmin)
					tmin_cnt = tmin_cnt + 1
				if prcp != miss:
					prcp_sum = prcp_sum + prcp
					prcp_cnt = prcp_cnt + 1
				if lwet != miss:
					lwet_sum = lwet_sum + lwet
					lwet_cnt = lwet_cnt + 1
				if rhum != miss:
					rhum_sum = rhum_sum + rhum
					rhum_cnt = rhum_cnt + 1
				if wspd != miss:
					wspd_sum = wspd_sum + wspd
					wspd_cnt = wspd_cnt + 1
				if srad != miss:
					srad_sum = srad_sum + srad
					srad_cnt = srad_cnt + 1
				if st4a != miss:
					st4a_sum = st4a_sum + st4a
					st4a_cnt = st4a_cnt + 1
				if st4x != miss:
					if st4x > st4x_max: st4x_max = copy.deepcopy(st4x)
					st4x_cnt = st4x_cnt + 1
				if st4n!= miss:
					if st4n < st4n_min: st4n_min = copy.deepcopy(st4n)
					st4n_cnt = st4n_cnt + 1
#		process monthly stats
		if tave_cnt > 0:
			tave_smry = tave_sum/tave_cnt
		else:
			tave_smry = miss
		if tmax_cnt > 0:
			tmax_smry = tmax_max
		else:
			tmax_smry = miss
		if tmin_cnt > 0:
			tmin_smry = tmin_min
		else:
			tmin_smry = miss
		if prcp_cnt > 0:
			prcp_smry = prcp_sum
		else:
			prcp_smry = miss
		if lwet_cnt > 0:
			lwet_smry = lwet_sum
		else:
			lwet_smry = miss
		if rhum_cnt > 0:
			rhum_smry = rhum_sum
		else:
			rhum_smry = miss
		if wspd_cnt > 0:
			wspd_smry = wspd_sum/wspd_cnt
		else:
			wspd_smry = miss
		if srad_cnt > 0:
			srad_smry = srad_sum
		else:
			srad_smry = miss
		if st4a_cnt > 0:
			st4a_smry = st4a_sum/st4a_cnt
		else:
			st4a_smry = miss
		if st4x_cnt > 0:
			st4x_smry = st4x_max
		else:
			st4x_smry = miss
		if st4n_cnt > 0:
			st4n_smry = st4n_min
		else:
			st4n_smry = miss
		monthly_data = (tave_smry,tmax_smry,tmin_smry,prcp_smry,lwet_smry,\
				        rhum_smry,wspd_smry,srad_smry,st4a_smry,st4x_smry,st4n_smry)
	except:
		print 'Error processing monthly summary'
		print_exception()
	return monthly_data

def get_sister_info (stn):
	var_sister= []
	try:
		from newaCommon.sister_info import sister_info
		if sister_info.has_key(stn):
			sister = sister_info[stn]
			for var in sister.keys():
				if sister[var][0:1] >= '1' and sister[var][0:1] <= '9' and sister[var][1:2] >= '0' and sister[var][1:2] <= '9':
					station_type = 'njwx'
				elif len(sister[var]) == 4 and sister[var][0:1].upper() == 'K':
					sister[var] = sister[var].upper()
					station_type = "icao"
				elif len(sister[var]) == 4:
					sister[var] = sister[var]
					station_type = "oardc"
				elif sister[var][0:3] == "cu_" or sister[var][0:3] == "um_" or sister[var][0:3] == "uc_" or sister[var][0:3] == "un_":
					station_type = "cu_log"
				elif sister[var][0:3] == "ew_":
					sister[var] = sister[var][3:]
					station_type = 'miwx'
				elif len(sister[var]) == 3 or len(sister[var]) == 6:
					station_type = "newa"
				est_staid,sister_name = newaCommon.get_metadata (sister[var], station_type)
				var_sister.append((var,sister_name))
	except:
		print 'Error finding sister info'
		print_exception()
	return var_sister

#--------------------------------------------------------------------------------------------		
def run_ddrange(stn,ddtype,accstr,accend):
	try:
		base = newaCommon.Base()
		cabbage = newaDisease.Cabbage()
		smry_dict = {'ddtype': ddtype.replace("dd", "")}
		now = DateTime.now()
		if not accend:
			accend = now
		end_date_dt = accend
		if not accstr:
			accstr = DateTime.DateTime(end_date_dt.year, 1, 1, 0)
		start_date_dt = accstr

		if start_date_dt > end_date_dt:
			return newaCommon_io.errmsg('Start date must be before end data.')

		if end_date_dt.year != now.year:
			smry_dict['this_year'] = False
			end_date_dt = end_date_dt + DateTime.RelativeDate(days = +6)
		else:
			smry_dict['this_year'] = True

		hourly_data, daily_data, download_time, station_name, avail_vars =  base.get_hddata2 (stn, start_date_dt, end_date_dt)
		smry_dict['last_time'] = download_time

		# add forecast data
		if smry_dict['this_year']:
			start_fcst_dt = DateTime.DateTime(*download_time) + DateTime.RelativeDate(hours = +1)
			end_fcst_dt = end_date_dt + DateTime.RelativeDate(days = +6)
			hourly_data = newaDisease.add_hrly_fcst(stn,hourly_data,start_fcst_dt,end_fcst_dt)
			daily_data = newaDisease.hrly_to_dly(hourly_data)
		else:
			start_fcst_dt = end_date_dt + DateTime.RelativeDate(hours = +1)
			end_fcst_dt = end_date_dt	
			end_date_dt = end_date_dt + DateTime.RelativeDate(days = -6)

		if len(daily_data) > 0:
			degday_dict = base.degday_calcs (daily_data,start_date_dt,end_fcst_dt, ddtype, "accum")

			if len(degday_dict) > 0:
				# get dates for gdd table
				smry_dict = cabbage.setup_dates(smry_dict, end_date_dt)
				# get dd for days of interest (including forecast)
				smry_dict = cabbage.add_ddays(smry_dict,degday_dict,start_date_dt,end_date_dt)
				return newaLister_io.ddrange_html(station_name,smry_dict,degday_dict)
			else:
				return self.nodata(stn, station_name, start_date_dt, end_date_dt)
		else:
			return self.nodata (stn, station_name, start_date_dt, end_date_dt)
	except:
		print_exception()
	return

#--------------------------------------------------------------------------------------------		
def process_input (request,path):
	try:
# 		retrieve input
		if path is None:
			newForm = {}
			for k,v in request.form.items() :
				newForm[str(k)] = str(v)
			request.form = newForm
			if request and request.form:
				try:
					stn = request.form['stn'].strip()
					smry_type = request.form['type'].strip()
					if request.form.has_key('month'):
						month = int(request.form['month'])
					else:
						month = None
					if request.form.has_key('year'):
						year = int(request.form['year'])
					else:
						year = None					
					if request.form.has_key('accend'):
						try:
							mm,dd,yy = request.form['accend'].split("/")
							accend = DateTime.DateTime(int(yy),int(mm),int(dd),23)
						except:
							accend = None
					else:
						accend = None
					if request.form.has_key('accstr'):
						try:
							mm,dd,yy = request.form['accstr'].split("/")
							accstr = DateTime.DateTime(int(yy),int(mm),int(dd),0)
						except:
							accstr = None
					else:
						accstr = None
					if request.form.has_key('ddtype'):
						ddtype = request.form['ddtype'].strip()
					else:
						ddtype = None
				except:
					print_exception()
					raise program_exit('Error processing request')
			else:
				return newaCommon_io.errmsg('Error processing request; check input')
		elif path[0] in ('dly','hly','hly2') or path[0][0:2] == 'dd':
			try:
				smry_type = path[0]
				stn = path[1]
				year = int(path[2])
				month = int(path[3])
			except IndexError:
				raise program_exit('Error processing request - index error')
			except:
				print_exception()
				raise program_exit('Error processing request')
		elif path[0] == 'est_info':
			try:
				smry_type = path[0]
				stn = path[1]
				if len(path) > 2:
					year = int(path[2])
					month = int(path[3])
				else:
					now = DateTime.now()
					year = now.year
					month = now.month
			except IndexError:
				raise program_exit('Error processing request - index error')
			except:
				print_exception()
				raise program_exit('Error processing request')
		else:
			return newaCommon_io.errmsg('Error processing input')
			
		if smry_type == 'ddrange':
			return run_ddrange(stn,ddtype,accstr,accend)
			
		if year and year == 9999:
			now = DateTime.now()
			year = now.year

		req_date_dt = DateTime.DateTime(year,month,1,0)
		if smry_type == 'hly' or smry_type == 'dly' or smry_type == 'hly2':
			start_date_dt = req_date_dt
		else:
			start_date_dt = DateTime.DateTime(year,1,1,0)
		end_date_dt = req_date_dt + DateTime.RelativeDate(months=+1)

		orig_stn = copy.deepcopy(stn)
		if stn[0:1] >= '1' and stn[0:1] <= '9' and stn[1:2] >= '0' and stn[1:2] <= '9':
			station_type = 'njwx'
		elif len(stn) == 4 and stn[0:1].upper() == 'K':
			station_type = 'icao'
		elif len(stn) == 4:
			station_type = 'oardc'
		elif stn[0:3] == "cu_" or stn[0:3] == "um_" or stn[0:3] == "uc_" or stn[0:3] == "un_":
			station_type = 'cu_log'
		elif stn[0:3] == "ew_":
			stn = stn[3:]
			station_type = 'miwx'
		elif len(stn) == 3 or len(stn) == 6:
			station_type = 'newa'
		else:
			return newaCommon_io.errmsg('Error processing request; check station input')

#		get ucanid and station name from metadata
		if smry_type != 'hly2':
			ucanid,station_name = newaCommon.get_metadata (stn, station_type)
			if station_type == 'icao':
				staid = stn.upper()
			else:
				staid = ucanid
		
		if smry_type == 'est_info':
			var_sister = get_sister_info (orig_stn)
			return newaLister_io.estimation_info(stn,station_name,var_sister,year,month)
	
# 		obtain all hourly and daily data for station
		if smry_type != 'hly2':
			hourly_data,daily_data,avail_vars = newaCommon.get_newa_data (staid,stn,start_date_dt,end_date_dt,station_type)
		if smry_type == 'hly2' or len(avail_vars) > 0: 
			if smry_type == 'dly':
				monthly_data = monthly_summary(daily_data,year,month)
				numcols = len(avail_vars)
				if 'dwpt' in avail_vars: numcols = numcols-1	#not used
				if 'temp' in avail_vars: numcols = numcols+2	#max, min, avg
				if 'st4i' in avail_vars: numcols = numcols+2	#max, min, avg
				return newaLister_io.dly_list_html(stn,station_name,year,month,daily_data,monthly_data,avail_vars,numcols,miss)
			elif smry_type == 'hly':	
				if 'dwpt' not in avail_vars and 'temp' in avail_vars and 'rhum' in avail_vars: avail_vars.append('dwpt')
				return newaLister_io.hly_list_html(orig_stn,station_name,year,month,hourly_data,avail_vars,miss,station_type)
			elif smry_type == 'hly2':	
				return newaLister_io.hly_listWS_html(stn,station_type,year,month)
			if smry_type in ['dd4c','dd143c','dd32','dd39','dd40','dd43','dd45','dd48','dd50','dd8650','dd55','dd43be','dd50be','dd4714']:
				degday_data, degday_miss = degday_summary(daily_data,year,month,smry_type)
				if len(degday_data) == 0:
		#			no data - try to provide additional information
					if newaCommon.sta_por.has_key(stn):
						bd,ed = newaCommon.sta_por[stn]
						spor_dt = DateTime.DateTime(int(bd[0:4]),int(bd[4:6]),int(bd[6:8]))
						if ed == '99991231':
							epor_dt = DateTime.now()
						else:
							epor_dt = DateTime.DateTime(int(ed[0:4]),int(ed[4:6]),int(ed[6:8]))
						if req_date_dt < spor_dt:
							addl_line = 'Data for %s starts %d/%d' % (station_name,spor_dt.month,spor_dt.year)
						elif end_date_dt > epor_dt:
							addl_line = 'Data for %s have been collected up to %d/%d' % (station_name,epor_dt.month,epor_dt.year)
						else:
							addl_line = None
					else:
						addl_line = None
					return newaCommon_io.nodata(addl_line)
				return newaLister_io.degday_list_html(stn,station_name,year,month,degday_data,degday_miss,miss,smry_type)
			else:
				return newaCommon_io.errmsg('Error processing request')
		else:
#			no data - try to provide additional information
			if newaCommon.sta_por.has_key(stn):
				bd,ed = newaCommon.sta_por[stn]
				spor_dt = DateTime.DateTime(int(bd[0:4]),int(bd[4:6]),int(bd[6:8]))
				if ed == '99991231':
					epor_dt = DateTime.now()
				else:
					epor_dt = DateTime.DateTime(int(ed[0:4]),int(ed[4:6]),int(ed[6:8]))
				if req_date_dt < spor_dt:
					addl_line = 'Data for %s starts %d/%d' % (station_name,spor_dt.month,spor_dt.year)
				elif end_date_dt > epor_dt:
					addl_line = 'Data for %s has been collected up to %d/%d' % (station_name,epor_dt.month,epor_dt.year)
				else:
					addl_line = None
			else:
				addl_line = None
			return newaCommon_io.nodata(addl_line)
	except program_exit,logmsg:
		print logmsg
		return newaCommon_io.errmsg('Error processing request; check input')
	except:
		if  request and request.form:
			print 'Exception - form is',request.form
		print_exception()
		return newaCommon_io.errmsg('Unexpected error')
