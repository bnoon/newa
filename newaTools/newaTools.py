#!/usr/local/bin/python

import sys, copy, math
from mx import DateTime
from print_exception import print_exception
import newaTools_io
from newaModel.phen_events import phen_events_dict	
import newaCommon_io
from newaCommon.newaCommon import *
from newaTools.Apple_ET_Model import Apple_ET_model
from newaTools.Apple_Thinning_Model.AppleGrowthModel import AppleGrowthModel
import csv
import collections

miss = -999
month_abb = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

class StationProblem (Exception):
	pass

class program_exit (Exception):
	pass

#--------------------------------------------------------------------------------------------		
class BaseTools():
	def calc_degday (self, tmax, tmin, smry_type):
		try:
			if tmax != miss and tmin != miss:
				if smry_type == 'dd4c':
					tave = (tmax+tmin)/2.
					tave_c = (5./9.) * (tave-32.)
					ddval = tave_c - 4.
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
	#			can't be below zero
				if ddval < 0: ddval = 0.
			else:
				ddval = miss
		except:
			print_exception()
		return ddval
	#--------------------------------------------------------------------------------------------		
	def find_biofix (self, hourly_data, jan1_dt, end_date_dt, smry_type, biofix_dd):
		biofix_date = None
		ddmiss = None
		try:
			ddaccum = 0.
			ddmiss = 0
			dly_max = -999
			dly_min = 999
			dly_miss = 0
			ks = hourly_data.keys()
			ks.sort()
			for key_date in ks:
				theDate = DateTime.DateTime(*key_date)
				hourly_temp = hourly_data[key_date]['temp'][0]
				if hourly_temp != miss:
					if hourly_temp > dly_max:
						dly_max = copy.deepcopy(hourly_temp)
					if hourly_temp < dly_min:
						dly_min = copy.deepcopy(hourly_temp)
				else:
					dly_miss = dly_miss + 1
	
	#			end of day update
				if theDate.hour == 23:
					if dly_miss == 0:
						dly_dd = BaseTools().calc_degday(dly_max, dly_min, smry_type)
					else:
						dly_dd = miss
				
	#				check to see if biofix gdd accum has been reached
					if dly_dd != miss:
						ddaccum = ddaccum + dly_dd
					else:
						ddmiss = ddmiss + 1
					if round(ddaccum,0) >= biofix_dd:
						biofix_date = theDate + DateTime.RelativeDate(hours=0)
						break
					dly_max = -999
					dly_min = 999
					dly_miss = 0
		except:
			print_exception()
		
		return biofix_date, ddmiss

#--------------------------------------------------------------------------------------------		
def apple_thinning_model (staid, start_date_dt, end_date_dt, station_type):
	thin_dict = {}
	try:
		weatherDataArray = []
#		initialize daily accumulations
		dly_srad = 0.0
		dly_miss_srad = 0
		dly_maxt = -9999
		dly_mint = 9999
		dly_miss_temp = 0
		daycnt = 0

#		get all hourly data (observed and forecast)
		hourly_data = collect_hourly_input(staid, start_date_dt, end_date_dt, ['temp','srad'], station_type)
		ks = hourly_data.keys()
		ks.sort()
		
		for key_date in ks:
			theDate = DateTime.DateTime(*key_date)
			doy = theDate.day_of_year
			tempv = hourly_data[key_date]['temp'][0]
			sradv = hourly_data[key_date]['srad'][0]

#			accumulate hourly values for day
			if sradv != miss:
				dly_srad = dly_srad + sradv
			else:
				dly_miss_srad = dly_miss_srad + 1
			if tempv != miss:
				if tempv > dly_maxt:
					dly_maxt = copy.deepcopy(tempv)
				if tempv < dly_mint:
					dly_mint = copy.deepcopy(tempv)
			else:
				dly_miss_temp = dly_miss_temp + 1

