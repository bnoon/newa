import string
import math
import random
from mx import DateTime

from ucanCallMethods import daily_ucan, hourly_ucan, print_exception
from ucanStandardRequests import *
ucan = general_ucan("newa")

def ESTIMATE_MISSING_DATA(alist,m):
	# use data 3 timesteps before and after to estimate missing data
	# modified 4/28/2006 to do estimate for first 3 and last 3, as well -kle
	new_list=[]
	for i in range(len(alist)):
		new_list.append(alist[i])

	for i in range(0,len(alist)):
		if alist[i]==m:
			a1_flag,a2_flag=0,0
			for ii in range(1,4):
				if i-ii >= 0:
					if alist[i-ii]!=m and a1_flag==0:
						a1_flag=1
						a1=alist[i-ii]
				if i+ii < len(alist):
					if alist[i+ii]!=m and a2_flag==0:
						a2_flag=1
						a2=alist[i+ii]
				if a1_flag and a2_flag: break
				
			if a1_flag==1 and a2_flag==0: 
				new_list[i]=a1
			elif a1_flag==0 and a2_flag==1:
				new_list[i]=a2
			elif a1_flag==1 and a2_flag==1:
				new_list[i]=(a1+a2)/2.0
			else:
				new_list[i]=m
	return new_list

#-------------------------------------------------------------------------

def GET_DAILY_TSVAR(id,sdate,edate,var_maj,var_min):
	valid_var=0
	var=[]; var_dates=[]
	try:
		query = ucan.get_query()
		r = query.getUcanFromIdAsSeq(id,'coop')
		if len(r) > 0:
			ucanid = r[-1].ucan_id
		else:
			ucanid = ''
		query.release()
	except:
		query.release()
		ucanid = ''

	data_daily = None
	c = None
	try:
		data_daily = ucan.get_data()
		if ucanid != '':
			c = data_daily.newTSVar(var_maj, 0, ucanid)
		else:
			c = data_daily.newTSVarNativeWithPriority(var_maj,var_min,id)
		
		c.setDateRange((sdate[0],sdate[1],sdate[2]),(edate[0],edate[1],edate[2]))
		var = c.getDataSeqAsFloat()
		var_dates = c.getDateArraySeq()
		c.release()
#		data_daily.release()
		valid_var=1
	except Data.TSVar.UnavailableDateRange:
		if c != None: c.release()
		if data_daily != None:
#			data_daily.release()
			pass
	except:
		i = print_exception()
		for item in i: print item
		print 'get_daily_TSVar -- inside except'
		if c != None: c.release()
#		if data_daily != None:
#			data_daily.release()
#			print 'get_daily_TSVar -- released data'
	return var,var_dates,valid_var

#-------------------------------------------------------------------------

def RECLASS_CCOND(cc,coverage,ccdates,tsky):
	# re-classify cloud conditions from 1-128 to 0-9 for easier coding
	for day in ccdates:
		dc = DateTime.Date(day[0],day[1],day[2])
		j_day=dc.day_of_year
		for i in range(len(cc[day[0]][j_day][day[3]])):
			c=cc[day[0]][j_day][day[3]][i]
			if c==5 or c==7:      		# CLR
				coverage[day[0]][j_day][day[3]][i]=0
			elif c==25 or c==43:  		# FEW or -SCT
				coverage[day[0]][j_day][day[3]][i]=1
			elif c==45 or c==47:  		# SCT
				coverage[day[0]][j_day][day[3]][i]=2
			elif c==63:           		# -BKN
				coverage[day[0]][j_day][day[3]][i]=3
			elif c==65 or c==67:  		# BKN
				coverage[day[0]][j_day][day[3]][i]=4
			elif c==83:           		# -OVC
				coverage[day[0]][j_day][day[3]][i]=5
			elif c==85 or c==87:  		# OVC
				coverage[day[0]][j_day][day[3]][i]=6
			elif c==105:          		# -X
				coverage[day[0]][j_day][day[3]][i]=8
			elif c==125:          		# X
				coverage[day[0]][j_day][day[3]][i]=7
			elif c==128 or c==-999:         # miss
				coverage[day[0]][j_day][day[3]][i]=\
				   RECLASS_TSKY(tsky[day[0]][j_day][day[3]])
			else:
				coverage[day[0]][j_day][day[3]][i]=9
	return coverage

