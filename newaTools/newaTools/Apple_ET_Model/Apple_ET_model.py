# Apple ET Program

import math
from mx import DateTime

###  Need to figure how to do sine/cos of radians in math in Zenith
###  Should math.sin be radians or degrees for soldec
###  ref_lon is set to Eastern Time Zone  This should be variable for use in other time zones

###  assumes that rs, vpd,are a list of 24 hourly solar radiation values

def Deg2Rad(Deg):
	Rad=math.pi/180.*Deg

	return Rad
	
def Rad2Deg(Rad):
	Deg=180/math.pi*Rad
	
	return Deg

def changeunits(tmp,dew,solar,wind):
	try:
		if tmp >-90.0:
			tmp = (tmp-32.0)*(5.0/9.0)
		else:
			tmp = -99.0
		
		if dew > -90:
			dew = (dew-32.0)*(5.0/9.0)
		else:
			dew = -99.0

		if solar >= 0.0:
			solar = solar*41860.0   ### langleys to watt-hours/m2
		else:
			solar = -99.0

		if wind >=0.0:
			wind = wind * 0.44704   ### mph to m/s
		else:
			wind = -99.0

	except:
		print 'ERROR chnaging Units: ', tmp,dew,solar,wind

	return (tmp,dew,solar,wind)

def SunAngle(doy,ftime,lat,Lz,Lm):
	## estimates sun angle (0=zenith) in both degrees and radians
	
    za_rad=Zenith(lat,Lz,Lm,ftime,doy)    #zenith angle in radians
    za_deg=Rad2Deg(za_rad)    #zenith angle in degrees
    sp=(za_deg,za_rad)
    
    return sp
    
    

def Zenith (lat,Lz,Lm,ftime,doy):
	#lat in degree
	#lz: longitude in degrees
	#lm: reference meridian longitude, degress
	#ftime: time expressed as hour and decimal fraction of hour 
	#jday: julian day
	#zenith angle in radians

    #  soldec is radians
    
	soldec=0.409*math.sin((2.0*math.pi/365.0)*doy-1.39)
	
	### soldoc is correct  print soldec,'soldec'
	f=279.575+0.9856*doy
	f= math.pi/180.0*f

	ET= -104.7*math.sin(f)+596.2*math.sin(2.*f)+4.3*math.sin(3.*f)-12.7*math.sin(4.*f)-429.3*math.cos(f)-2.0*math.cos(2.*f)+19.3*math.cos(3.*f)
	ET=ET/3600.
	LC=(abs(Lm)-abs(Lz))*0.0667
	t0=12.0-ET-LC
	ftime=(ftime-t0)*0.26179
	lat=math.pi/180.0*lat
	z=math.acos(math.sin(lat)*math.sin(soldec)+math.cos(lat)*math.cos(soldec)*math.cos(ftime))
	
	return z


def SunlitFraction(sunangle):

#	print sunangle,'In Sunlit'
	# returns the fraction of sunlit and shaded leaf area

	sl_fr=0
	sh_fr=0
	
	if sunangle<90 and sunangle>0:      # day
		sl_fr=0.4

		#this is for very low sun angle, when the trees are shading each other
	
		suna = 90-sunangle     # 0 is now sun at the horizon
#                print suna,'suna'
		if suna<=32:
			sl_fr=sl_fr*((0.01225*suna**2+2.733*suna)/100.)

		sh_fr=1-sl_fr

	elif sunangle>90 or sunangle<=0:    #night

		sl_fr=0
		sh_fr=0          # at night both sl and sh are 0%

#	print sunangle,'sunangle'
	return (sl_fr, sh_fr)
	


def DiffuseRadiation(rs,hour):

	# estimates the percentage of diffuse radiation basedon time of the day and total solar irradiance (see model document)
	
	diff = 0
		
	if hour>=8 and hour<10:               # % between 8:00am and 9:59
		diff= -0.1471*rs+109.7
	elif hour>=10 and hour<16:  			  # between 10:00am and 15:59
		diff=-0.1311*rs+131.4
	elif hour>=16 and hour<17: 		  #between 16:00 and 16:59am
		diff=-0.1563*rs+112.1
	elif hour>=17 and hour<19:  			  #between 17:00 and 18:59am
		diff=-0.1579*rs+96.26	

	if diff>92:	 					  #no more than 92% of diffuse
		diff=92

	return diff