#			end of day update; save daily values to array
			if theDate.hour == 23:
				if dly_miss_srad == 0:
#					dly_srad = dly_srad*0.0116   ### langleys to KW-hours/m2
					dly_srad = dly_srad*0.0419   ### langleys to MJ/m2
				else:
					dly_srad = miss
				if dly_miss_temp <= 3:
					dly_maxt = (dly_maxt-32.0)*(5.0/9.0)
					dly_mint = (dly_mint-32.0)*(5.0/9.0)
				else:
					dly_maxt = miss
					dly_mint = miss
				weatherDataArray.append([daycnt, dly_mint, dly_maxt, dly_srad])

				dly_srad = 0.0
				dly_miss_srad = 0
				dly_maxt = -9999
				dly_mint = 9999
				dly_miss_temp = 0
				daycnt = daycnt + 1
	except:
		print_exception()

	# Call Apple Growth Model
	model = AppleGrowthModel(weatherDataArray, start_date_dt)
	cellValues = model.evaluate()
	
## Write results to CSV
	
	colSet = set()
	rowSet = set()
	for c in cellValues.keys():
		colSet.add(c[0])
		rowSet.add(c[1])
	
	colList = list(colSet)
	colList.sort()
	rowList = list(rowSet)
	rowList.sort()
	
##	fileHandle = open('appleoutput.csv', 'wb')
##	csvWriter = csv.writer(fileHandle, dialect='excel')
##	csvWriter.writerow(colList)
	
	rowVals = list()
	for r in rowList:
		rowVals = []
		for c in colList:
			rowVals.append(cellValues[c,r])
##		csvWriter.writerow(rowVals)

		if rowVals[14] != miss and rowVals[79] != miss:
			thin_index = rowVals[14] - rowVals[79]
		else:
			thin_index = miss
		thin_dict[rowVals[78]] = {"maxt": rowVals[74], "mint": rowVals[77], "srad": rowVals[22], "dlyCarbonBal": rowVals[14], "totalDemand": rowVals[79],  "thinIndex": thin_index}
		
##	fileHandle.close()

	return thin_dict

#--------------------------------------------------------------------------------------------		
def apple_hourly (staid, start_date_dt, end_date_dt, biofix_dt, station_type):
	et_dict = {}
	try:
#		initialize daily accumulations
		dly_evap = 0.0
		dly_srad = 0.0
		dly_miss = 0
		dly_prcp = 0.0
		dly_prcp_miss = 0

#		get all hourly data (observed and forecast)
		hourly_data = collect_hourly_input(staid, start_date_dt, end_date_dt, ['temp','wspd','tsky','dwpt','srad','prcp'], station_type)

		ks = hourly_data.keys()
		ks.sort()
		for key_date in ks:
			theDate = DateTime.DateTime(*key_date)
			doy = theDate.day_of_year

			tempv = hourly_data[key_date]['temp'][0]
			dwptv = hourly_data[key_date]['dwpt'][0]
			wspdv = hourly_data[key_date]['wspd'][0]
			sradv = hourly_data[key_date]['srad'][0]
			tskyv = hourly_data[key_date]['tsky'][0]
			prcpv = hourly_data[key_date]['prcp'][0]

#			final checks
			if dwptv > tempv: dwptv = tempv
			if tskyv == miss: tskyv = 0.5

#			do hourly et calculations
			if tempv != miss and dwptv != miss and wspdv != miss and sradv != miss:
				evapo = Apple_ET_model.run_apple(theDate.month,theDate.day,theDate.hour, \
						doy,tempv,dwptv,wspdv,sradv,tskyv, biofix_dt)
			elif sradv == 0:
				evapo = 0.		# Reasonable; added to get around missing data night of final forecast day
			else:
				evapo = miss

