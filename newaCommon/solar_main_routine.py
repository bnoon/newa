import sys
import string
import math
import random
from mx import DateTime

from morecs import solar_routines
from ucanStandardRequests import *
from util.station_searches import getNearestCoop
from morecs.stationInfo import stationInfo
from morecs.morecs_hourly import getHourlyVars

def SOLAR_MAIN(ICAO,sd,ed,stpr0,wthr0,dwpt0,visi0,ccnd0,chgt0,ceil0,tsky0):
# 	Define units 1=langleys; 2=MJ/m2; 3=W/m2; 4=BTU/ft2
	units=1

# 	Define Temporal resolution of model output
# 	1=Daily; 2=Hourly
	temp_res=2

# 	Missing Value and initial value for asos
	miss = -999; asos = 0
	
#	Value used when ceiling is "unlimited"
	unlimited = 100000.

#	Codes for haze and fog occurrences	
	haze_list=[81,82]
	fog_list=[70,71,72,73,74,75,77,78]

	######### Obtain the station information ###################################
	sinf = stationInfo()
	asos_date = sinf.getvar(ICAO, "asos_date")
	lat = sinf.getvar(ICAO, "lat")
	lon = sinf.getvar(ICAO, "lon")
	utc_lapse = sinf.getvar(ICAO, "gmt_offset")
	snow_station = sinf.getvar(ICAO, "snow_station")
	############################################################################

	######### Find nearest snow station if not identified ######################
	if snow_station == None:
		varmajor = 11; detailed_check = 1
		snow_station = getNearestCoop (lat,lon,varmajor,sd,ed,detailed_check)
		sinf.setvar(ICAO, "snow_station", snow_station)
	############################################################################

	######### Set utc_lapse to 5 if not available ##############################
	if utc_lapse == -999:
		print "Error: no gmt offset available; using 5"
		utc_lapse = 5
	############################################################################

	######### Needed since MORECS does full days ###############################
	if ed[3] > 0:
		ed = (DateTime.DateTime(*ed) + DateTime.RelativeDate(days=+1,hour=0)).tuple()[:3]
	############################################################################

	### Initialize hourly data dictionaries
	wx,ceil={},{}
	condition,height={},{}
	pres,dew,vis,tsky,snow={},{},{},{},{}
	for yr in range(sd[0],ed[0]+1):
		wx[yr]={}; ceil[yr]={}
		condition[yr]={}; height[yr]={}
		pres[yr]={}; dew[yr]={}; vis[yr]={}; tsky[yr]={}; snow[yr]={}
		for d in range(1,367):
			wx[yr][d]={}; ceil[yr][d]={}
			condition[yr][d]={}; height[yr][d]={}
			pres[yr][d]={}; dew[yr][d]={}; vis[yr][d]={}; tsky[yr][d]={}
			for h in range(24):
				wx[yr][d][h]=[]
				condition[yr][d][h]=[]; height[yr][d][h]=[]

	### Determine number of 30-day periods ###
	d1=DateTime.Date(sd[0],sd[1],sd[2])
	d2=DateTime.Date(ed[0],ed[1],ed[2])
	num_periods=int(math.floor((d2.absdate-d1.absdate-1)/30.0))+1

	SR_out_dates=[]; SR_out=[]

	### Loop through 30-day periods
	for period in range(num_periods):