#-------------------------------------------------------------------------

def RECLASS_TSKY(ftsky):
	# re-classify tsky 0.0 to 1.0 to our 0-9 scale
	tsky = int(ftsky*10.)
	if   tsky==0:						# CLR
		coverage=0
	elif tsky>=1 and tsky<=2:			# FEW
		coverage=1
	elif tsky>=3 and tsky<=5:			# SCT
		coverage=2
	elif tsky>=6 and tsky<=9:			# BKN
		coverage=4
	elif tsky==10:						# OVC
		coverage=6
	else:								# missing or other
		coverage=9
	
	return coverage

#-------------------------------------------------------------------------

def TRAN(iyear,imon,asos,haze,fog,vis,ht,cover,ceil,miss):
#	print 'tran routine'
	# iyear:	year
	# imon:		month
	# asos:		1 (yes) or 0 (no)
	# pwx:		present weather
	# vis:		visibility
	# ht:		cloud base height
	# cover:	cloud coverage
	# ceil:		ceiling height

	# **   Subroutine to calculate Ti, the cloud transmissivity without the
	# **   effects of ground-cloud-ground reflection.  The calculation of
	# **   Ti (trans) depends on the single cloud layer transmissivities
	# **   read in from TLAYA (asos) or TLAY (manual).
	# **   Updated 11/97 to account for asos and metar changes. - kle

	import solar_routines

	cl_albedo = 0.0

	# Initialize transmissivity and coverage in each layer and cloud albedo
	if (iyear<1996 or (iyear==1996 and imon<=6)):
		metar = 0
	else:
		metar = 1

	if asos:	# asos version
		t_median,cl_albedo=TLAYA(ht, cover, metar)
	else:		# Manual version
		t_median,cl_albedo=TLAY (ht, cover, metar)

	trans = 1.0
	LAYER = 0

	# Calculates cumulative effect of tranmissivities for all three layers
	# Corresponds to product symbol in Meyers and Dale Eq. 10
	while (((ht[LAYER]!=miss and cover[LAYER]!=9) or \
		   cover[LAYER]==7 or cover[LAYER]==8) and (LAYER<=2)):
		trans = t_median[LAYER]*trans
		LAYER = LAYER + 1

	# Transmissivity = 1 if missing data
	if (ht[0]==miss and ht[1]==miss and ht[2]==miss):
		trans = 1.0

	# Transmissivity = 0.9999 for clear skies
	if asos:
		if cover[0]==0: trans = 0.9999
	else:
		if cover[0]==0: trans = 0.9999

	# Trans is only equal to 1 or missing data
	if trans<1.0:

		# Adjusts transmissivity value when visibility is less than 1 mile
		# but no obscuration is reported
		if (vis<1.0 and cover[0]!=8 and cover[0]!=7):
			trans = trans*0.72	# same asos

		# Adjusts transmissivity if haze is reported with other than clear
		# skies
		elif (cover[0]!=0) and (haze==1):
			if asos:
				trans=trans*0.92
			else:
				trans=trans*0.93
		else:
			pass

		if asos:
			# Trans equals .9999 under clear skies
			if trans==0.9999:
				# Adjusts clear sky transmissivity if visibility is less than
				# 10 miles and no fog or haze is reported
				if (vis<10.0 and (fog==0 and haze==0)):
					trans = 0.96
				# Adjusts clear sky tranmissivity if fog or haze is reported
				elif (vis<1.0 and (fog==1 or haze==1)):
					trans = 0.92
				else:
					pass
			else:
				pass
		else:
			# Trans equals .9999 under clear skies
			if trans==0.9999:
				# Adjusts clear sky transmissivity if visibility is less than
				# 10 miles and no fog or haze is reported
				if (vis<10.0 and (fog==0)):
					trans = 0.98
				# Adjusts clear sky tranmissivity if fog or haze is reported
				elif (vis<1.0 and (fog==1)):
					trans = 0.93
				else:
					pass
			else:
				pass
	else:
		pass

#	if trans==1.00000:
#		o1 = open('./trans_eq_1.txt','w')
#		for ix in range(3):
#			if ix<2:
#				o1.write('%2d %3d ' % (cover[ix],ht[ix]))
#			else:
#				o1.write('%2d %3d %3d %7.5f %1d %1d' % \
#				  (cover[ix],ht[ix],ceil,trans,asos,metar))
#		o1.close()
#	else:
#		pass

	return trans, cl_albedo
	