#			accumulate hourly values for day
			if evapo != miss:
				dly_evap = dly_evap + evapo
				dly_srad = dly_srad + sradv
			else:
				dly_miss = dly_miss + 1
			if prcpv != miss:
				dly_prcp = dly_prcp + prcpv
			else:
				dly_prcp_miss = dly_prcp_miss + 1

#			end of day update
			if theDate.hour == 23:
#				save daily values to dictionary
				tkey = (theDate.year,theDate.month,theDate.day)
				et_dict[tkey] = {}
				et_dict[tkey]['date'] = '%s %d' % (month_abb[theDate.month],theDate.day)
				if dly_miss == 0:
					et_dict[tkey]['et'] = dly_evap
					et_dict[tkey]['srad'] = dly_srad
				else:
					et_dict[tkey]['et'] = miss
					et_dict[tkey]['srad'] = miss
				if dly_prcp_miss <= 3:
					et_dict[tkey]['prcp'] = dly_prcp
				else:
					et_dict[tkey]['prcp'] = miss

				dly_evap = 0.0
				dly_srad = 0.0
				dly_prcp = 0.0
				dly_miss = 0	
				dly_prcp_miss = 0
	except StationProblem, logmsg:
		sys.stdout.write('%s\n' % logmsg)	
	except:
		print_exception()
	
	return et_dict

#--------------------------------------------------------------------------------------------		
def run_apple_et (stn,accend,greentip,output):
	et_dict = {}
	try:
		#date range
		start_date_dt = accend + DateTime.RelativeDate(days=-7) + DateTime.RelativeDate(hour=0,minute=0,second=0.0)
		end_date_dt = accend + DateTime.RelativeDate(days=+6) + DateTime.RelativeDate(hour=23,minute=0,second=0.0)	
		
		if stn[0:1] >= '1' and stn[0:1] <= '9' and stn[1:2] >= '0' and stn[1:2] <= '9':
			station_type = 'njwx'
		elif len(stn) == 4:
			station_type = 'icao'
		elif stn[0:3] == 'cu_' or stn[0:3] == 'um_':
			station_type = 'cu_log'
		elif stn[0:3] == "ew_":
			stn = stn[3:]
			station_type = 'miwx'
		elif len(stn) == 3 or len(stn) == 6:
			station_type = 'newa'
		else:
			raise StationProblem('Cannot determine station type for %s'%stn)
		
		try:
			biofix_dt = greentip + DateTime.RelativeDate(hour=0, minute=0, second=0.0)
		except TypeError:
			return newaTools_io.apple_et_results(None)
		
		# get daily modeled et, solar rad and precipitation
		et_dict['data'] = apple_hourly (stn, start_date_dt, end_date_dt, biofix_dt, station_type)
	except:
		print_exception()
	
	return newaTools_io.apple_et_results(et_dict)

#--------------------------------------------------------------------------------------------		
def run_apple_et_specs (stn,accend,output):
	et_dict = {}

	#date range
	start_date_dt = accend + DateTime.RelativeDate(days=-7) + DateTime.RelativeDate(hour=0,minute=0,second=0.0)
	end_date_dt = accend + DateTime.RelativeDate(days=+6) + DateTime.RelativeDate(hour=23,minute=0,second=0.0)	
	
	fcst_stn = copy.deepcopy(stn)
	if stn[0:1] >= '1' and stn[0:1] <= '9' and stn[1:2] >= '0' and stn[1:2] <= '9':
		station_type = 'njwx'
	elif len(stn) == 4:
		station_type = 'icao'
	elif stn[0:3] == 'cu_' or stn[0:3] == 'um_':
		station_type = 'cu_log'
	elif stn[0:3] == "ew_":
		stn = stn[3:]
		station_type = 'miwx'
	elif len(stn) == 3 or len(stn) == 6:
		station_type = 'newa'
	else:
		raise StationProblem('Cannot determine station type for %s'%stn)
	
	#need to get greentip date in DateTime format for leaf area adjustment
	biofix_dd = phen_events_dict['macph_greentip_43']['dd'][2]					#green tip degree day accumulation
	hourly_data = {}
	jan1_dt = DateTime.DateTime(end_date_dt.year,1,1,0,0,0)
	fcst_data = get_fcst_data (fcst_stn, 'temp', jan1_dt, end_date_dt)
	hourly_data = get_hourly_data (stn, 'temp', jan1_dt, end_date_dt, hourly_data, fcst_data, station_type)
	biofix_dt, ddmiss = BaseTools().find_biofix (hourly_data, jan1_dt, end_date_dt, 'dd43be', biofix_dd)
	if biofix_dt and ddmiss <= 7: 
		et_dict['greentip'] = '%d/%d/%d' % (biofix_dt.month,biofix_dt.day,biofix_dt.year)
	ucanid,station_name = get_metadata (stn, station_type)
	et_dict['station_name'] = station_name
	
	return newaTools_io.apple_et_specs(et_dict)