#		Create Date List for this period
		date_list=[]
		ds=DateTime.Date(sd[0],sd[1],sd[2])+DateTime.RelativeDate(days=int(30.0*period))
		date_list.append([ds.year,ds.month,ds.day])
		for p_inc in range(1,31):
			dn = ds + DateTime.RelativeDate(days=p_inc)
			if dn <= d2:
				date_list.append([dn.year,dn.month,dn.day])
			else:
				break
		################ For obtaining hourly data via TSVars ###################
		vsd,ved = date_list[0],date_list[-1]
		vsd.append(0)
		ved.append(0)
		pres_list,pres_dates           = getHourlyVars(ICAO, "stpr", stpr0, vsd, ved)
		wx_list,wx_dates               = getHourlyVars(ICAO, "wthr", wthr0, vsd, ved)
		dew_list,dew_dates             = getHourlyVars(ICAO, "dwpt", dwpt0, vsd, ved)
		vis_list,vis_dates             = getHourlyVars(ICAO, "visi", visi0, vsd, ved)
		tsky_list,tsky_dates           = getHourlyVars(ICAO, "tsky", tsky0, vsd, ved)
		ceil_list,ceil_dates           = getHourlyVars(ICAO, "ceil", ceil0, vsd, ved)
		condition_list,condition_dates = getHourlyVars(ICAO, "ccnd", ccnd0, vsd, ved)
		height_list,height_dates       = getHourlyVars(ICAO, "chgt", chgt0, vsd, ved)
		#########################################################################

		############### Specify Unlimited Ceiling ("Unl") as 100000 feet ########
		###############    No longer needed, getting ceiling as float    ########
		#for c in range(len(ceil_list)):
		#	if string.find(ceil_list[c],"Unl")!=-1: ceil_list[c]="1000.0"
		
		############### Obtain Snow Cover via TSVars ############################
		# Obtain snow cover data for this station
		var_min_list=[1,4]
		if snow_station != -1:
			snow_list,snow_dates,valid_snow = \
			solar_routines.GET_DAILY_TSVAR(snow_station,date_list[0],date_list[-1],11,var_min_list)
		else:
			valid_snow = 0
		if valid_snow:
			pass
		else:
			snow_list=[]
			snow_dates=date_list
			for i in range(len(snow_dates)):
				snow_list.append(miss)
		#########################################################################

		################ Convert lists to dictionaries ##########################
		for i in range(len(snow_dates)):
			yr=snow_dates[i][0]; month=snow_dates[i][1];
			day=snow_dates[i][2]
			ds = DateTime.Date(yr,month,day)
			j_day = ds.day_of_year
			snow[yr][j_day]=float(snow_list[i])

		for i in range(len(pres_dates)):
			yr=pres_dates[i][0]; month=pres_dates[i][1];
			day=pres_dates[i][2]; hr=pres_dates[i][3]
			ds = DateTime.Date(yr,month,day)
			j_day = ds.day_of_year
			if pres_list[i] != miss:
				pres[yr][j_day][hr]=pres_list[i]*3387.0/1000.0
			else:
				pres[yr][j_day][hr]=pres_list[i]

			dew[yr][j_day][hr]=dew_list[i]
			vis[yr][j_day][hr]=vis_list[i]
			tsky[yr][j_day][hr]=tsky_list[i]
#			ceil[yr][j_day][hr]=float(ceil_list[i])
			ceil[yr][j_day][hr]=ceil_list[i]
			condition[yr][j_day][hr]=condition_list[i].value()
			height[yr][j_day][hr]=height_list[i].value()
			wx[yr][j_day][hr]=wx_list[i].value()

			if len(condition[yr][j_day][hr])==0:
				condition[yr][j_day][hr]=[-999.0,-999.0,-999.0,-999.0]
			for x in range(4):
				try:
					if condition[yr][j_day][hr][x]<0: condition[yr][j_day][hr][x]=-999.0
				except:
					condition[yr][j_day][hr].append(5)

			if len(height[yr][j_day][hr])==0:
				height[yr][j_day][hr]=[-999.0,-999.0,-999.0,-999.0]
			for x in range(4):
				try:
					if height[yr][j_day][hr][x]<0: 
						height[yr][j_day][hr][x]=-999.0
					else: 
						height[yr][j_day][hr][x]=height[yr][j_day][hr][x]/100.0
				except:
					height[yr][j_day][hr].append(-999.0)
		#########################################################################

		## Re-classify model definitions of sky condition 0-9 instead of 1-128 ##
		cover=condition; cover_dates=condition_dates
		coverage = solar_routines.RECLASS_CCOND(condition,cover,condition_dates,tsky)
		#########################################################################

		### Loop through hourly data
		for d in date_list:
			if d==date_list[-1]: continue
			trans,cl_alb={},{}

			# Check if asos is commissioned at this station for this date (d)
			if (d[0]>asos_date[0]) or \
			   (d[0]==asos_date[0] and d[1]>asos_date[1]) or \
			   (d[0]==asos_date[0] and d[1]==asos_date[1] and d[2]>asos_date[2]):
				asos=1
			else:
				asos=0

			# define julian day
			d_cal = DateTime.Date(d[0],d[1],d[2])
			d_cal_next = d_cal+DateTime.RelativeDate(days=1)
			julian_day=d_cal.day_of_year
			julian_day_next=d_cal_next.day_of_year

			if len(height[d[0]][julian_day][0]) == 0:
				for h in range(24): 
					sr_date = [d[0],d[1],d[2],h]
					SR_out_dates.append(sr_date)
					SR_out.append(miss)
				continue

			# assign snow depth, obtained previously from nearby coop station
			try:
				snodpth=snow[d[0]][julian_day]
			except:
				snodpth=miss

			try:
				snodpth_next=snow[d[0]][julian_day_next]
			except:
				snodpth_next=miss

			# assign snow depth by averaging today"s and next day"s snow depth
			if (snodpth!=miss and snodpth_next!=miss):
				sno=int((snodpth+snodpth_next)/2.0)
			elif (snodpth==miss and snodpth_next!=miss):
				sno=snodpth_next
			elif (snodpth!=miss and snodpth_next==miss):
				sno=snodpth
			else:
				sno=0

			haze_hourly=[]; fog_hourly=[]
			for i in range(24):
				numlyr = 0

				# determine if fog or haze is present
				haze,fog=0,0
				for w in wx[d[0]][julian_day][i]:
					if w in haze_list: haze=1
					if w in fog_list:  fog=1

				haze_hourly.append(haze); fog_hourly.append(fog)

				# If cloud base height is missing, coverage is -BKN, -OVC
				# or -X and ceiling is unlimited, assign a height of 20,000 ft
				for l in range(3):      # loops through lowest 3 cloud layers
					if (height[d[0]][julian_day][i][l]<0.0 and \
					    (coverage[d[0]][julian_day][i][l]==3 or \
					     coverage[d[0]][julian_day][i][l]==4 or \
					     coverage[d[0]][julian_day][i][l]==5 or \
					     coverage[d[0]][julian_day][i][l]==6) and \
					     ceil[d[0]][julian_day][i]==unlimited):
						ceil[d[0]][julian_day][i] = 200.
					if height[d[0]][julian_day][i][l]!=miss: numlyr = numlyr+1

				# If cloud base height is missing, calls the subroutine ceiling to
				# obtain an estimate based on the ceiling height
				for l in range(3):      # loops through lowest 3 cloud layers
					if (height[d[0]][julian_day][i][l]<0.0 and \
					    coverage[d[0]][julian_day][i][l]!=9 and \
					    coverage[d[0]][julian_day][i][l]!=0 and \
					    ceil[d[0]][julian_day][i]!=miss):
						zhight=random.random()
						height_new = solar_routines.CEILING(height[d[0]][julian_day][i],\
								coverage[d[0]][julian_day][i],ceil[d[0]][julian_day][i],zhight)
						height[d[0]][julian_day][i]=height_new
						break

				# Hours with a height given but no coverage will be assigned
				# a coverage of obscured
				if (numlyr==1 and height[d[0]][julian_day][i][0]!=miss and \
				    coverage[d[0]][julian_day][i][0]==9 and vis[d[0]][julian_day][i]<=1):
					coverage[d[0]][julian_day][i][0] = 7

				# call routine to get the cloud transmission values
				trans[i],cl_alb[i] = \
					solar_routines.TRAN(d[0],d[1],asos,haze,fog,\
					vis[d[0]][julian_day][i],height[d[0]][julian_day][i],\
					coverage[d[0]][julian_day][i],ceil[d[0]][julian_day][i],miss)
			