#-------------------------------------------------------------------------

def TLAY(ht,cover,metar):
	# Define the single layer cloud transmissivities (without 
	# ground-cloud-ground reflection effects) when manual
	# observations are used.
	# ht: 		cloud base height
	# cover: 	cloud coverage
	# metar:	1 (yes) or 0 (no)

	t_median={}
	cl_albedo = 0.0
	for layer in range(3):
		t_median[layer] = 1.00

		# Layers below 2000 feet
		if (ht[layer]<=20 and ht[layer]>0):
			cl_albedo = 0.5
			# OVC = 6; -OVC = 5
			if (cover[layer]==5 or cover[layer]==6):
				t_median[layer] = 0.26
			# BKN = 4; -BKN = 3
			elif (cover[layer]==3 or cover[layer]==4):
				t_median[layer] = 0.63
			# SCT = 2; -SCT = 1
			elif (cover[layer]==2):
				if metar:
					t_median[layer] = 0.82
				else:
					t_median[layer] = 0.84
			elif (cover[layer]==1):
				if metar:
					t_median[layer] = 0.87
				else:
					t_median[layer] = 0.84
			else:
				pass

		# Cloud bases between 2000 and 4000 feet
		elif (ht[layer]>20 and ht[layer]<=40):
			cl_albedo = 0.5
			# OVC = 6; -OVC = 5
			if (cover[layer]==5 or cover[layer]==6):
				t_median[layer]=0.32
			# BKN = 4; -BKN = 3
			elif (cover[layer]==3 or cover[layer]==4):
				t_median[layer] = 0.70
			# SCT = 2; -SCT = 1
			elif (cover[layer]==2):
				if metar:
					t_median[layer] = 0.86
				else:
					t_median[layer] = 0.87
			elif (cover[layer]==1):
				if metar:
					t_median[layer] = 0.89
				else:
					t_median[layer] = 0.87
			else:
				pass

		# Cloud bases between 4000 and 8000 feet
		elif (ht[layer]>40 and ht[layer]<=80):
			cl_albedo = 0.5
			# OVC = 6; -OVC = 5
			if (cover[layer]==5 or cover[layer]==6):
				t_median[layer]=0.35
			# BKN = 4; -BKN = 3
			elif (cover[layer]==3 or cover[layer]==4):
				t_median[layer] = 0.70
			# SCT = 2; -SCT = 1
			elif (cover[layer]==1 or cover[layer]==2):
				t_median[layer] = 0.88
			else:
				pass

		# Cloud bases between 8000 and 12000 feet
		elif (ht[layer]>80 and ht[layer]<=120):
			cl_albedo = 0.5
			# OVC = 6; -OVC = 5
			if (cover[layer]==5 or cover[layer]==6):
				t_median[layer]=0.39
			# BKN = 4; -BKN = 3
			elif (cover[layer]==3 or cover[layer]==4):
				t_median[layer] = 0.63
			# SCT = 2; -SCT = 1
			elif (cover[layer]==2):
				if metar:
					t_median[layer] = 0.87
				else:
					t_median[layer] = 0.85
			elif (cover[layer]==1):
				if metar:
					t_median[layer] = 0.84
				else:
					t_median[layer] = 0.85
			else:
				pass

		# Cloud bases between 12000 and 18000 feet
		elif (ht[layer]>120 and ht[layer]<=180):
			cl_albedo = 0.5
			# OVC = 6; -OVC = 5
			if (cover[layer]==5 or cover[layer]==6):
				t_median[layer]=0.43
			# BKN = 4; -BKN = 3
			elif (cover[layer]==3 or cover[layer]==4):
				t_median[layer] = 0.75
			# SCT = 2; -SCT = 1
			elif (cover[layer]==2):
				if metar:
					t_median[layer] = 0.88
				else:
					t_median[layer] = 0.88
			elif (cover[layer]==1):
				if metar:
					t_median[layer] = 0.88
				else:
					t_median[layer] = 0.88
			else:
				pass

		# Cloud bases greater than 18000 feet
		elif (ht[layer]>180 and ht[layer]<800):
			if cover[layer]==6:
				t_median[layer]=0.73
			elif cover[layer]==5:
				t_median[layer]=0.92
			elif cover[layer]==4:
				t_median[layer]=0.86
			elif cover[layer]==3:
				t_median[layer]=0.96
			elif cover[layer]==2:
				t_median[layer]==0.99
			elif cover[layer]==1:
				if metar:
					t_median[layer] = 0.99
				else:
					t_median[layer] = 0.99
			else:
				pass

		# added following to treat layers with a height of zero as
		# obscured -KLE
		elif ht==0:
			if (cover[layer]>=1 and cover[layer]<=5):
				cover[layer]=8
			elif cover[layer]==6:
				cover[layer]=7
			else:
				pass

		else:
			pass

		if cover[layer]==7:	# OBSCURED (X)
			t_median[layer] = 0.25
		elif cover[layer]==8:	# PARTIALLY OBSCURED (-X)
			t_median[layer] = 0.82
		else:
			pass
	return t_median,cl_albedo