#--------------------------------------------------------------------------------------------		
def run_apple_thin (stn,accend,greentip,bloom,output):
	thin_dict = {}
	try:
		if stn[0:1] >= '1' and stn[0:1] <= '9' and stn[1:2] >= '0' and stn[1:2] <= '9':
			station_type = 'njwx'
		elif len(stn) == 4:
			station_type = 'icao'
		elif stn[0:3] == 'cu_' or stn[0:3] == 'um_' or stn[0:3] == 'un_' or stn[0:3] == 'uc_':
			station_type = 'cu_log'
		elif stn[0:3] == "ew_":
			stn = stn[3:]
			station_type = 'miwx'
		elif len(stn) == 3 or len(stn) == 6:
			station_type = 'newa'
		else:
			raise StationProblem('Cannot determine station type for %s'%stn)
		
		try:
			biofix_dt = greentip + DateTime.RelativeDate(hour=0, minute=0, second=0.0)
		except TypeError:
			return newaTools_io.apple_thin_results(None)
		try:
			bloom_dt = bloom + DateTime.RelativeDate(hour=0, minute=0, second=0.0)
		except TypeError:
			bloom_dt = None
		
		#date range
		accend = accend + DateTime.RelativeDate(hour=0,minute=0,second=0.0)
##		start_date_dt = accend + DateTime.RelativeDate(days=-7) + DateTime.RelativeDate(hour=0,minute=0,second=0.0)
		start_date_dt = biofix_dt
		end_date_dt = accend + DateTime.RelativeDate(days=+6) + DateTime.RelativeDate(hour=23,minute=0,second=0.0)	
		
		# get model results
		thin_dict['data'] = apple_thinning_model (stn, start_date_dt, end_date_dt, station_type)
		thin_dict['selectedDate'] = accend
		thin_dict['greentipDate'] = biofix_dt
		thin_dict['bloomDate'] = bloom_dt
	except:
		print_exception()
	
	return newaTools_io.apple_thin_results(thin_dict)