#			sys.stdout.write("%s: Trans:  " % d[0:3])
#			for kle in range(0,24):	
#				sys.stdout.write(" %5.2f" % (trans[kle]))
#			sys.stdout.write("\n")
#			sys.stdout.write("%s Cloud ht:" % d[0:3])
#			for kle in range(0,24):	
#				top = max(height[d[0]][julian_day][kle])
#				sys.stdout.write(" %5d" % (int(top)))
#			sys.stdout.write("\n")

			# call routine to calculate global solar radiation values
			sun_top,sun_clear,sun_cloud,zenith = \
				solar_routines.SOLAR_CALC_H(d[0],d[1],julian_day,\
				pres[d[0]][julian_day],dew[d[0]][julian_day],trans,cl_alb,\
				height[d[0]][julian_day],coverage[d[0]][julian_day],\
				vis[d[0]][julian_day],sno,haze_hourly, fog_hourly,\
				lat,lon,miss,utc_lapse,ICAO,asos)

			for h in range(24):
				sr_date=[d[0],d[1],d[2],h]
				SR_out_dates.append(sr_date)
				if sun_cloud[h] == miss or sun_cloud[h] == -99:
#					print "Missing solar",ICAO,sr_date,trans[h],height[d[0]][julian_day][h],coverage[d[0]][julian_day][h],vis[d[0]][julian_day][h],pres[d[0]][julian_day][h],dew[d[0]][julian_day][h],sno,fog_hourly[h],haze_hourly[h]
#					print "Missing solar",ICAO,sr_date,ceil[d[0]][julian_day][h]
					SR_out.append(miss)
				elif units==1:
					SR_out.append(sun_cloud[h]*23.88)
				elif units==2:
					SR_out.append(sun_cloud[h])
				elif units==3:
					SR_out.append(sun_cloud[h]/0.0036)
				elif units==4:
					SR_out.append(sun_cloud[h]*88.054)
				else:
					pass
	return SR_out_dates, SR_out