#-------------------------------------------------------------------------

def TLAYA(ht,cover,metar):
#	t_median values updated 6/27/2003
	t_median={}
	cl_albedo = 0.0
	for layer in range(3):
		t_median[layer] = 1.00

# Layers below 2000 feet
		if (ht[layer]>0 and ht[layer]<=20):
			cl_albedo = 0.5
			if cover[layer]==6: 	# OVC
				t_median[layer] = 0.17
			elif cover[layer]==4:	# BKN
				t_median[layer] = 0.552
			elif (cover[layer]==2):	# SCT
				if metar:
					t_median[layer] = 0.844
				else:
					t_median[layer] = 0.883
			elif (cover[layer]==1): # FEW
				if metar:
					t_median[layer] = 0.961
				else:
					t_median[layer] = 0.883
			else:
				pass

# Cloud bases between 2000 and 4000 feet
		elif (ht[layer]>20 and ht[layer]<=40):
			cl_albedo = 0.5
			if cover[layer]==6: 	# OVC
				t_median[layer] = 0.32
			elif cover[layer]==4:	# BKN
				t_median[layer] = 0.685
			elif (cover[layer]==2):	# SCT
				if metar:
					t_median[layer] = 0.868
				else:
					t_median[layer] = 0.901
			elif (cover[layer]==1):	# FEW
				if metar:
					t_median[layer] = 0.967
				else:
					t_median[layer] = 0.901
			else:
				pass

# Cloud bases between 4000 and 8000 feet
		elif (ht[layer]>40 and ht[layer]<=80):
			cl_albedo = 0.5
			if cover[layer]==6: 	# OVC
				t_median[layer] = 0.45
			elif cover[layer]==4:	# BKN
				t_median[layer] = 0.692
			elif (cover[layer]==2):	# SCT
				if metar:
					t_median[layer] = 0.828
				else:
					t_median[layer] = 0.871
			elif (cover[layer]==1):	# FEW
				if metar:
					t_median[layer] = 0.957
				else:
					t_median[layer] = 0.871
			else:
				pass

# Cloud bases between 8000 and 12000 feet
		elif (ht[layer]>80 and ht[layer]<=120):
			cl_albedo = 0.5
			if cover[layer]==6: 	# OVC
				t_median[layer] = 0.44
			elif cover[layer]==4:	# BKN
				t_median[layer] = 0.58
			elif cover[layer]==2:	# SCT
				if metar:
					t_median[layer] = 0.828
				else:
					t_median[layer] = 0.871
			elif cover[layer]==1:	# FEW
				if metar:
					t_median[layer] = 0.957
				else:
					t_median[layer] = 0.871
			else:
				pass

# Cloud bases greater than 12000 feet
		elif (ht[layer]>120 and ht[layer]<800):
			t_median[layer] = 0.9999

# added following to treat layers with a height of zero as obscured -KLE
		elif (ht[layer]==0 and cover[layer]!=0):
			cover[layer] = 7
		else:
			if (cover[layer]!=9 and cover[layer]!=0):
				print 'TLAYA: Ignoring height/coverage of %4d %4d' % \
					(ht[layer],cover[layer])
			else:
				pass

		if cover[layer]==7:	# OBSCURED
			t_median[layer] = 0.30
		else:
			pass
	return t_median,cl_albedo

#-------------------------------------------------------------------------