def vapor_def(temp,dew):
	v_temp = 6.108*math.exp(17.27*temp/(temp+273.3))
	v_dew = 6.108*math.exp(17.27*dew/(dew+273.3))

	vpd = v_temp-v_dew

	return vpd

def relhum(temp,dew):

	v_temp = 6.108*math.exp(17.27*temp/(temp+273.3))
	v_dew = 6.108*math.exp(17.27*dew/(dew+273.3))

	rh = (v_dew/v_temp)*100.

        return rh
	
def StomatalConductance(sunangle,vpd,gstd,gmax,vpdmax):

#estimates stomatal conductance as a function of vpd, using Alan model of gs
#sunangle: col1=deg col2=radians
#vpd   : vpd (kPa) vector
#gsdt  : photosynthesis limited value for gs for VPD=0
#gmax  : max gs without phot limitation for VPD =0
#maxvpd: max vod at which stomata are still open (or just close) 
#these parameters are used to determine the vpd threshold for phot-limited vs vpd-limited gs
#note: sunangle is used to set gs to 0 at night

#note= this function returns the gs in the same units as gstd

	gs=0
	
	if vpd<0:   #some cleaning on vod
		vpd=0	
	# determine the equation for the vpd-limited gs

	p1=(0.0,gmax)

	p2=(vpdmax,0.0)

	a=(p2[1]-p1[1])/(p2[0]-p1[0]) # slope
	b=p1[1]-a*p1[0]               # intercept

	#determines  the VPD threshold for the phot-limited gs

#	print a,'a'
#	print b, 'b'
#	print sunangle,'sunangle'
	vpd_tr=(gstd-b)/a

	# now we can proceede and assigne gs based on VPD
	if vpd<vpd_tr:
		gs =gstd         #phot limited gs	
	elif vpd>=vpd_tr:
		gs = a*vpd+b    # vpd limited gs

	# and just to finish, we set to 0 all the gs at night

	if sunangle>=90 or sunangle<=0:
		gs = 0

	return gs


def AerodynamicResistance(ws,z,z0w,z0m,dw,dm):

#z0w: roughness length for water vapor (m)
#z0m: roughness length for momentum (m)
#dw: displacement heght for water vapor (m)
#dm: displacement height for momentum (m)
# aerodynamic resistance Dragoni 03

	k_square= 0.1681  # square root of Von Karman costant 0.41
	if ws< -9000:
		ws=0
	if ws ==0: ws = 0.01  ### avoid division by zero below #atd
	
	ra = (math.log((z-dw)/z0w)*math.log((z-dm)/z0m)/(ws*k_square)) # aerodynamic resistance

	return ra

def net_rad(tmp,dew,tsky,rs):
	adj_cp_albedo = 0.1 + 0.25*(0.17-0.1)*2.5  #### Using MORECS orhard vales for soil albedo and trees
	omega = 0.0000000567  # Stephan boltz
	em = 0.95       # emissivity
	v_dew = 6.108*math.exp(17.27*dew/(dew+273.3))  ##vapor presure

	ccc = 0.2 + 0.8*(1.0-tsky)  ## reduction due to sky cover

	ktmp = tmp + 273.16

	r_lw_net = em * omega * (ktmp**4.0) * (1.35 * ((v_dew/ktmp)**(1.0/7.0))-1.0) *ccc

	r_short = (1.0-adj_cp_albedo)*rs

	rad = r_lw_net + r_short

	return rad

