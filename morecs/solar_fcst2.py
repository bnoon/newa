import sys
from bsddb import hashopen
from cPickle import loads
from print_exception import print_exception
from mx import DateTime
from solar_routines import SOLAR_CALC_H
from morecs_hourly import estmiss

miss = -999

# get the available forecast data
def get_srfcst_data (stn, start_date, end_date):
	hourly_fcst = {}
	try:
		start_date_dt = DateTime.DateTime(*start_date)
		end_date_dt = DateTime.DateTime(*end_date)
		stn = stn.upper()
		forecast_db = hashopen('/Users/keith/NDFD/hourly_forecasts.db','r')		
		stn_dict = loads(forecast_db[stn])
		latlon = stn_dict['ll']
		for requested_var in ['tsky','dwpt']:
			if stn_dict.has_key(requested_var):
				if not hourly_fcst.has_key(requested_var):
					hourly_fcst[requested_var] = {}
				for dkey in stn_dict[requested_var].keys():
					dkey_dt = DateTime.DateTime(*dkey)
					if dkey_dt >= start_date_dt and dkey_dt <= end_date_dt:
						for h in range(0,24):
							if stn_dict[requested_var][dkey][h] != miss:
								tkey = (dkey[0],dkey[1],dkey[2],h)
								hourly_fcst[requested_var][tkey] = stn_dict[requested_var][dkey][h]
		forecast_db.close()
	except:
		print_exception()
	return latlon, hourly_fcst

# forecast solar radiation
def solar_main_fcst2(stnid,sd,ed):
#	Initialize output lists
	SR_out={}

#	Make all stations ASOS	
	asos = 1
	
#	don't have this in metadata; assume we're in the East
	utc_lapse = 5

	######### Needed since MORECS does full days ###############################
	if sd[3] > 0: sd[3] = 0
	if ed[3] < 23: ed[3] = 23

#	Create date list
	date_list=[]
	ds=DateTime.Date(sd[0],sd[1],sd[2])
	d2=DateTime.Date(ed[0],ed[1],ed[2])
	p_inc = 0
	while p_inc >= 0:
		dn = ds + DateTime.RelativeDate(days=p_inc)
		if dn <= d2:
			date_list.append([dn.year,dn.month,dn.day])
			p_inc = p_inc + 1
		else:
			break
			
#	get lat, lon and forecast data
	ll, hrly_fcst = get_srfcst_data (stnid, sd, ed)
	
	lat = ll[0]
	lon = ll[1]
	
	# don't have pressure forecasts
	pres_list = []
	for h in range(24):
		pres_list.append(30. * 3397./1000.)

	# set snow depth to zero
	sno=0
		
	### Loop through hourly data
	for d in date_list:
		trans = {}
		cl_alb = {}

		# define julian day
		julian_day=DateTime.Date(d[0],d[1],d[2]).day_of_year
		
		# fill in tsky
		tsky_list = []
		for h in range(24):
			if hrly_fcst['tsky'].has_key((d[0],d[1],d[2],h)):
				tsky_list.append(hrly_fcst['tsky'][(d[0],d[1],d[2],h)])
			else:
				tsky_list.append(miss)
			
		dwpt_list = []

		for i in range(24):
			# build a list of dewpoint values for the day
			if hrly_fcst['dwpt'].has_key((d[0],d[1],d[2],i)):
				dwpt_list.append(hrly_fcst['dwpt'][(d[0],d[1],d[2],i)])
			else:
				dwpt_list.append(miss)
		
			# determine if fog or haze is present
			haze,fog=0,0
#			add folllowing if/when wx forecasts become available
#			for w in wx[d[0]][julian_day][i]:
#				if w in [81,82]: haze=1
#				if w in [70,71,72,73,74,75,77,78]: fog=1

			# use equation to estimate the cloud transmission values
			if tsky_list[i] == miss:
				cl = estmiss(tsky_list,i,miss)
			else:
				cl = tsky_list[i]
				
			if cl == miss:
				print 'tsky missing for:',d,i
				trans[i] = 1.0
				cl_alb[i] = miss
			else:
				# replace just this:
#				trans[i] = -2.8855*(cl**4) + 5.3559*(cl**3) - 3.4322*(cl**2) + 0.295*cl + 0.9999
				# with this:
				if cl < 0.75:
					trans[i] = -2.8855*(cl**4) + 5.3559*(cl**3) - 3.4322*(cl**2) + 0.295*cl + 0.9999
				else:
					trans[i] = 1.549 - 1.216*cl		#added this condition 2/6/2013 -kle
				# refine  #
				# and then this:   (3/26/2012 -kle)
				#   0-20	-0.1
				#  20-30	-0.04
				#  30-60	-0.02
				#  60-100	-0.1					
				if cl == 0.0:
					pass
				elif cl <= 0.2 or cl > 0.6:
					trans[i] = trans[i] - 0.1
				elif cl <= 0.3:
					trans[i] = trans[i] - 0.04
				elif cl <= 0.6:
					trans[i] = trans[i] - 0.02

				if trans[i] > 1: trans[i] = 0.9999

#				Need visibility for following adjustments
#				# Adjusts transmissivity value when visibility is less than 1 mile
#				visib = vis[d[0]][julian_day][i]		#changed [h] ti [i] - kle 7/20/2010
#				if visib != miss and visib < 1.0: 
#					trans[i] = trans[i]*0.72	
#				# Adjusts transmissivity if haze is reported with other than clear skies
#				elif haze==1:
#					trans[i]=trans[i]*0.92
#		
#				if trans[i]==0.9999:	# clear skies
#					# Adjusts clear sky transmissivity if visibility is less than
#					# 10 miles and no fog or haze is reported
#					if visib != miss and visib < 10.0 and (fog==0 and haze==0):
#						trans[i] = 0.96
#					# Adjusts clear sky tranmissivity if fog or haze is reported
#					elif visib < 1.0 and (fog==1 or haze==1):
#						trans[i] = 0.92
	
				# Cloud albedo
				if cl == 0:
					cl_alb[i] = 0.0
				else:
					cl_alb[i] =	0.5
					
		# call routine to calculate global solar radiation values
		sun_top,sun_clear,sun_cloud,zenith = SOLAR_CALC_H(d[0], d[1],\
			julian_day, pres_list, dwpt_list, trans, cl_alb,\
			miss,miss,miss,sno,miss,miss,lat,lon,miss,utc_lapse,miss,asos)
			
		for h in range(24):
			sr_date=(d[0],d[1],d[2],h)
			if sun_cloud[h] == miss or sun_cloud[h] == -99:
				SR_out[sr_date] = miss
			else:
				SR_out[sr_date] = sun_cloud[h]*23.88	#in langleys

	return SR_out