def CEILING(ht,cover,ht_ceil,zht):
#	print 'ceiling routine'
	# ht:		cloud base height (list of layers)
	# cover:	cloud coverage (list of layers)
	# ht_ceil:	ceiling height
	# zht:	to determine random ceiling height

	kount = 0
	miss = -999

	# Determines the number of layers reporting cloud coverage
	for lyr in range(3):
		if (cover[lyr]==0 or cover[lyr]==9): kount=kount+1

	# No cloud height needed if clear or coverage also missing
	if (kount==3):
		return ht

	# Only one layer of clouds is reported
	elif (kount==2):
		# Ceiling height assigned to BKN or OVC layer
		if (cover[0]>=3 and cover[0]<7):
			ht[0] = ht_ceil
		# Assign a value of 100 ft for any obscured layer -kle 8/27/93
		elif (cover[0]==7 or cover[0]==8):
			ht[0] = 1
		# Random height given to SCT layers
		else:
			if (cover[0]==1 or cover[0]==2):
				ht[0] = int((zht/4.0)*1000)
		return ht

	# Two cloud layers reported
	elif (kount==1):
		#Lowest layer BKN or OVC
		if (cover[0]>=3 and cover[0]<7):
			if ht[0]==miss: ht[0]=ht_ceil
			if ht[1]==miss:
				if ht_ceil<=100:
					ht[1]=ht_ceil+50
				else:
					ht[1]=ht_ceil+100
			else:
				pass
		else:
			# Highest layer BKN or OVC
			if (cover[1]>=3 and cover[1]<7):
				if ht[1]==miss: ht[1]=ht_ceil
				if (cover[0]>0 and ht[0]==miss):
					if ht_ceil<=50: ht[0]=ht_ceil
					if (ht_ceil<=100 and ht_ceil>50): ht[0]=ht_ceil-50
					if ht_ceil>100: ht[0]=ht_ceil-100
				else:
					pass
			else:
				# High -SCT both layers given arbitrary height (1)
				if cover[1]==1:
					if ht[0]==miss: ht[0]=80
					if ht[1]==miss: ht[1]=250
				else:
					# Two SCT layers randomly given height (2)
					# of 2000 and 12000 or 15000 and 25000 feet
					if cover[1]==2:
						if zht<0.5:
							if ht[0]==miss: ht[0]=20
							if ht[1]==miss: ht[1]=120
						else:
							if ht[0]==miss: ht[0]=150
							if ht[1]==miss: ht[1]=250
					else:
						pass

	# If three cloud layers are reported
	elif (kount==0):
		# Lowest layer is BKN (>=3,<7)
		if (cover[0]>=3 and cover[0]<7):
			if ht[0]==miss: ht[0]=ht_ceil
			if ht[1]==miss: ht[1]=ht_ceil+50
			if ht[2]==miss: ht[2]=ht_ceil+100
		else:
			# If second layer is Broken and lowest layer Scattered (>=3,<7)
			if (cover[1]>=3 and cover[1]<7):
				if ht[1]==miss: ht[1]=ht_ceil
				if ht_ceil<=50:
					# Ceiling less than 5000 ft
					if ht[2]==miss: ht[2]=ht_ceil+50
					if ht[0]==miss: ht[0]=ht_ceil
				else:
					# Ceiling between 5000 and 10000 ft
					if (ht_ceil>50 and ht_ceil<=100):
						if ht[2]==miss: ht[2]=ht_ceil+50
						if ht[0]==miss: ht[0]=ht_ceil-50
					# Ceiling over 10000 ft
					else:
						if ht[2]==miss: ht[2]=ht_ceil+100
						if ht[0]==miss: ht[0]=ht_ceil-100
			else:
				# Highest layer Broken or Overcast Lowest 2 layers Scattered (>=3,<7)
				if (cover[2]>=3 and cover[2]<7):
					if ht[2]==miss: ht[2]=ht_ceil
					if ht_ceil<=50:
						# Ceiling less than 5000 feet
						if ht[1]==miss: ht[1]=ht_ceil
						if ht[0]==miss: ht[0]=ht_ceil
					else:
						# Ceiling between 5000 and 10000 feet
						if (ht_ceil>50 and ht_ceil<=100):
							if ht[1]==miss: ht[1]=ht_ceil-30
							if ht[1]==miss: ht[0]=ht_ceil-50
						else:
							# Ceiling greater than 10000 feet but less than 18000 feet
							if (ht_ceil>100 and ht_ceil<=180):
								if ht[1]==miss: ht[1]=ht_ceil-40
								if ht[0]==miss: ht[0]=ht_ceil-80
							else:
								# Ceiling above 18000 ft
								if ht[1]==miss: ht[1]=ht_ceil-100
								if ht[0]==miss: ht[0]=ht_ceil-160
				else:
					# Three Scattered cloud layers reported (1,2)
					if (cover[2]==1 or cover[2]==2):
						if ht[2]==miss: ht[2]=200
						if ht[1]==miss: ht[1]=120
						if ht[0]==miss: ht[0]=80
					else:
						pass

	else:
		pass

	# Partially obscured layer assigned height of 900 ft
	if (cover[0]==8 and ht[0]==miss): ht[0]=9  # modify for partially obscured?

	return ht

