import sys
from math import log, exp

def etsoil_calc (gtype,soil_type,month,day,hour,tmp,dewpt,wind,rain,sun_cloud,tsky,snow,daily_ppt,
				loc_constants,sc_status,sc_constants):

#	***** variable definition *****

#	gtype ------- a number representing a certain kind of crop
#		1=soil               8=upland 
#		2=alfalfa            9=open water (pan evap)
#		3=potatoes          10=winter wheat
#		4=coniferous        11=corn (silage)
#		5=orchards          12=corn (grain)
#		6=deciduous         13=PET (grass)
#		7=grasslands					
#	soil_type --- soil water holding capacity
#		1=low
#		2=medium 
#		3=high
#	month, day -- month and day of interest
#	hour -------- hour in local standard time
#	tmp --------- hourly temperature (F)
#	dewpt ------- hourly dewpoint (F)
#	wind -------- hourly windspeed (mph)
#	rain -------- hourly precipitation total (inches) (default=5.0)
#	sun_cloud --- incoming solar radiation (langleys)
#	tsky -------- percent cloud cover (default=0.5)
#	snow -------- depth of snow on ground (inches; default=0)
#	daily_ppt --- precipitation is daily total instead of hourly

#	Following are in sc_constants:
#	 h_max ------- maximun crop height before harvest
#	 h_min ------- mininum crop height after emergence
#	 d_e,d_f,d_h - days of crop (e)mergence, (f)ull growth, and (h)arvesting
#	 cp_albedo --- albedo of fully grow crop
#	 max_leaf ---- maximum leaf area index
#	 surf_res ---- surface resistance for dense green crops
#	 water_cap --- available water capacity for particular surfaces
#	 soil_max ----
#	 crop_max ----

#	Following are in sc_status:
#	 crop_x ------ upper 40% of available water during crop season
#	 crop_y ------ lower 60% of available water during crop season
#	 soil_x ------ upper 60% of available water without crop planted
#	 soil_y ------ lower 40% of available water without crop planted
#	 gtotal ------ total daytime heat flux accumulator (needed for nighttime g)
#	 interception- amount of water on leaves

#	Following are in loc_status:
#	 lat -------- latitude in degrees
#	 long ------- longitude in degrees
#	 gmtoff ----- offset from UCT (hours; EST=5)

#	hr_evap ----- inches of evaporation per hour
#	r_n --------- net radiation (wm-2) (+ve downwards)
#	g   --------- soil heat flux (wm-2) (+ve downwards)
#	r_s --------- bulk surface resistance (s m-1)
#	r_a --------- bulk aerodynamic resistance (s m-1)
#	leaf -------- leaf area of the crop for the specific day


#	*****  determine day of year (julian_day). don't care if it's leap year.
	ndays = [0,31,59,90,120,151,181,212,243,273,304,334]
	julian_day = ndays[month-1] + day
	
#	***** sometimes this comes in as a negative number. must be positive for this routine. *****
	if loc_constants['long'] < 0.: loc_constants['long'] = loc_constants['long'] * -1.
	
#	*****  determine time of sunrise and sunset and number of hours of daylight 
	sunrise,sunset = daylength (julian_day, loc_constants)
	dayhours = round(sunset,0) - round(sunrise,0)
	
#	*****  is it night time?
	if hour > round(sunrise,0) and hour <= round(sunset,0):
		nighttime = 0
	else:
		nighttime = 1
		
#	***** change missing to default values when possible *****
	rain, snow, tsky, wind, sun_cloud = chk_default (rain, snow, tsky, wind, sun_cloud, hour, sunrise, sunset)
		
#	***** convert to correct units for calculations *****
	tmp, dewpt, sun_cloud, wind, rain = changeunits (tmp, dewpt, sun_cloud, wind, rain)

#	***** special d_e, d_f, and d_h for alfalfa and wheat *****
	special_dates (gtype, julian_day, sc_constants)

#	***** determine the leaf size for a given surface and julian_day *****
	leaf = leafsize (gtype, month, julian_day, sc_constants)
	
#	sys.stdout.write ('month,day,hour,nighttime: %d %d %d %d;' % (month,day,hour,nighttime))
	
#	***** can't do calculations if any of these are missing *****
	if tmp <= -99. or dewpt <= -99 or sun_cloud <= -99:
		hr_evap = -999.
		dew = 0.0
	else:
#		***** calculate net radiation at the surface *****
		r_n = radiation (tmp, dewpt, tsky, sun_cloud, snow, gtype,leaf, soil_type, sc_status, sc_constants)
	
#		***** calculate how much surface radiation is turned into heat flux into the soil *****
		g = calculateg (gtype, leaf, r_n, nighttime, dayhours, month, sc_status, hour, sunrise)
	
#		***** calculate aerodynamic resistance *****
		r_a = aerores (gtype, julian_day, wind, sc_constants)

#		***** calculate the surface resistance *****
		r_s = rscalc (gtype, month, julian_day, leaf, tmp, dewpt, snow, nighttime, sc_constants, sc_status)  
	
#		***** calculate the amount of evaporation (mm) that takes    *****
#		***** place. page 15  eq. 4.13.  update interception.    	 *****
		hr_evap, dew = evapamt (r_n, g, tmp, dewpt, r_a, r_s, gtype, nighttime, sc_status)

#	sys.stdout.write(' hr_evap: %f\n' % hr_evap)

#	*** calculate interception of rain+dew by leaves *****
#	*** interception is updated in rainfall. add_inter is interception added this hour *****
	rain = rain + dew
	add_inter = rainfall (rain, leaf, month, julian_day, gtype, daily_ppt, sc_constants, sc_status)
	
#	**** account for runoff *****
	runo = runocalc (rain, dew, gtype, add_inter, sc_constants, sc_status)
	
#	*** water added to soil (condensate no longer considered) *****
	if hr_evap == -999:
		addition = rain - add_inter - runo
	else:
		addition = rain - hr_evap - add_inter - runo
	
#	***** make adjustments to the available water levels in the soil *****
	cant_evap = adjust_soilmoist (gtype, julian_day, addition, sc_constants, sc_status)
	
#	***** total evaporation (convert to inches) *****
	if hr_evap == -999:
		evapo = -999.
	else:
		evapo = (hr_evap + cant_evap) / 25.400
	
#	print "%d\t%4.4f\t%4.4f\t%4.4f\t%4.4f" % (hour,
#		hr_evap/25.400,(rain-dew)/25.400,dew/25.400,sc_status['interception']/25.400)

	return (evapo)

#---------------------------------------------------------------------------
def add_to_layer (deficit, addition, max_val, current_val):

	if deficit >= addition:

#		***   If deficit more than addition, then the soil layer can hold the entire
#		***   amount of water that needs to be added.

		current_val = current_val + addition
		addition = 0.0
		done = 1 

	else:
	
#		***  If the deficit is less than addition, the soil level is set to the
#		***  max amount of water it can hold and addition is reduced by the 
#		***  appropriate amount. 

		current_val = max_val
		addition = addition - deficit
		done = 0

	return (addition, current_val, done)
	
#---------------------------------------------------------------------------
def adjust (addition,x_max,y_max,sc_constants,sc_status):
	
	soil_max = sc_constants['soil_max']
	crop_max = sc_constants['crop_max']
	h2o_cap = sc_constants['water_cap']
	crop_x = sc_status['crop_x']
	crop_y = sc_status['crop_y']
	soil_x = sc_status['soil_x']
	soil_y = sc_status['soil_y']

	runoff = 0.0
	cant_evap = 0.0

#	***   amount of water needed to bring each reservoir to capacity

	def_x_soil = (0.40 * soil_max) - soil_x
	def_y_soil = (0.60 * soil_max) - soil_y
	def_x_crop = (0.40 * crop_max) - crop_x
	def_y_crop = (0.60 * crop_max) - crop_y

#	***   addition is positive so water needs to be added to soil

	if addition >= 0:
#		***   addition water fills reservoirs in set order: x_soil, x_crop,y_soil,
#		***   y_crop.  when a given layer is filled to capacity, any additional water
#		***   is added to the next layer.  if all reservoirs are filled any remaining
#		***   water is assumed to be lost as runoff.

		if def_x_soil > 0:
			addition, sc_status['soil_x'], done = add_to_layer(def_x_soil,addition,0.40*soil_max,soil_x)
			if done == 1: return (runoff, cant_evap)

		if def_x_crop > 0:
			addition, sc_status['crop_x'], done = add_to_layer(def_x_crop,addition,0.40*crop_max,crop_x)
			if done == 1: return (runoff, cant_evap)

		if def_y_soil > 0:
			addition, sc_status['soil_y'], done = add_to_layer(def_y_soil,addition,0.60*soil_max,soil_y)
			if done == 1: return (runoff, cant_evap)

		if def_y_crop > 0:
			addition, sc_status['crop_y'], done = add_to_layer(def_y_crop,addition,0.60*crop_max,crop_y)
			if done == 1: return (runoff, cant_evap)

		runoff = addition
		
		return (runoff, cant_evap)


#	***   addition is negative so water needs to be removed from soil

	elif addition < 0:
#		***   water is removed from reservoirs in set order: x_soil, x_crop,y_soil,
#		***   y_crop.  when all the available water in a given layer is gone, any 
#		***   additional water that still needs to be removed is
#		***   taken from the next layer.  if all reservoirs are "dry" any additional
#		***   evaporation is impossible (no water to evaporate) so the amount of
#		***   calculated evaporation needs to be reduced. avail is the amount of
#		***   unavailable water in each layer.
		
		if soil_x > 0:
			avail = 0.0
			addition, sc_status['soil_x'], done = sub_from_layer(addition,soil_x,avail)
			if done == 1: return (runoff, cant_evap)

		if crop_x > 0:
			avail = x_max
			addition, sc_status['crop_x'], done = sub_from_layer(addition,crop_x,avail)
			if done == 1: return (runoff, cant_evap)

		if soil_y > 0:
			avail = 0.0
			addition, sc_status['soil_y'], done = sub_from_layer(addition,soil_y,avail)
			if done == 1: return (runoff, cant_evap)

		if crop_y > 0:
			avail = y_max
			addition, sc_status['crop_y'], done = sub_from_layer(addition,crop_y,avail)
			if done == 1: return (runoff, cant_evap)

		cant_evap = addition
	
	return (runoff, cant_evap)

#---------------------------------------------------------------------------
def adjust_soilmoist (gtype, julian_day, addition, sc_constants, sc_status):

#	this program calculates the added mosture to the soil in the case of rain
#	or subtracted in the case of evaporation. pg 32 outlines this procedure.

#	***  adjust soil moisture for winter wheat
	if gtype == 10:
		x_max,y_max = wintercropsadd (julian_day,sc_constants)
		runoff, cant_evap = adjust (addition,x_max,y_max,sc_constants,sc_status)

#	***  surface gtypes that don't vary anually (bare soil, conifers, deciduous trees)
 	elif gtype == 1 or gtype == 4 or gtype == 6:
		x_max = 0.0
		y_max = 0.0
		runoff, cant_evap = adjust (addition,x_max,y_max,sc_constants,sc_status)

#	*** only et is desired (not tracking soil moisture)
	elif gtype == 9 or gtype == 13:
		runoff = 0.0
		cant_evap = 0.0

#	***  adjust soil moisture for all other crop gtypes
	else: 
 		x_max,y_max = seasonaladd (gtype,julian_day,sc_constants)
		runoff, cant_evap = adjust (addition,x_max,y_max,sc_constants,sc_status)
		
	return (cant_evap)

#---------------------------------------------------------------------------
def adjustalbedo (gtype, cp_albedo, leaf, stype, sc_status):
#	make adjustment to cp_albedo based on leaf size and soil wetness 

	wet_soil_albedo = [0.05, 0.10, 0.15]
	dry_soil_albedo = [0.10, 0.20, 0.30]
		
#	soil albedo based on wetness
	if sc_status['soil_x']+sc_status['soil_y'] > 0.0: 
		s_alb = wet_soil_albedo[stype-1]
	else:
		s_alb = dry_soil_albedo[stype-1]

	if gtype == 1:
		adj_cp_albedo = s_alb
	elif leaf <= 4.0:
		adj_cp_albedo = s_alb + 0.25*(cp_albedo-s_alb)*leaf
	else:
		adj_cp_albedo = cp_albedo
		
	return (adj_cp_albedo)
	
#---------------------------------------------------------------------------
def adjustmaxlinear (max,julian_day,start,end,decrease):

#	this subroutine makes a linear calculation of the amount of unavailable
#	  water between two dates. linear decrease if decrease=1; otherwise
#	  linear increase. 

	numdays = end - start
	day_of_period = julian_day - start

	if decrease:
		percent = 1.0 - (float(day_of_period) / float(numdays))
	else:
		percent = float(day_of_period) / float(numdays)

	x_max = 0.4*(percent*max)
	y_max = 0.6*(percent*max)

	return (x_max,y_max)
	
#---------------------------------------------------------------------------
def aerores (gtype,day,wind,sc_constants):