def RefGrassNetRad(doy,hour,minute,rs,T,rh,vpd,long,latitude,LTZlong,slas):
	#estimates net radiation of reference grass
	#INPUT 
	#doy  :doy

	#rs : solar radiation W m-2
	#T  : air temperature
	#longitude
	#latitude
	#reference_longitude
	#sea level altitude

	# estimate ea from rh and vpd

	if rh==100: rh=99.9
		
	rh=rh/100

	ea=vpd/(1./rh-1)
	
	#estimats extraterresrtial solar radiation
	time=hour+minute/60    
	dr=1+0.033*math.cos(2.*math.pi/365.*doy)    # inverse relative distance Earth-Sun

	sd=0.409*math.sin(2.*math.pi/365.*doy-1.39) # solar declination
	b=(2.*math.pi*(doy-81))/364                      #b forseasonal correction

	sc=0.1645*math.sin(2.*b)-0.1255*math.cos(b)-0.025*math.sin(b)          #season correction for solar time (hour)
	sta=math.pi/12.*((time+0.06667*(LTZlong-long)+sc)-12)     #solar time angle  at midpoint of the period

	sta1=sta-math.pi*1./24

	sta2=sta+math.pi*1./24


	ra_xt=229.18312*0.0820*dr*((sta2-sta1)*math.sin(latitude)*math.sin(sd)+math.cos(latitude)*math.cos(sd)*(math.sin(sta2)-math.sin(sta1))) # extraterrestrial solar radiation MJ m-2 h-1

	rso=(0.75+0.00002*slas)*ra_xt       # clear sky solar radiation MJ m-2 h-1

	B=2.043E-10                      # Stefan-Boltzman constant MJ m-2 j-1

	if rs<0:
		rs=0

	if rs>rso:
		rs=rso

	if rs>0:
		ratio=rs/rso
	else: 
		ratio=0.8		# if night the ratio rs/rso is assumed to be 0.8/'
			
	rnl=B*(T+273.16)**4.*(0.34-0.14*math.sqrt(ea))*(1.35*ratio-0.35)        # net outgoing radiation for reference grass
	rns=(1-0.23)*rs                                                               # net incoming shortware solar radiation MJ m-2 h-1

	rn=(rns-rnl)               # grass reference solar radiation

	return rn


def NetRad_ground2leaf(treed,rn,Al,As):
	#estimates net radiation on leaf area basis from net radiation measurements on ground area
	#treed   : tree density tree m-2
	#rn      : net radiation vector
	#Al      : total sunlit leaf area
	#As      : total shaded leaf area

	#nr_sl   : shaded net rad
	#nr_sh   : shaded net rad

	nr_sl=0
	nr_sh=0

#	print rn,treed,Al,'rn,treed,Al in ground2'

	nr_tot=rn/(treed*(Al))       # total net radiation is distributed among sunlit leaves of the tree

	if nr_tot<0:
		nr_tot=0  # negative nr are set to 0

	nr_sl=nr_tot

	nr_sh=0         # shaded leaf net radiation is assumed to be equal to 0 (Green 97)

	return (nr_sl, nr_sh)


def VapPSatCurveSlope(airt):

	#estimates saturation slope vapor pressure curve at temperature T (kPa*C-1)
	#airt: temperature (C)

	a=17.27*airt/(airt+237.3)
	b=4098.0*(0.6108*math.exp(a))
	
	vp=(b/(airt+237.3)**2)

	return vp

def PenmanMontieth(rn,rs,ra,vpd,temp,atmpress,delta): 

	#Penman Montieth equation (Green 1997)
	#rn: net radiation (W*m-2)
	#rs: stomatal conductance (s*m-1)
	#ra: aerodynamic constant (s*m-1)
	#vpd: water vapor pressure deficit (kPa)
	#temp: air temperature (K)
	#atmpress: atmospheric pressure (kPa)
	#delta :' slope vapor pressure curve [kPa*C-1]


	Cp = 1013.0               #//  specific heat of moist air at constant pressure  [J*kg-1*C-1]
	WvDAirMW_ratio = 0.622    #   ratio between water vapor and dry air molecular weights
    
	lamnda=2.45*1000000.0     ##### //latentheatofvaporisation[J*kg-1]
	rho=1.2923           ###//meanairdensityatconstantpressure[kg*m-3]

	if rn<0:
    		rn=0

	psi=Cp*atmpress/(WvDAirMW_ratio*lamnda)      ###% //psychrometricconstant[kPa*C-1]
		
	et1=rn*delta*ra+rho*Cp*vpd    # //numeratorofPM
	et2=(delta+2.0*psi)*ra+psi*rs      # //denominatorofPM
	et=((1./lamnda)*(et1/et2))        #% //PM

#	print et1,et2,'in pen'
#	print delta,ra,psi,rs,'delta,RA,PSI,RS'		
	return et

def run_apple(month,day,hour,doy,temp,dwpt,ws,rs,tsky,greentip_dt=None):