#-------------------------------------------------------------------------

def DEWAVG(dp,miss):
	# Subroutine calculates average daily dewpoint.  This value is used if
	# more than three consecutive hourly values are missing

	d_ave,i=0.0,0.0
	for hour in range(24):
		if dp[hour]!=miss:
			d_ave=d_ave+dp[hour]
			i=i+1.0
		else:
			pass

	if i!=0.0:
		d_ave=d_ave/i
	else:
		# Dewpoint = miss if all hours are missing
		d_ave=miss

	return d_ave

#-------------------------------------------------------------------------

def SOLAR_CALC_H(nyear,mon,julian_day,prs,dp,\
	trans,cl_albedo,ht,cover,vis,sno,\
	haze_hourly,fog_hourly,\
	lat,long,miss,utc_lapse,ICAO,asos):

	from solar_routines import DEWAVG, ESTIMATE_MISSING_DATA

	prslist=[]; dplist=[]; translist=[]; calblist=[]
	for i in range(24):
		prslist.append(prs[i])
		dplist.append(dp[i])
		translist.append(trans[i])
		calblist.append(cl_albedo[i])

	new_prs=ESTIMATE_MISSING_DATA(prslist,miss)
	new_dp=ESTIMATE_MISSING_DATA(dplist,miss)
	new_trans=ESTIMATE_MISSING_DATA(translist,1.0)
	new_calb=ESTIMATE_MISSING_DATA(calblist,miss)

	for i in range(24):
		prs[i]=new_prs[i]
		dp[i]=new_dp[i]
		trans[i]=new_trans[i]
		cl_albedo[i]=new_calb[i]

	# Return hourly or daily solar radiation
        # prs:          station pressure
        # dp:           dewpoint
        # trans:        cloud transmissivity
        # cl_albedo:    cloud albedo
        # ht:           cloud base height
        # cover:        cloud coverage
        # sno:          snow depth
        # lat:          latitude of station
        # lon:          longitude of station
        # nyear:        year of model run

	cosZ={}

#       season_lam----AN EMPIRICALLY FOUND CONSTANT FOR LATITUDE AND SEASON
#       M-------------OPTICAL AIR MASS
#       U-------------PRECIPITABLE WATER VAPOR
#       T_A-----------ATTENUATION DUE TO AEROSOLS
#       T_RG----------ATTENUATION BY RAYLEIGH SCATTERING AND GAS ABSORPTION
#       T_W-----------ATTENUATION BY WATER VAPOR
#       albedo--------SURFACE albedo AT THE SITE
#       LAM-----------ECLIPTIC LONGITUDE
#       N-------------NUMBER OF DAYS FROM J2000.0
#       L-------------MEAN LONGITUDE OF SUN, CORRECTED FOR ABERRATION
#       G-------------MEAN ANOMALY OF SUN
#       E-------------OBLIQUITY OF ECLIPTIC
#       Z-------------COSINE OF THE SOLAR ZENITH ANGLE
#       I_O-----------COMPUTED INCOMING SOLAR RADIATION
#       LAT-----------STATION LATITUDE
#       DEC-----------DECLINATION ANGLE OF THE SUN