#	***** aerodynamic resistance for heat and water vapor transfer *****
#	*****  p. 21  eq. 4.39 *****

	h_min = sc_constants['h_min']
	h_max = sc_constants['h_max']
	d_e = sc_constants['d_e']
	d_f = sc_constants['d_f']
	d_h = sc_constants['d_h']

#	***** wind must be greater than zero *****
	if wind == 0: wind = 0.5

	if gtype != 4 and gtype != 6:
	
#		***** this equation is used for crops with effective heights below *****
#		***** two meters.  p. 20  eq. 4.36                                 *****

#		***** determine effective heights of sufaces  *****
#		*****  z_o is roughness length of the surface *****

		if h_max == h_min:
			z_o = 0.1 * h_max
		else:
			if day < d_e or day > d_h:
#				*****  before emergence or after harvest
				z_o = 0.1 * h_min
			elif day >= d_e and day <= d_f:
#				*****  between emergence and full leaf
				z_o = 0.1 * (h_min+(h_max-h_min)*float(day-d_e)/float(d_f-d_e))
			elif day > d_f and day <= d_h:
#				*****  during full leaf
				z_o = 0.1 * h_max

		aero_res = (6.25/wind)*log(10.0/z_o)*log(6.0/z_o)

	elif gtype == 4:

#		***** use this equation for tall coniferous trees *****

		aero_res = 56.3/(0.6 * wind)

	elif gtype == 6:

#		***** a special form of the aerodynamic resistance equation must *****
#		***** be used for deciduous trees due to their change in         *****
#		***** effective height, from .15 meters to 10 meters (h_max).    *****

		if day < d_e or day >= d_h+40:
#			***  trees have no leaves
			h_min = .15
			z_o = .1 * h_min

		elif day >= d_e and day < d_f:
#			***  trees going from bud to full leaf
			h_min = 2.0
			z_o = 0.1 *(h_min+((h_max-h_min)*float(day-d_e) / float(d_f-d_e)))

		elif day >= d_f and day <= d_h:
#			***  trees in full leaf
			z_o = .1 * h_max
			
		elif day > d_h and day < d_h+40:
#			***  leaves are falling
			h_min = .15
			z_o = .1 *( h_min+((h_max-h_min)*float(d_h+40-day)/40.0))
			
#		use equation we think is for greater roughness surfaces -kle 7/2002
		aero_res = (6.25/wind)*log(10.0/z_o)*log(50.0/z_o)

	return (aero_res)
	
#---------------------------------------------------------------------------
def calculateg (gtype, leaf, r_n, nighttime, dayhours, month, sc_status, hour, sunrise):

#	calculate how much surface radiation is turned into heat flux into the soil                   

	p = [-137.0,-75.0,30.0,167.0,236.0,252.0,213.0,69.0,-85.0,-206.0,-256.0,-206.0]
	
	if hour == round(sunrise,0)+1:
		sc_status['gtotal'] = 0.0

	if gtype == 9:
		g = 0.0
	
	elif nighttime:
		g = ( p[month-1] - sc_status['gtotal'] ) / (24.0 - dayhours)

	else:
		if gtype == 1:
			g = 0.3 * r_n
		elif gtype == 7 or gtype == 13:
			g = 0.2 * r_n
		else:
			g = (0.3 - (0.03*leaf)) * r_n 
			
		sc_status['gtotal'] = sc_status['gtotal'] + g
		
	return (g)

#---------------------------------------------------------------------------
def changeunits (tmp, dew, solar, wind, rain):

	try:
#		convert temperatures from fahrenheit to celsius
		if tmp > -90.0:
			tmp = (tmp-32.0) * (5.0/9.0) 
		else:
			tmp = -99.0
		if dew > -90.0:
			dew = (dew-32.0) * (5.0/9.0)
		else:
			dew = -99.0
	
#		convert solar rad from langleys to w/m2
		if solar >= 0.0:
			solar = solar*41860.0
		else:
			solar = -99.0

#		convert wind speed from mph to m/s
		if wind >= 0.0:
			wind = wind * 0.44704
		else:
			wind = -99.0
	
#		convert rainfall to mm
		if rain >= 0.00:
			rain = rain * 25.400
		else:
			rain = -99.0
	except:
		print 'ERROR changing units:',tmp,dew,solar,wind,rain
	
	return(tmp,dew,solar,wind, rain)
	
#---------------------------------------------------------------------------
def chk_default (rain, snow, tsky, wind, sun_cloud, hour, sunrise, sunset):

#	change missing to default values when possible
	if rain < 0: rain = 0.00
	if snow < 0: snow = 0
	if tsky < 0: tsky = 0.5
	if wind < 0: wind = 5.0
	if (hour <= sunrise or hour > int(sunset)+1) and sun_cloud != 0:
		print 'CHK_DEFAULT: Hour=',hour,'sr/ss',sunrise,sunset,'; solar rad of',sun_cloud,'set to zero.'
		sun_cloud = 0.0
		
	return (rain, snow, tsky, wind, sun_cloud)
	
#---------------------------------------------------------------------------
def daylength (jdate, loc_constants):

#	jdate is the julian day
#	gmtoff is the offset of local time from uct (positive value)
#	latitude and longitude are input in decimal degrees
#	t1 and t2 are returned as times of sunrise and sunset

	from math import pi, sin, cos, tan, asin, acos, atan
	
	gmtoff = loc_constants['gmtoff']
	lat = loc_constants['lat']
	long = loc_constants['long']

	dr = pi/180.
	uct_est_off = -abs(gmtoff)

#	***** approx time of phenomenon in days since 0 jan 0 hrs ut *****

	t = jdate + (6.0 + long/15.0) / 24.0

#	***** mean anomaly *****

	m = 0.9856 * t - 3.289

#	***** ecliptic longitude *****

	l = (m+1.916*sin(m*dr)+0.02*sin(2.0*m*dr)+282.634) % 360.0
	if l == 180.0:
		l = 179.9999999
	elif l == 270.0:
		l = 269.9999999
		
#	***** right ascension *****

	ra = (atan(0.91746*tan(l*dr)))/dr
	
#	***** put 'ra' and 'l' into the same quadrant *****

	if l > 90.0 and l < 180.0:
		ra = 90.0 - abs(ra) + 90.0
	elif l >= 180.0 and l < 270.0:
		ra = abs(ra) + 180.0
	elif l  > 270.0:
		ra = 90.0 - abs(ra) + 270.0

#	***** declination angle *****

	ra = ra/15.0
	d = (asin(0.39782*sin(l*dr)))/dr
	