#	greentip_dt is date of green tip (bud break) in DateTime format
	#scaling of LA based on days since green-tip (days 0 through 90) from Terence Robinson
	la_scale = [0.00,0.21,0.49,0.83,1.18,1.52,1.94,2.43,2.91,3.47,4.09,4.78,5.54,6.31,7.07,7.90,8.80,9.70,10.60,11.50,12.54,
				13.79,15.04,16.29,17.53,18.71,19.89,21.07,22.18,23.28,24.32,25.29,26.20,27.10,28.00,29.11,30.42,32.02,33.82,
				35.90,38.12,40.47,42.97,45.60,48.37,51.21,54.05,56.83,59.67,62.44,65.14,67.84,70.41,72.97,75.40,77.62,79.56,
				81.29,82.67,83.99,85.17,86.21,87.18,88.01,88.91,89.74,90.58,91.34,92.17,92.86,93.56,94.25,94.87,95.43,95.98,
				96.47,96.95,97.30,97.71,98.06,98.34,98.61,98.82,99.03,99.24,99.45,99.58,99.65,99.79,99.86,99.93]
	#end of season scaling of LA for days since green-tip 184-205 from Terence Robinson
	la_scale_end = [99.72,99.10,98.06,96.74,95.01,92.93,90.51,87.66,84.62,81.15,77.48,73.46,69.16,64.59,59.67,54.47,49.00,
				43.17,36.94,30.35,23.28,15.80,7.90]

#	print 'in run_apple',month,day,hour,temp,dwpt,ws,rs,tsky
	#INPUT

	#ws         : wind speed (m s-1)
	#rs         : solar radiation (w m-2)
	#vpd        : vpd (kPa)
	#temp       : temp (degC)
	#rn         : net radiation (W m-2)
	#rh         : relative humidity (%)
	#LA         : total leaf area of the tree
	#filename   : name for the output file

	#OUTPUT

	#tr         : transpiration l h-1 tree-1
	#tr_daily   : daily total of transpiration l day-1 tree-1  col1= DOY col2 =tr col3=number of valid hours
	#rn         : net radiation for the trees, on ground basis W m-2 ground
	#nr_sl      : sunlit net radiation on leaf area basis W m-2 LA
	#nr_sh      :shaded net radiation on leaf area basis W m-2 LA
	#Esl        : total transpiration from sunlit leaves l hour-1
	#Esh        : total transpiration from shaded leaves l hour-1
	#Esl        : transpiration per LA from sunlit leaves l hour-1 m-2
	#Esh        : transpiration per LA from shaded leaves l hour-1 m-2

	#CONSTANTS
	#density 1280 tree ha-1 = 0.1280 tree m-2
	#Geneva_latitude=42;
	#Geneva_longitude=-73;
	#Geneva_timeZonelongitude=-75;
	#Geneva_altitude=200;
	#meas_height=5;
	#canopy_height=2.5;
	global stn_lat,stn_lon,stn_GMT_off,stn_elev,obs_ht,canopy_ht,tree_den,LA
	stn_lat =    42.
	stn_lon = -73.
	ref_lon = -75.    ### depends on time zone
	stn_elev = 200.
	obs_ht = 5.
	canopy_ht = 2.5
	tree_den = 0.1280
	LA = 14.95			### full leaf area
	
#	scale leaf area for time of year (days since greentip)
	if greentip_dt:
		dys_since_greentip = doy - greentip_dt.day_of_year
		if dys_since_greentip < 0 or dys_since_greentip > 206:
			LA = 0.
		elif dys_since_greentip >= 0 and dys_since_greentip <= 90:
			LA = LA * la_scale[dys_since_greentip]/100.
		elif dys_since_greentip > 90 and dys_since_greentip <= 183:
			LA = LA * 1.0
		elif dys_since_greentip > 183 and dys_since_greentip <= 206:
			LA = LA * la_scale_end[dys_since_greentip - 184]/100.
	
	minute = 0.  ### just hourly data

	temp,dwpt,rs,ws = changeunits(temp,dwpt,rs,ws)

	rs = rs/3600.  ### to assumes langleys/sec was orginal unit (I think this makes it watts/m2 -kle)
	vpd = vapor_def(temp,dwpt)

	vpd = vpd*.1  ###convert to kPa

	rh = relhum(temp,dwpt)

	ftime = hour+minute/60.

#	print doy,'doy',ftime,'ftime',vpd,'vpd',rh
	sun_angle = SunAngle(doy,ftime,stn_lat,stn_lon,ref_lon)
	zenith_ang = sun_angle

#	print 'zenith',zenith_ang

	(slprop,shprop) = SunlitFraction(zenith_ang[0])    ## Sunlit and shaded leaf area fraction