#--------------------------------------------------------------------------------------------		
def run_apple_thin_specs (stn,accend,output):
	et_dict = {}

	#date range
	start_date_dt = accend + DateTime.RelativeDate(days=-7) + DateTime.RelativeDate(hour=0,minute=0,second=0.0)
	end_date_dt = accend + DateTime.RelativeDate(days=+6) + DateTime.RelativeDate(hour=23,minute=0,second=0.0)	
	
	fcst_stn = copy.deepcopy(stn)
	if stn[0:1] >= '1' and stn[0:1] <= '9' and stn[1:2] >= '0' and stn[1:2] <= '9':
		station_type = 'njwx'
	elif len(stn) == 4:
		station_type = 'icao'
	elif stn[0:3] == 'cu_' or stn[0:3] == 'um_' or stn[0:3] == 'un_' or stn[0:3] == 'uc_':
		station_type = 'cu_log'
	elif stn[0:3] == "ew_":
		stn = stn[3:]
		station_type = 'miwx'
	elif len(stn) == 3 or len(stn) == 6:
		station_type = 'newa'
	else:
		raise StationProblem('Cannot determine station type for %s'%stn)
	
	#need to get greentip and bloom date in DateTime format
	biofix_dd = phen_events_dict['macph_greentip_43']['dd'][2]					#green tip degree day accumulation
	bloom_dd = phen_events_dict['macph_bloom_43']['dd'][2]						#bloom degree day accumulation
	
	hourly_data = {}
	jan1_dt = DateTime.DateTime(end_date_dt.year,1,1,0,0,0)
	fcst_data = get_fcst_data (fcst_stn, 'temp', jan1_dt, end_date_dt)
	hourly_data = get_hourly_data (stn, 'temp', jan1_dt, end_date_dt, hourly_data, fcst_data, station_type)
	biofix_dt, ddmiss = BaseTools().find_biofix (hourly_data, jan1_dt, end_date_dt, 'dd43be', biofix_dd)
	bloom_dt, bloom_ddmiss = BaseTools().find_biofix (hourly_data, jan1_dt, end_date_dt, 'dd43be', bloom_dd)
	if biofix_dt and ddmiss <= 7: 
		et_dict['greentip'] = '%d/%d/%d' % (biofix_dt.month,biofix_dt.day,biofix_dt.year)
	if bloom_dt and bloom_ddmiss <= 7: 
		et_dict['bloom'] = '%d/%d/%d' % (bloom_dt.month,bloom_dt.day,bloom_dt.year)
	ucanid,station_name = get_metadata (stn, station_type)
	et_dict['station_name'] = station_name
	
	return newaTools_io.apple_thin_specs(et_dict)

#--------------------------------------------------------------------------------------------					
def process_help (request, path):
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
		elif path[0] in ['apple_et', 'apple_thin']:
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
		if smry_type == 'apple_et':
			return newaTools_io.helppage([("Model overview","/apple_et_help.html"),
										  ("Station inclusion","/apple_tool_stations.html")])
		elif smry_type == 'apple_thin':
			return newaTools_io.helppage([("Model overview","/apple_thin_help.html"),
										  ("Station inclusion","/apple_tool_stations.html")])
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
		accend = None
		greentip = None
		bloom = None
		output = "tab"
#	 	retrieve input
		if path is None:
			if request and request.form:
				try:
					smry_type = request.form['type'].strip()
					if request.form.has_key('stn'):             stn = request.form['stn'].strip()
					if request.form.has_key('output'):          output = request.form['output']
					if request.form.has_key('greentip'):
						try:
							mm,dd,yy = request.form['greentip'].split("/")
							greentip = DateTime.DateTime(int(yy),int(mm),int(dd),23)
						except:
							greentip = None
					if request.form.has_key('bloom'):
						try:
							mm,dd,yy = request.form['bloom'].split("/")
							bloom = DateTime.DateTime(int(yy),int(mm),int(dd),23)
						except:
							bloom = None
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
		elif path[0] in ['apple_et','apple_et_specs', 'apple_thin', 'apple_thin_specs']:
			try:
				smry_type = path[0]
				if len(path) > 1: stn = path[1]
				output = "standalone"
			except IndexError:
				raise program_exit('Error processing request - index error')
			except:
				print_exception()
				raise program_exit('Error processing request')
		else:
			return newaCommon_io.errmsg('Error processing input')
			
# 		send input to appropriate routine
		if stn:
			if smry_type == 'apple_et':
				return run_apple_et(stn,accend,greentip,output)
			elif smry_type == 'apple_et_specs':
				return run_apple_et_specs(stn,accend,output)
			elif smry_type == 'apple_thin':
				return run_apple_thin(stn,accend,greentip,bloom,output)
			elif smry_type == 'apple_thin_specs':
				return run_apple_thin_specs(stn,accend,output)
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