#	***** check for a rising and setting event *****

	h = (-0.01415439-sin(d*dr)*sin(lat*dr))/(cos(d*dr)*cos(lat*dr))
	
	if h <= 1.0 and h >= -1.0:
		h = acos(h)/dr
	elif h > 1.0:
		t1 = 9999
		t2 = 9999
		print 'the sun never rises'
		return (t1, t2)
	elif h < -1.0:
		t1 = 9999
		t2 = 9999
		print 'the sun never sets'
		return (t1, t2)

#	***** calculate sunrise and sunset in decimal form ***** 

	t1 = ((360.0 - h)/15.0 + ra - 0.06571*t - 6.622 + long/15.0) % 24.0
	t2 = (h/15.0           + ra - 0.06571*t - 6.622 + long/15.0) % 24.0
	
#	***** adjust times from uct to est *****

	t1 = t1 + uct_est_off
	if t1 < 0.0:
		t1 = 24.0 + t1
	t2 = t2 + uct_est_off
	if t2 < 0.0:
		t2 = 24.0 + t2

#	***** hours of daylight *****
#	daylight = t2-t1

	return (t1, t2)
	
#---------------------------------------------------------------------------
def evapamt (r_n, g, tmp, dewpt, r_a, r_s, gtype, nighttime, sc_status):

	r_sz = 0.0	#no surface resistance

#	***** no interception by open water *****
	if gtype == 9:
		sc_status['interception'] = 0.0  
		
#	***** initialize as no dew
	dew = 0.0        
	
#	***** this equation takes all the variables from above and   *****
#	***** and calculates the amount of evaporation (mm) that     *****
#	***** takes place. page 15  eq. 4.13.  if intercepted water  *****
#	***** exists on the leaf surfaces the surface resistance is  *****
#	***** 0 until this water evaporates.			             *****

	if sc_status['interception'] > 0:
#		***  intecepted water exists on leaves, so no surface resistance
		e1 = evapcalc (r_n, g, tmp, dewpt, r_a, r_sz)
		
		if nighttime:
			if e1 >= 0:
				dew = 0.0
			else:
#				**** negative evaporation means dew has formed	
				dew = -(e1)
				e1 = 0

		if e1 < sc_status['interception']:
#			*** intercepted water still exists, so no evap from soil and
#			*** interception reduced by amount of evaporation.
			hr_evap = 0.0 
			sc_status['interception'] = sc_status['interception']-e1
			
		else:
# 			*** evap is total amount of water evaporated - amount
# 			*** of original intercepted water. intercepted amount now zero.
			hr_evap = e1-sc_status['interception']
			sc_status['interception'] = 0.0

	else:

#		***   no inteception was present so value of et can be calculated.
		hr_evap = evapcalc (r_n, g, tmp, dewpt, r_a, r_s)

		if nighttime:
			if hr_evap < 0:
	
#				***   if this condition is met it means that dew has formed, so redo et 
#				***   calculation with no surface resistance.	
				hr_evap = evapcalc (r_n, g, tmp, dewpt, r_a, r_sz)

 				if hr_evap < 0:
					dew = -(hr_evap)
					hr_evap = 0.0
				else:
					dew = 0.0
			else:
				dew = 0.0	

#	print "%9.1f\t%11.1f\t%d\t%d\t%5.1f\t%5.1f\t%d\t%4.3f\t%4.3f\t%4.3f" % (r_n,g,tmp,dewpt,
#		r_a,r_s,nighttime,hr_evap/25.400,dew/25.400,sc_status['interception']/25.400)

	return (hr_evap, dew)

#---------------------------------------------------------------------------
def evapcalc (r_n, g, tmp, dew, r_a, r_s):

#	constants
#	latent heat of vaporization (j kg-1)
	lamdav = 2465000.0
#	latent heat of sublimation (j kg-1)
	lamdas = 2799000.0
#	psychromatic constant (for temps in c and pressure in mb)
	gamma = 0.66

#	air density (kg m-3) - should be a function of temp and pressure
#	row = 1.25
#	specific heat of air at constant pressure (j kg-1)
#	c_p = 1005.0
#	rcp = row*c_p
	rcp = 1256.25

#	original - some constant that should vary with season (average used here)
#	b = 0.525
#	tested - calculate b more precisely -kle 7/3/03
#	omega = 0.0000000567
#	em = 0.95
#	b = (4.*em*omega*((273.1+tmp)**3.)) 
#	finally - decided we didn't need it -kle 7/7/03
	b = 0.
	
#	derived rate of change of saturated vapor pressure with temperature (mb `c-1)
	delta = (exp(21.255-5304./(tmp+273.))) * (5304./((tmp+273.)**2.))
#	vapor pressure of temperature
	v_tmp = 6.108*exp(17.27*tmp/(tmp+273.3))
#	vapor pressure of dewpoint
	v_dew = 6.108*exp(17.27*dew/(dew+273.3))

#	calculation	
#	e=(delta*(r_n-g)+rcp*(v_tmp-v_dew)*(1.0+(b*r_a)/rcp)/r_a)/(delta+gamma*(1.0+r_s/r_a)*(1.0+(b*r_a)/rcp))
	e=(delta*(r_n-g)+rcp*(v_tmp-v_dew)/r_a) / (delta+gamma*(1.0+r_s/r_a))
	
#	sys.stdout.write(' b,g,r_n: %f %f %f;' % (b,g,r_n))
	
	if tmp > -1.1:
		evap = e/lamdav
	else:
		evap = e/lamdas
	
	return (evap)
	