#	print 'rs',rs,hour
	diffuse = DiffuseRadiation(rs,hour)

#	print diffuse,'DIFFUSE'
	#stomatal conductance  sunlit leaves
	#0.00625 m s-1 =250 mmol m-2 s-1
	#0.01667 m s-1 = 800 mmol m-2 s-1
	# determines the non-vpd limited stomata conductance for sunlit leaves  based on percentage of diffuse light

	gs_sunlit_std=-1.*diffuse+250
	gs_sunlit_std=gs_sunlit_std/40000.  # m s-1
	
#	print gs_sunlit_std,' before gs_std',vpd
	gs_sunlit=StomatalConductance(sun_angle[0],vpd,gs_sunlit_std,0.01667,6.0)

#	print gs_sunlit,diffuse,'gs and diffuse'
	#  shaded leaves  determines the non-vpd limited stomata conductance for shaded leaves
	#0.002 m s-1 =80 mmol m-2 s-1
	#0.01667 m s-1 = 800 mmol m-2 s-1

	gs_shaded_std=diffuse+50.    #mmol m-2 s-1
	gs_shaded_std=gs_shaded_std/40000.    # m s-1
	gs_shaded=StomatalConductance(sun_angle[0],vpd,gs_shaded_std,0.01667,6)


#	print ws,'wind'
	ra=AerodynamicResistance(ws,5.0,0.03,0.34,0.83,0.83)
	
#	print slprop,LA,shprop,'slprop,LA,shprop'
	Al=slprop*LA
	As=shprop*LA

	# sometimes there may be negative net radiation while solar radiation is
	# still positive. For these hours we are set the net radiation to 80% of
	# solar radiation (80% is derived from plotting Nr vs Sr)

	rn = net_rad(temp,dwpt,tsky,rs)

#	print rn,rs,'rads long and short'
	if rn<=0 and rs >0:
		rn=0.8*rs
		
	# estimates reference grass net radiation
	# solar interception of grass in the orchard is set to 45% of total solar radiation. (after in-field observations)

	rs_grass=rs*0.45

	grass_rn=RefGrassNetRad(doy,hour,minute,rs_grass,temp,rh,vpd,stn_lat,stn_lon,ref_lon,stn_elev)

	# remove reference grass net radiation from total net radiation of the orchard
	# it takes in consideration that the grass in the orchard is only occuping
	# a fraction of the area ... 0.47 (see Apple Model document for explanation)

	if grass_rn<0:          #negative estimated grass rn is set to 0
		grass_rn=0


	grass_rn=0.53*grass_rn

	# however, no shadowing effect of adjacent trees in considered. ie., the
	# assumption is that the grass is always fully exposed... This need to be addressed in ther future

	rn=rn-grass_rn
	
	if Al<>0:  ### NOT NIGHT   atd added to make Danilo code work??

		nr_sl,nr_sh = NetRad_ground2leaf(tree_den,rn,Al,As);

	else:
		nr_sl = 0
		nr_sh = 0


	# transpiration

	delta=VapPSatCurveSlope(temp)

	##### GOT TO HERE IN CONVERSION

	pres = 101.3

	###  atd add to avoid division by zero
        if gs_sunlit==0: gs_sunlit = 0.00625
	if gs_shaded ==0: gs_shaded = 0.002
	##  end atd add

	Esl=PenmanMontieth(nr_sl,1.0/gs_sunlit,ra,vpd,temp,pres,delta)       #// transpiration rates kg/sec*m2 of LA
	Esh=PenmanMontieth(nr_sh,1.0/gs_shaded,ra,vpd,temp,pres,delta)


#	if Esl < 0 or Esh < 0:
#		print Esl, Esh
#		print temp
#		print vpd
#		print rh
#		print ws
#		print rs
#		print rn
#		print pres
#		print gs_sunlit
#		print gs_shaded

	Esl_LA=Esl*3600.0  #Test to see if this is needed based on input rs        ##// kg/hour*m2LA
	Esh_LA=Esh*3600.0  #Tests to see if this is needed based on input rs       

	Esl=Esl_LA*Al                #// kg/hour total trasnpiration of sunlit leaves
	Esh=Esh_LA*As                #// kg/hour total traspiration of shaded leavers

	E=(Esl+Esh)         #// kg/hour*tree

	tr=E
	
	return tr