#       ********* SITE SPECIFIC CONSTANTS ARE ASSIGNED ********

	sun_clear,sun_cloud,sun_top={},{},{}
	for i in range(24):
		sun_top[i] = 0
		sun_clear[i] = 0
		sun_cloud[i] = 0

	t1 = 0.0
	t2 = 0.0

	#  **  Assign values to Season_lam, an empirical constant (Eq. 7 Meyers and
	#  **  Dale), another empirical constant (Eq. 8 Meyers and Dale)
	#  **  x_value changes in 1992 to account for the effects of the eruption
	#  **  of Mt. Pinatubo

	if ((julian_day>=1 and julian_day<60) or julian_day>=335):
		if (lat>20 and lat<=30): season_lam=3.60
		if (lat>=30 and lat<=40): season_lam=3.04
		if (lat>40 and lat<50): season_lam=2.70
		if (lat>50 and lat<60): season_lam=2.52
	elif (julian_day>=60 and julian_day<152):
		if (lat>20 and lat<=30): season_lam=3.00
		if (lat>=30 and lat<=40): season_lam=3.11
		if (lat>40 and lat<50): season_lam=2.95  
		if (lat>50 and lat<60): season_lam=3.07
	elif (julian_day>=152 and julian_day<244):
		if (lat>20 and lat<=30): season_lam=2.98
		if (lat>=30 and lat<=40): season_lam=2.92
		if (lat>40 and lat<50): season_lam=2.77  
		if (lat>50 and lat<60): season_lam=2.67
	elif (julian_day>=244 and julian_day<335):
		if (lat>20 and lat<=30): season_lam=2.93
		if (lat>=30 and lat<=40): season_lam=2.94
		if (lat>40 and lat<50): season_lam=2.71  
		if (lat>50 and lat<60): season_lam=2.93
	else:
		pass

	# ********* THESE EQUATION INVOLVE DETERMINING THE SOLAR ANGLE *******
	# **    See Walraven 1978:  Calculating the position of the sun Sol. Energy,
	# **    20, 193

	intyr = int(4.0*(int((float(nyear))/4.0)))
	lp = 0
	if intyr==nyear: lp = 1

	if mon<=2:
		doy = julian_day - lp
	else:
		doy = julian_day

	delta = float(nyear) - 1980.0
	leap = int(delta/4.0)

	#       ********* THIS OUTER LOOP INCREMENTS THE TIME BY SIX MINUTES *******
	#       ********* AND THEN DOES RADIATION CALCULATIONS *********

	for hr in range(230):
		ahr = (float(hr)/10.)

		if math.floor(ahr)==ahr:
			ohour = int(math.floor(ahr))
		else:
			ohour = int(math.floor(ahr))+1

		time = delta*365.0 + leap + doy - 1.0 + (ahr/24.0)
		if delta==(leap*4.0): time=time-1.0
		if (delta<0 and delta!=(leap*4.0)): time=time-1.0

		theta = 2.0*math.pi*time / 365.25
		g = -0.031271 - (time * 4.53963e-07) + theta
		L = 4.900968 + (time * 3.67474e-07) + (math.sin(g) * (0.033434 - \
			2.3e-09 * time)) + (math.sin(2*g) * 0.000349) + theta
		eps = 23.440 - (time * 3.56e-07)
		ST = (6.720165 + 24.0 * (time / 365.25 - delta) + \
			0.000001411 * time) * (15.0 * math.pi / 180.0)

		if ST>(2*math.pi): ST=ST-(2*math.pi)

		# bnb: -180 < long < +180
		locst = ST + (long * math.pi/180.0) + 1.0027379 * (ahr + utc_lapse) \
			* (15.0 * math.pi /180.0)

		if locst>(2*math.pi): locst=locst-(2*math.pi)

		sinL = math.sin(L)
		X = math.cos(eps * math.pi /180.0) * sinL
		Y = math.cos(L)

		rasc = math.atan2(X,Y)

		if rasc<0.0: rasc=rasc+(2.0*math.pi)

		HA = rasc - locst
		sindec = math.sin(eps * math.pi /180.0) * sinL
		dec = math.asin(sindec)

		cosZ[hr] = ( math.sin(lat*math.pi/180.0) * sindec) + \
			(math.cos(lat*math.pi/180.0) * math.cos(math.asin(sindec)) * math.cos(HA))

		if (cosZ[hr]>0.0001 and t1<1):
			t1 = ahr
		elif (cosZ[hr]<0.0001 and t2<1 and ahr>12):
			t2 = ahr
		else:
			pass

		Z=math.acos(cosZ[hr])*180.0/math.pi
		I_O = (1367.0*(1+(.034*(math.cos(2.0*math.pi* \
			(((doy)-1.0)/365.0))))))

		#       ******* WHEN THE SOLAR ANGLE IS ABOVE THE HORIZON ********
		#       ******* WE START OUR CALCULATIONS ********

		if (I_O*cosZ[hr]>0):

			#       ******* CHECK FOR VALID OBS. DATA. IF IT ISN'T THERE ********
			#       ******* SET MODEL OUTPUT TO MISSING		  ********

			if prs[ohour]==miss:
				sun_top[ohour] = -99.00
				sun_clear[ohour] = -99.00
				sun_cloud[ohour] = -99.00
				continue
			else:
				pass

			dp_ave = DEWAVG(dp,miss)
			if dp_ave!=miss:
				dp[ohour] = dp_ave
			else:
				sun_top[ohour] = -99.00
				sun_clear[ohour] = -99.00
				sun_cloud[ohour] = -99.00
				continue

			if trans[ohour]==1.0:
				sun_top[ohour] = -99.00
				sun_clear[ohour] = -99.00
				sun_cloud[ohour] = -99.00
				continue
			else:
				pass

			if cl_albedo[ohour]==miss:
				sun_top[ohour] = -99.00
				sun_clear[ohour] = -99.00
				sun_cloud[ohour] = -99.00
				continue
			else:
				pass

			#       ****** CALCULATE SOLAR RADIATION FOR A SIX MINUTE PERIOD ********
			#       ****** USING HOURLY OBS. INFORMATION *********

			# Equation for optical air mass Meyers and Dale Eq. 5
			M = 35.0*(((1224.0*(cosZ[hr]**2))+1.0)**(-0.5))

			# Equation for precipitable water content Meyers and Dale Eq. 7
			U=math.exp(0.1133-math.log(season_lam+1.0)+.0393*dp[ohour])

			# Cloud transmissivity
			T_C=trans[ohour]

			# Equation for Rayleigh scattering and permanent gas absorption
			# Meyers and Dale Eq. 4
			T_RG = 1.021-.084*((M*(949*prs[ohour]*(10**(-5)) + .051))**(.5))

			# Absorption due to water vapor Meyers and Dale Eq. 6
			T_W = 1.0 - .077*((U*M)**(.3))

			# Equation for aerosol absorption Meyers and Dale Eq. 8
			if (asos):
				x_coeff=0.84				 # changed 6/27/2003
			else:
				x_coeff=0.870 + 0.00096*Z    # regression - running means
			T_A = (x_coeff)**M

			# compute albedo term for ground-cloud-ground reflection,
			# using defined surface and cloud albedos.
			# If snow dpth is less than 1 inch surface albedo = 0.20, otherwise
			# surface albedo equals 0.65
			if sno<=1:
				albedo = 1.0/(1.0 - (0.2*cl_albedo[ohour]))
			else:
				albedo = 1.0/(1.0 - (0.65*cl_albedo[ohour]))

			sun_top[ohour] = sun_top[ohour] + I_O*cosZ[hr]*0.1

			# Calculation of daily solar radiation IGNORING clouds.  Factor of .1
			# used to account for 6 minute rather than 1 hour integration
			sun_clear[ohour] = sun_clear[ohour] + \
					(I_O*cosZ[hr]*T_RG*T_W*T_A)*0.1

			# Calculation of daily solar radiation INCLUDING clouds.  Factor of .1
			# used to account for 6 minute rather than 1 hour integration
			sun_cloud[ohour] = sun_cloud[ohour] + \
				(I_O*cosZ[hr]*T_RG*T_W*T_A*albedo*T_C)*0.1
		else:
			pass

	# *****CONVERTS Watts/m^2  TO MJ/m^2*day *******
	I_O=I_O*0.0036
	zenith={}
	for i in range(24):
		if sun_cloud[i]!=-99.00: sun_cloud[i]=sun_cloud[i]*0.0036
		if sun_clear[i]!=-99.00: sun_clear[i]=sun_clear[i]*0.0036
		if sun_top[i]!=-99.00: 
			sun_top[i]=sun_top[i]*0.0036
			zenith[i]=math.acos(sun_top[i]/I_O)*180.0/math.pi
		else:
			zenith[i] = -99.

	return sun_top, sun_clear, sun_cloud, zenith