#---------------------------------------------------------------------------
def getcropconst (gtype,soil_type,sc_constants):

	soil_data_dict = {
	'high': (
		(0.05, 0.05, 0.00, 0.00, 366.00, 0.15, 0.00, 100.00, 25.00),
		(0.60, 0.05, 119.00, 250.00, 250.00, 0.25, 5.00, 40.00, 175.00),
		(0.60, 0.05, 95.00, 176.00, 236.00, 0.25, 4.00, 40.00, 112.50),
		(10.00, 10.00, 0.00, 0.00, 366.00, 0.12, 6.00, 70.00, 218.75),
		(3.00, 0.15, 95.00, 176.00, 236.00, 0.25, 5.00, 0.00, 187.50),
		(10.00, 0.15, 95.00, 176.00, 236.00, 0.17, 6.00, 80.00, 218.75),
		(0.15, 0.15, 0.00, 0.00, 366.00, 0.25, 0.00, 45.00, 156.25),
		(0.15, 0.15, 0.00, 0.00, 366.00, 0.25, 3.50, 110.00, 62.50),
		(0.005, 0.00, 0.00, 0.00, 366.00, 0.05, 0.00, 0.00, 175.00),
		(0.80, 0.08, 262.00, 304.00, 577.00, 0.25, 5.00, 40.00, 175.00),
		(2.43, 0.08, 136.00, 191.00, 253.00, 0.22, 4.75, 100.00, 127.00),
		(2.43, 0.08, 136.00, 191.00, 253.00, 0.22, 4.75, 100.00, 127.00),
		(0.15, 0.15, 0.00, 0.00, 366.00, 0.25, 0.00, 45.00, 156.25),
		),
	'med': (
		(0.05, 0.05, 0.00, 0.00, 366.00, 0.15, 0.00, 100.00, 20.00),
		(0.60, 0.05, 119.00, 250.00, 250.00, 0.25, 5.00, 40.00, 140.00),
		(0.60, 0.05, 95.00, 176.00, 236.00, 0.25, 4.00, 40.00, 90.00),
		(10.00, 10.00, 0.00, 0.00, 366.00, 0.12, 6.00, 70.00, 175.00),
		(3.00, 0.15, 95.00, 176.00, 236.00, 0.25, 5.00, 0.00, 150.00),
		(10.00, 0.15, 131.00, 142.00, 255.00, 0.17, 6.00, 80.00, 171.00),
		(0.15, 0.15, 0.00, 0.00, 366.00, 0.25, 0.00, 45.00, 125.00),
		(0.15, 0.15, 0.00, 0.00, 366.00, 0.25, 3.50, 110.00, 50.00),
		(0.005, 0.00, 0.00, 0.00, 366.00, 0.05, 0.00, 0.00, 140.00),
		(0.80, 0.08, 262.00, 304.00, 577.00, 0.25, 5.00, 40.00, 140.00),
		(2.43, 0.08, 136.00, 191.00, 253.00, 0.22, 4.75, 100.00, 101.60),
		(2.43, 0.08, 136.00, 191.00, 253.00, 0.22, 4.75, 100.00, 101.60),
		(0.15, 0.15, 0.00, 0.00, 366.00, 0.25, 0.00, 45.00, 125.00),
		),
	'low': (
		(0.05, 0.05, 0.00, 0.00, 366.00, 0.15, 0.00, 100.00, 15.00),
		(0.60, 0.05, 119.00, 250.00, 250.00, 0.25, 5.00, 40.00, 105.00),
		(0.60, 0.05, 95.00, 176.00, 236.00, 0.25, 4.00, 40.00, 67.50),
		(10.00, 10.00, 0.00, 0.00, 366.00, 0.12, 6.00, 70.00, 131.25),
		(3.00, 0.15, 95.00, 176.00, 236.00, 0.25, 5.00, 0.00, 112.50),
		(10.00, 0.15, 95.00, 136.00, 269.00, 0.17, 6.00, 80.00, 131.25),
		(0.15, 0.15, 0.00, 0.00, 366.00, 0.25, 0.00, 45.00, 93.75),
		(0.15, 0.15, 0.00, 0.00, 366.00, 0.25, 3.50, 110.00, 37.50),
		(0.005, 0.00, 0.00, 0.00, 366.00, 0.05, 0.00, 0.00, 105.00),
		(0.80, 0.08, 262.00, 304.00, 577.00, 0.25, 5.00, 40.00, 105.00),
		(2.43, 0.08, 136.00, 191.00, 253.00, 0.22, 4.75, 100.00, 76.20),
		(2.43, 0.08, 136.00, 191.00, 253.00, 0.22, 4.75, 100.00, 76.20),
		(0.15, 0.15, 0.00, 0.00, 366.00, 0.25, 0.00, 45.00, 93.75),
		),
	}

	cover_abbr = ['soil','alfa','pota','conif','orch','deci','grass','upld',
				'water','wheat','corn s','corn g','pot et']
				
	soil_capacity = ['low','med','high']
	
	whc = soil_capacity[soil_type-1]
				
	crop = soil_data_dict[whc][gtype-1]
	
	sc_constants['h_max'] = crop[0]
	sc_constants['h_min'] = crop[1]
	sc_constants['d_e'] = crop[2]
	sc_constants['d_f'] = crop[3]
	sc_constants['d_h'] = crop[4]
	sc_constants['cp_albedo'] = crop[5]
	sc_constants['max_leaf'] = crop[6]
	sc_constants['surf_res'] = crop[7]
	sc_constants['water_cap'] = crop[8]

#	*****  maximum amount of water in the soil_x and soil_y layers.
	if soil_type == 1: 
		sc_constants['soil_max'] = 15.0
	elif soil_type == 2: 
		sc_constants['soil_max'] = 20.0
	elif soil_type == 3: 
		sc_constants['soil_max'] = 25.0

#	*****  crop_max is the maximum amount of water in the crop_x and crop_y layers.
	sc_constants['crop_max'] = sc_constants['water_cap'] - sc_constants['soil_max']

	return ()

#---------------------------------------------------------------------------
def leafsize (gtype, month, day, sc_constants):

	d_e = sc_constants['d_e']
	d_f = sc_constants['d_f']
	d_h = sc_constants['d_h']
	max_leaf = sc_constants['max_leaf']

	grass = [2.0,2.0,3.0,4.0,5.0,5.0,5.0,5.0,4.0,3.0,2.5,2.0]	#modified re: 1997 doc

#	***** no leaves for bare soil and open water
	if gtype == 1 or gtype == 9:
		leaf = 0.0

#	***** constant value used for coniferous trees
	elif gtype == 4:
		leaf = 6.0

#	***** leaf size is dependent on month for grass and upland
	elif gtype == 7 or gtype == 8 or gtype == 13:
		leaf = grass[month-1]

#	***** leaf area for deciduous trees and silage corn
	elif gtype == 6 or gtype == 11:
		if day >= d_e and day < d_f:
			leaf =((max_leaf-0.1)*(float(day-d_e)/float(d_f-d_e)))+0.1
		elif day < d_e or day >= d_h+40:
			leaf = 0.0
		elif day >= d_f and day < d_h:
			leaf = max_leaf
		elif day >= d_h and day < d_h+40:
			leaf =  ((max_leaf - 0.1)*float(d_h+40-day)/40.0)+0.1

#	***** leaf area for orchards (just tree component)
	elif gtype == 5:
		if day < d_e or day >= d_h:
			leaf = 0.0
		elif day >= d_e and day < d_f:
			leaf = 2.5*float(day-d_e)/float(d_f-d_e)
		elif day >= d_f and day < d_h-40:
			leaf = 2.5
		elif day >= d_h-40 and day < d_h:
			leaf = 2.5*float(d_h-day)/40.0

# 	**** all other crops (2, 3, 10, 12)
	else:
		if day >= d_e and day < d_f:
			leaf = ((max_leaf - 0.1)*float(day-d_e)/float(d_f-d_e)) + 0.1
		elif day >= d_f and day <= d_h:
			leaf = max_leaf
		else:
			leaf = 0.0

	return (leaf)
	
#---------------------------------------------------------------------------
def radiation (tmp, dew, tsky, solar, snow, gtype, leaf, soil_type, sc_status, sc_constants):

#	calculate net radiation (Wm-2)

	if gtype == 9:
#		use this for pan evap  -kle 7/11/03
		adj_cp_albedo = 0.13
	elif snow >= 1:
#		use snow albedo instead of crop albedo   -kle 4/21/03
		adj_cp_albedo = 0.65
	else:
#		make adjustment to surface cp_albedo based on leaf size 
		adj_cp_albedo = adjustalbedo (gtype, sc_constants['cp_albedo'], leaf, soil_type, sc_status)
	
#	stephan boltzman constant (wm-2 k-4)
	omega = 0.0000000567
#	emissivity
	em = 0.95

#	vapor pressure of dewpoint
	v_dew = 6.108*exp(17.27*dew/(dew+273.3))
	
#	reduction in long-wave radiation due to sky cover
	ccc = 0.2 + 0.8*(1.0-tsky)

	ktmp = tmp + 273.16

#	net long-wave radiation
	r_lw_net = em * omega * (ktmp**4.0) * (1.35*((v_dew/ktmp)**(1.0/7.0))-1.0) * ccc 

#	adjust short wave based on surface charcacteristics 
 	r_short = (1.0-adj_cp_albedo)*solar

	rad =  r_lw_net + r_short

	return (rad)
	
#---------------------------------------------------------------------------
def rainfall (rain, leaf, month, julian_day, gtype, daily_ppt, sc_constants, sc_status):

	d_e = sc_constants['d_e']
	d_f = sc_constants['d_f']
	d_h = sc_constants['d_h']

#	***** leaf interception is subtracted, giving total rainfall  *****

	if gtype != 6:
#		***   p_max is the maximum percentage of rain that can be intercepted
		p_max = (1.0 - (0.5)**leaf)

#		***   i is the maximum amount of intercepted rain
		i = rain * p_max
		
#		***   add intercepted rain to interception already on leaf
		i = i + sc_status['interception']
	
#		***  i can't exceed 0.2 times the leaf area
		if i > 0.2 * leaf:
			i = 0.2 * leaf

#		***  decrease amt of intercepted water when adding rain hourly  -kle 4/2/03
		if not daily_ppt:
			i = i/24.

#		***   factor allows for evap of interception while rain is falling.
#		***	  not used when hourly precipitation is being used -kle 6/2002
		if daily_ppt and i > 0.00:
			factor = [1.0,1.0,1.2,1.4,1.6,2.0,2.0,2.0,1.8,1.4,1.2,1.0]
			i = factor[month-1] * i
#			*** can not intercept more rain than fell
			if i > rain:
				i = rain

#	***   interception by deciduous trees is a special case.  reference to this
#	***   routine is given in helvey and patric, canopy and litter interception
#	***   of rainfall by hardwoods of eastern united states, water resour. res, 
#	***   1965 1,193-206.

	elif gtype == 6:

#		**   switch rain back to inches	
		rain = rain/25.4

#		**   value for dormant trees
		idorm = ((.914*rain)-0.015)

		if idorm < 0:
			idorm=0.

#		**   value for trees in leaf
		igrow = ((.901*rain)-0.031)

		if igrow < 0:
			igrow=0.

		if julian_day <= d_e or julian_day > d_h+40:
			i = rain-idorm
		elif julian_day >= d_f and julian_day <= d_h:
			i = rain-igrow
#		**   linear interpolation on interception between leaf emergence and full leaf
		elif julian_day > d_e and julian_day < d_f:
			i=(((rain-igrow)-(rain-idorm))*(float(julian_day-d_e)/float(d_f-d_e)))+(rain-idorm)
#		**  linear interpolation on interception between full leaf and leaf fall
		elif julian_day > d_h and julian_day <= d_h+40:
			i=(((rain-igrow)-(rain-idorm))*(float(d_h+40-julian_day)/40.0))+(rain-idorm)

#		**  change rain and interception back to millimeters
		rain = rain*25.4
		i = i*25.4
		
#		add to what's already there
		i = i + sc_status['interception']
	
#	how much interception has been added to leaves
	add_interception = i - sc_status['interception']

#	update amount of interception on leaves		
	sc_status['interception'] = i

	return (add_interception)
	
#---------------------------------------------------------------------------
def rscalc (gtype, month, julian_day, leaf, tmp, dewpt, snow, nighttime, sc_constants, sc_status):

#	***** calculate the surface resistance based on leaf  *****
#	***** area and the amount of water in the soil.       *****
	if snow >= 1 or gtype == 9: 
#		no resistance when snow on ground or open water
		r_s = 0.0
		return (r_s)
	else:
		r_s, r_ss = surfresist(gtype,month,julian_day,leaf,tmp,dewpt,sc_constants,sc_status)

#	***** this is the expression for surface resistance at night 
#	***** when the leafs stomata are closed. page 24 eq. 4.42  
	if nighttime:
		if gtype == 5:
#			for orchards, add average leaf size of grass to that of trees
			if julian_day > sc_constants['d_e'] and julian_day < sc_constants['d_h']:
				leaf = leaf + 5.0
			else:
				leaf = 2.5

		r_s = 2500*r_ss/((r_ss*leaf)+2500) 
		
	return (r_s)
	
#---------------------------------------------------------------------------
def runocalc (rain, dew, gtype, add_inter, sc_constants, sc_status):

#	dew is not allowed to runoff.  no runoff from grass, bare soil or water (pan evap)
	if rain-dew > 0.0 and gtype != 7 and gtype != 1 and gtype != 9:

#		***   amount of soil moisture in centimeters
		store = (sc_constants['water_cap']-(sc_status['crop_x']+sc_status['crop_y']+sc_status['soil_x']+sc_status['soil_y']))/10.

#		****  convert rain to centimeters
		precip = rain/10.

#		****  runoff occurs when precip exceeds inch or soil near saturation
		if precip > 2.54 or store < (sc_constants['soil_max']/10)*0.4:
#			****  calculate runoff using usda 1972 scs national engineering hanbook, hydrology, section 4.
			runo = (precip - (0.2*store))**2/(precip + (0.8*store))

#			****  runoff converted to mm
			runo = runo*10
		else:
			runo = 0.0

	else:
		runo = 0.0

#	***  runoff is set to zero if it exceeds rainfall
	if runo > rain-add_inter:
		runo=0.0
		
	return (runo)

#---------------------------------------------------------------------------
def seasonaladd (type,julian_day,sc_constants):

#	this subroutine calculates the amount of unavailable water for a
#	   winter wheat crop at different parts of the year.

#	specific types need linear calculation adjustments
#				d_e to d_f	d_h to d_h+40	type
#	soil			 no			 no			  1
#	alfalfa			yes			 no			  2
#	potatoes		yes			 no			  3
#	conifers		 no			 no			  4
#	orchards	    yes			yes			  5
#	deciduous	     no			 no			  6
#	grasslands   	yes			 no			  7
#	upland	        yes			 no			  8
#	open water	     no			 no			  9
#	winter cereals	see wintercropsadd		 10
#	corn (silage)   yes			 no			 11
#	corn (grain)    yes			yes			 12


	d_e = sc_constants['d_e']
	d_f = sc_constants['d_f']
	d_h = sc_constants['d_h']
	crop_max = sc_constants['crop_max']
	increase = 0
	decrease = 1

	if julian_day > d_h or julian_day < d_e:
#		***  before emmergence and after harvest only bare soil remains for certain
#		***  crops.  thus the moisture in the x_crop and y_crop reservoirs is 
#		***  unavailable for et.  this amount of water is given by x_max and y_max.

		if type != 5 and type != 12:
			x_max = 0.4*crop_max
			y_max = 0.6*crop_max

		else:
			if julian_day > d_h and julian_day <= d_h+40:
#				*** for these crop types the amount of unavailable water is zero until 
#				*** harvest and then is linearly increased to the maximum value over
#				*** a period of 40 days.  assumes that even though the crop is harvested 
#				*** the plants remain and continue to contribute to et.
 
				x_max,y_max = adjustmaxlinear (crop_max,julian_day,d_h,d_h+40,increase)

			elif julian_day > d_h+40 or julian_day < d_e:
#				*** 40 days after harvest et is limited to that from bare soil.

				x_max = 0.4*crop_max
				y_max = 0.6*crop_max

	elif julian_day >= d_e and julian_day <= d_f:
#		*** between emergence and full leaf (root) the amount of unavailable water
#		*** is linearly reduced to zero at full leaf.

		x_max,y_max = adjustmaxlinear (crop_max,julian_day,d_e,d_f,decrease)

	elif julian_day > d_f and julian_day <= d_h:

#		*** this period wasn't addressed previously, added 7/2002 kle

		x_max = 0.
		y_max = 0.
	
	return (x_max,y_max)
	
#---------------------------------------------------------------------------
def special_dates (gtype, julian_day, sc_constants):

	if gtype == 2: 
#		***** set d_e, d_f, and d_h depending on which of alfalfa's *****
#		***** three growth seasons we are in.                       *****
		if julian_day >= 120 and julian_day < 161:
			sc_constants['d_e'] = 120
			sc_constants['d_f'] = 160
			sc_constants['d_h'] = 160
		elif julian_day >= 161 and julian_day < 206:
			sc_constants['d_e'] = 161
			sc_constants['d_f'] = 205
			sc_constants['d_h'] = 205
		elif julian_day >= 206 and julian_day < 250:
			sc_constants['d_e'] = 206
			sc_constants['d_f'] = 250
			sc_constants['d_h'] = 250
		else:
			sc_constants['d_e'] = 119
			sc_constants['d_f'] = 250
			sc_constants['d_h'] = 250
		
	elif gtype == 10:
#		***** find values of d_e, d_f, and d_h for different times of  *****
#		***** the year for winter wheat. the crop height is assumed to *****
#		***** .20 just before and after the dormant winter season.     *****
		if julian_day < 75:
			sc_constants['d_e'] = 75
			sc_constants['d_f'] = 175
			sc_constants['d_h'] = 365
			sc_constants['h_max'] = .20	      
			sc_constants['h_min'] = .20
		elif julian_day < 262 and julian_day >= 75:
			sc_constants['d_e'] = 75
			sc_constants['d_f'] = 175
			sc_constants['d_h'] = 212
			sc_constants['h_max'] = .80
			sc_constants['h_min'] = .20
		elif julian_day >= 262:
			sc_constants['d_e'] = 262
			sc_constants['d_f'] = 304
			sc_constants['d_h'] = 304
			sc_constants['h_max'] = .20
			sc_constants['h_min'] = .05 

	return ()

#---------------------------------------------------------------------------
def sub_from_layer (addition, current_val, avail):


#	***	does the amount of water in layer exceed the amount of et?

	if current_val >= abs(addition):

#		***	if it does so, reduce the amount of water in layer by amount of et
 
		current_val = current_val + addition
		addition = 0.
		done = 1
		
		if current_val < avail:

#			***	when crops are not actively growing, all of the water in a layer is
#			***	not available to et (no roots). avail is the amount of water in the 
#			***	layer that is unavailable to et.

#			***	addition is reduced by the amount of et required to bring the soil
#			***	moisture to its smallest posssible value and the amount of soil water
#			***	set to avail.  

			addition = current_val - avail
			current_val = avail
			done = 0
	
	else:

#		*** addition is reduced by the amount of et required to bring the soil
#		*** moisture to its smallest posssible value. 
   
		addition = addition + (current_val - avail)
		current_val = avail
		done = 0

	return (addition, current_val, done)

#---------------------------------------------------------------------------
def surfresist (gtype,month,day,leaf,temp,dewpt,sc_constants,sc_status):

#	res_grass =  [50.0,50.0,50.0,50.0,45.0,40.0,40.0,40.0,40.0,45.0,50.0,50.0] #orig morecs
	res_grass =  [80.0,80.0,60.0,50.0,40.0,60.0,60.0,70.0,70.0,70.0,80.0,80.0] #morecs 2.0
	leaf_grass  = [2.0,2.0,3.0,4.0,5.0,5.0,5.0,5.0,4.0,3.0,2.5,2.0]	#modified re: 1997 doc
	
	res_upland = [160.0,160.0,160.0,160.0,70.0,70.0,70.0,70.0,70.0,160.0,160.0,160.0]

#	res_min -- surface resistance of a dense crop in wet soil
#	res_crop - surface resistance of the crop
#	res_soil - surface resistance of bare soil
#	capacity - maximum water capacity for crop
#	crop_x --- amount of water currently in top 40% of soil 
#	crop_y --- amount of water currently in bottom 60% of soil
#	vpd ------ vapor pressure deficit

	crop_x = sc_status['crop_x']
	crop_y = sc_status['crop_y']
	soil_x = sc_status['soil_x']
	soil_y = sc_status['soil_y']
	d_e = sc_constants['d_e']
	d_f = sc_constants['d_f']
	d_h = sc_constants['d_h']
	res_min = sc_constants['surf_res']
	capacity = sc_constants['water_cap']
	soil_max = sc_constants['soil_max']

#	*** for ochards, grass must be included. page 26 eq. 4.47, eq. 4.49 

	if gtype == 5:
		if day > d_e and day < d_h:
#			between leaf emergence and leaf fall
			res_crop = 1.0 / ((0.7**leaf)/res_grass[month-1] + (1.0-(0.7**leaf))/80.0)
#			for surface resistance calculations, use combined LAI of trees and grass
			leaf = leaf + leaf_grass[month-1]
		else:
#			when no leaves on the trees, same as grass
			res_crop = res_grass[month-1]
			leaf = leaf_grass[month-1]

#	*** for coniferous trees crop resistance is greatly dependent on temperature 
#	*** and vapor pressure therefore these equations are used. page 24     

	elif gtype == 4:
		if temp >= 20:
			res_crop=res_min
		elif temp <= -5:
			res_crop=10000.0
		else:
			res_crop=25.0*res_min/(temp+5.0)

#		vapor pressure of temperature
		v_tmp = 6.108*exp(17.27*temp/(temp+273.3))
#		vapor pressure of dewpoint
		v_dew = 6.108*exp(17.27*dewpt/(dewpt+273.3))

		vpd = v_dew - v_tmp

		if vpd >= 20:
			res_crop = 10000.0
		else:
			res_crop = res_crop/(1.0-0.05*vpd)

#	*** for cereal crops scenescence is taken into account
#	*** between full growth and harvest. page 24 eq. 4.44 

	elif (gtype == 2 or gtype == 10 or gtype == 11) and (day > d_f and day <= d_h):
		fact = float(day-d_f)/float(d_h-d_f)
		res_crop = res_min +  50.0*fact + 500.0*((fact)**(3.0)) 

#	***   similarly senescence is taken into account during leaf fall in deciduous trees.

	elif gtype == 6 and (day > d_h and day < d_h+40): 
		fact = float(day-d_h)/float((d_h+40)-d_h)
#		res_crop = res_min + 50.0*fact + 500.0*((fact)**(3.0))  changed to following 8/02 -kle
		res_crop = res_min + 100.0*fact
		
#	*** for deciduous trees and corn for grain the leaves are 
#	*** assumed to be dead through winter, so use bare soil    

	elif (gtype == 6 or gtype == 12) and (day > d_h+40 or day < d_e):
		res_crop = 100.0
	
#	***   for grass and uplands crop resistance is a function of month.
#	***   potential evaporation (gtype 13) is defined over grass.

	elif gtype  ==  7 or gtype == 13:
		res_crop = res_grass[month-1]

	elif gtype  ==  8:
		res_crop = res_upland[month-1]

#  ***  CAN'T FIND THIS IN DOCUMENTATION; REMOVED
#  ***  surface resistance is also a function of soil moisture
#		if crop_x + soil_x  ==  0.0:
#			if crop_y + soil_y > 0.0:
#				surf_resist = res_crop*((2.5*((capacity-soil_max)*0.6)/crop_y)-1.5)
#			else:
#				surf_resist = 10000.00
#		return (surf_resist, res_soil)

#	***  anything not covered above

	else:
		res_crop = res_min



#	***  bare soil case - depends on soil moisture ***

	if gtype == 1:
	
		res_soil = 100.0

		if soil_x > 0:
#			***  uppermost layer is not dry
			surf_resist = res_soil

		else:
#			***  uppermost layer completely dry
			surf_resist = res_soil*((2.5*soil_max*0.6)/(soil_y+.000001)-1.5)
		

#	soil resistance term when crop is present

	else:
		if soil_x+crop_x > 0.4*soil_max or gtype == 13:
#			***  top soil is wet.  this is the case for potential et, by definition.
			res_soil = 100.0

		elif soil_x+crop_x == 0.0:
#			***   top soil layer is completely dry
			res_soil = 10000.0

#			***   crop resistance also increases as stomata begin to close.
			res_crop = res_crop*((2.5*(capacity*0.6)/(crop_y+soil_y+.000001))-1.5)

		else:
#			***  soil resistance increases as soil drys out.
			x_max = 0.4*capacity
			res_soil = (100. * x_max) / ((crop_x+soil_x) + (0.01 * x_max))


#		*** finally calculate the combined soil and crop resistance *****
#		*** p. 23  eq. 4.40 (after some algebraic manipulation)     *****

		a = (0.7)**leaf
		surf_resist = (res_crop*res_soil)/((res_soil*(1-a))+(res_crop*a))

	return (surf_resist,res_soil)

#---------------------------------------------------------------------------
def wintercropsadd (julian_day,sc_constants):

#	this subroutine calculates the amount of unavailable water for a
#	   winter wheat crop at different parts of the year.

#	the amount of available water varies from:
#		jan - d_e: 3.75 x available water for bare soil 
#		d_e - d_f: linear rise from 3.75 x available water for bare soil
#		           to 100% crop_max
#		d_f - d_h: 100% crop_max
#		d_h - dec: available water for bare soil.

	crop_max = sc_constants['crop_max']
	soil_max = sc_constants['soil_max']
	d_e = sc_constants['d_e']
	d_f = sc_constants['d_f']
	d_h = sc_constants['d_h']
	
	sparse = crop_max-(soil_max * 3.75)

	if julian_day >= 1 and julian_day < d_e:

#		*** calculate amount of unavailable water between jan 1 and emergence	

		x_max = 0.4 * sparse
		y_max = 0.6 * sparse

	elif julian_day >= d_e and julian_day <= d_f:

#		*** linear decrease unavailable water from sparse to 0

		x_max,y_max = adjustmaxlinear (sparse,julian_day,d_e,d_f,decrease)
	
	elif julian_day > d_f and julian_day <= d_h:

#		*** this period wasn't addressed previously, added 7/2002 kle

		x_max = 0.
		y_max = 0.

	elif julian_day > d_h and julian_day <= 366:

#		*** after harvest all of water in crop reserviors is unavailable

		x_max = 0.4*crop_max
		y_max = 0.6*crop_max

	return (x_max,y_max)