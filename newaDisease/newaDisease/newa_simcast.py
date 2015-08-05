# ----------------------
# simcast 
# ----------------------
# imports
# ----------------------
import sys
#import subprocess
from mx import DateTime
from print_exception import print_exception
import units
from potato_dictionary import potatoD
from tomato_dictionary import tomatoD

# ----------------------
# definitions
# ----------------------
global degF_to_degC,degC_to_degF
degF_to_degC = units.new('degF','degC')
degC_to_degF = units.new('degC','degF')
global mm_to_inch, inch_to_mm
mm_to_inch = units.new('mm','inch')
inch_to_mm = units.new('inch','mm')
global susceptible, moderately_susceptible,moderately_resistant

susceptible  = {
	'hi_tmp' : {	7: 1, 8: 1, 9: 1,
					10: 2, 11: 2, 12: 2,
					13: 3, 14: 3, 15: 3,
					16: 4, 17: 4, 18: 4,
					19: 5, 20: 5, 21: 5, 22: 5, 23: 5, 24: 5},
	'med_hi_tmp' : { 7: 5, 8: 5, 9: 5,
					10: 6, 11: 6, 12: 6,
					13: 7, 14: 7, 15: 7, 16: 7, 17: 7, 18: 7,
					19: 7, 20: 7, 21: 7, 22: 7, 23: 7, 24: 7},
	'med_lo_tmp':  { 7:1,
					 8:2, 9:2,
					10:3,
					11:4, 12:4,
					13:5, 14:5, 15:5,
					16:6, 17:6, 18:6, 19:6,
					20:6, 21:6, 22:6, 23:6, 24:6 },
	'lo_tmp': 	 { 10:1, 11:1, 12:1,
					13:2, 14:2, 15:2,
					16:3, 17:3, 18:3,
					19:4, 20:4, 21:4, 22:4, 23:4, 24:4   },
	'criticalBU': 30,
	'criticalFU': 15}


moderately_susceptible = { 
	'hi_tmp': 	 { 10:1, 11:1, 12:1, 13:1, 14:1, 15:1, 16:1, 17:1, 18:1,
					19:2, 20:2, 21:2, 22:2, 23:2, 24:2   },
	'med_hi_tmp': 	 { 7:1,
					 8:2,
					 9:3,
					10:4,
					11:5, 12:5,
					13:6, 14:6, 15:6, 16:6, 17:6, 18:6, 19:6, 20:6, 21:6, 22:6, 23:6, 24:6   },
	'med_lo_tmp': 	 { 7:1, 8:1, 9:1,
					10:2, 11:2, 12:2,
					13:3, 14:3, 15:3,
					16:4, 17:4, 18:4,
					19:5, 20:5, 21:5, 22:5, 23:5, 24:5   },
	'lo_tmp': 	 { 
					13:1, 14:1, 15:1, 16:1, 17:1, 18:1,
					19:1, 20:1, 21:1, 22:1, 23:1, 24:1   },
	'criticalBU': 35,
	'criticalFU': 17 }

moderately_resistant =  {
	'hi_tmp': 	 { 16:1, 17:1, 18:1, 19:1, 20:1,
					21:1, 22:1, 23:1, 24:1   },
	'med_hi_tmp': 	 { 7:1,
					 8:2,
					 9:3,
					10:4, 11:4, 12:4,
					13:5, 14:5, 15:5, 16:5, 17:5, 18:5,
					19:5, 20:5, 21:5, 22:5, 23:5, 24:5   },
	'med_lo_tmp': 	 { 10:1, 11:1, 12:1,
					13:2, 14:2, 15:2,
					16:3, 17:3, 18:3, 19:3, 20:3,
					21:3, 22:3, 23:3, 24:3   },
	'lo_tmp': 	 { 19:1, 20:1, 21:1, 22:1, 23:1, 24:1   },
	'criticalBU': 40,
	'criticalFU': 25}


def fixDate(date) :
	# --------------------------------------
	# transform date from yyyy-mm-dd to
	# DateTime object
	# --------------------------------------
	if '-' in date :
		date = date.split('-')
		yyyy = int(date[0])
		mm = int(date[1])
		dd = int(date[2])
	elif  '/' in date :
		date = date.split('/')
		yyyy = int(date[2])
		mm = int(date[0])
		dd = int(date[1])
	this_time = DateTime.DateTime(yyyy,mm,dd,10)
	return this_time


class general_simcast(object) :

	def __init__(self) :
		self.missing = -999.0
		self.sas_missing = '.'
		self.threshold = 90 
		self.obs_blight = 0 
		self.obs_fungicide = 0 
		self.fc_blight = 0 
		self.fc_blight_date = ''
		self.fc_fungicide = 0 
		self.fc_fungicide_date = ''
		self.blightList = []
		self.blightCritList = []
		self.blightDateList = []
		self.fungicideList = []
		self.fungicideCritList = []


	def saveBlightTableValues(self,blightUnits,eTime) :
		dateString = "%s/%s"%(eTime.month,eTime.day)
		if len(self.blightList) == 0 :
			self.blightList.append(self.obs_blight)
			lastObs = self.forecast_sTime + DateTime.RelativeDate(days=-1)
			lastDay = "%s/%s"%(lastObs.month,lastObs.day)
			self.blightDateList.append(lastDay)
			if (self.obs_blight >= self.criticalBU) :
				self.blightCritList.append(1)
			else:
				self.blightCritList.append(0)

		critFlag = 0
		if (blightUnits >= self.criticalBU) :
			critFlag = 1
		if  (len(self.blightDateList)>= 2)  :
			previousDateString = self.blightDateList[-1]
			if (previousDateString==dateString) :
				self.blightList[-1] = blightUnits
				self.blightCritList[-1] = critFlag
			else :
				self.blightList.append(blightUnits)
				self.blightDateList.append(dateString)
				self.blightCritList.append(critFlag)
		else :
			self.blightList.append(blightUnits)
			self.blightDateList.append(dateString)
			self.blightCritList.append(critFlag)
			

	def update_blightTableValues(self,monthDay) :
		if len(self.blightList) == 0 :
			lastObs = self.forecast_sTime + DateTime.RelativeDate(days=-1)
			lastDay = "%s/%s"%(lastObs.month,lastObs.day)
			critFlg = 0
			if self.obs_blight > self.criticalBU :
				critFlg = 1

			diff = self.today - lastObs 
			if diff.day == 1 :
				self.blightDateList.append(lastDay)
				self.blightList.append(self.obs_blight)
				self.blightCritList.append(critFlg)
				self.blightDateList.append(monthDay)
				self.blightList.append(self.obs_blight)
				self.blightCritList.append(critFlg)
			elif diff.day == 0 :
				self.blightDateList.append(monthDay)
				self.blightList.append(self.obs_blight)
				self.blightCritList.append(critFlg)

			else :
				print '**** this should never happen',diff.day
				sys.exit()
		else :
			last_blight_value = self.blightList[-1]
			last_crit_value = self.blightCritList[-1]
			self.blightDateList.append(monthDay)
			self.blightList.append(last_blight_value)
			self.blightCritList.append(last_crit_value)


	def saveFungicideTableValues(self,fungicideUnit) :
		monthDay = "%d/%d"%(self.today.month,self.today.day)
		if monthDay not in self.blightDateList :
			self.update_blightTableValues(monthDay)
		if len(self.fungicideList) == 0 :
			self.fungicideList.append(-self.obs_fungicide)
			if (self.obs_fungicide >= self.criticalFU) :
				self.fungicideCritList.append(1)
			else :
				self.fungicideCritList.append(0)
		self.fungicideList.append(-fungicideUnit)
		if (fungicideUnit >= self.criticalFU) :
			self.fungicideCritList.append(1)
		else :
			self.fungicideCritList.append(0)


	def identify_arrays(self,stnWeather) :
		# --------------------------------
		# date format:	(year, month, day, hour)
		# tmp unit:		degF
		# 				we work with both degF  and degC
		# prcp unit:	mm  
		#				we work with both mm and inches
		# rh unit:		percent 
		# --------------------------------
		self.dates = stnWeather['dates']
		self.tmp = stnWeather['tmpF']
		self.rh = stnWeather['rh'] 
		self.prcp = stnWeather['prcpMM']
		self.flags = stnWeather['flags']
		
	def get_fungicide_times(self,all_fungicide) :
		self.fungicide = {}
#		print 'get_fungicide_times',all_fungicide
		# TEMPORARY  FIX LJJ   pounds = 1.5
		pounds = 1.5
		# For NEWA, we will only have, at most, a single fungicide date -KLE
		if all_fungicide:
			fungicideTime = fixDate(all_fungicide)
			self.fungicide[fungicideTime] = pounds
			self.firstFungicideApp = fungicideTime
		else:
			self.firstFungicideApp = None


	def get_blitecast_time(self) :
		self.bliteCritTime = None
	

	def establish_report_startTime(self) :
		self.report_sTime = None
		if ( ( self.firstFungicideApp != None) and (self.bliteCritTime != None) ) :
			if self.bliteCritTime <  self.firstFungicideApp :
				self.report_sTime = self.bliteCritTime
			else :
				self.report_sTime = self.firstFungicideApp
		elif (self.firstFungicideApp != None) :
			self.report_sTime = self.firstFungicideApp
		elif (self.bliteCritTime != None) :
			self.report_sTime = self.bliteCritTime

		
	def identify_blight_dictionary(self,resistance) :
		resistance = resistance.strip()
		if resistance == 'susceptible'  :
			self.blight_dictionary = susceptible
		elif resistance == 'moderately susceptible': 
			self.blight_dictionary = moderately_susceptible
		elif resistance == 'moderately resistant' : 
			self.blight_dictionary = moderately_resistant
		else :
			print 'unknown resistance',resistance
			sys.exit()
		self.resistance = resistance
		self.criticalBU = self.blight_dictionary['criticalBU']
		self.criticalFU = self.blight_dictionary['criticalFU']
		
	def init_season_counters(self) :
		self.season_blight_units = 0
		self.season_fung_units = 0
	
	def init_blight_units(self) :
		self.postFung_blight_units= 0

	def init_wet_counters(self) :
		self.rh_hours = 0
		self.tmp_accum = 0.0
		self.wet_start = None
		self.wet_end = None

	def init_fungicide_units(self) :
		self.postFung_fung_units = 0

	def init_daily_prcp(self) :
		self.daily_prcp = 0.0
	
	def init_missing_flg(self) :
		# 
		# daily_missing_flg:
		#	 we have missing data = 1 
		#	 no missing data = 0	
		#
		# missP number of  missing prcp  hours
		# missT number  of  missing  temp  hours
		# missR  number  of  missing  rh  hours
		#
		self.daily_missing_flg = 0  
		self.missP = 0
		self.missT = 0
		self.missR = 0


	def increment_wet_counters(self,tmp) :
		self.rh_hours = self.rh_hours + 1
		self.tmp_accum = self.tmp_accum + tmp
		if self.wet_start == None :
			self.wet_start = self.today 
			self.wet_end = self.today
		else :
			self.wet_end = self.today 


	def increment_prcp(self,precipitation) :
		self.daily_prcp = self.daily_prcp + precipitation

		
	def check_wet_counter(self) :
		if self.rh_hours != 0 :
			ave_tmp = self.tmp_accum/self.rh_hours
			ave_tmp = round(ave_tmp,0)
			ave_tmp = int(ave_tmp)
			blight_units = 0
			try :

			# ---------------------------------------------
			# temp ranges:
			#     hi tmp:   F 73 - 81,  C 23 - 27
			# med_hi_tmp:   F 55 - 72   C 13   22 
			# med_lo_tmp:   F 46 - 54   C 8    12 
			#     lo_tmp:   F 37 - 45   C 3    7 
			# ---------------------------------------------
				if ( (ave_tmp >= 23) and (ave_tmp <= 27) ) :
					TmpType = 'hi_tmp'
				elif ( ( ave_tmp >= 13) and (ave_tmp <= 22) ) :
					TmpType = 'med_hi_tmp'
				elif ( (ave_tmp >= 8) and (ave_tmp <= 12) ) :
					TmpType = "med_lo_tmp"
				elif ( ( ave_tmp >= 3) and (ave_tmp <= 7) ) :
					TmpType = "lo_tmp"
		
				else :
					TmpType = None
				
				if TmpType :

					all_unit_dictionary = self.blight_dictionary[TmpType]
					if self.rh_hours in all_unit_dictionary :
						blight_units = all_unit_dictionary[self.rh_hours]

						self.postFung_blight_units = self.postFung_blight_units + blight_units
						self.season_blight_units = self.season_blight_units + blight_units


				sDate = (self.wet_start.year,self.wet_start.month,self.wet_start.day,self.wet_start.hour)
				eDate = (self.wet_end.year,self.wet_end.month,self.wet_end.day,self.wet_end.hour)
				# --------------------------------------------------
				# Update 7/7/2011:
				# weather changed  to local time in  weather programs
				# --------------------------------------------------
				sTime = apply(DateTime.Date,sDate)
				eTime = apply(DateTime.Date,eDate)
					
				report_eTime = eTime + DateTime.RelativeDate(hours=+1)
				if report_eTime > sTime  :
					# ------------------------------------------------
					# Each Line:
					#	bkgrnd mFlg sevFlg buFlg fuFlg 
					#	date fung wetS wetE hrs tmp BUd BU BUseason 
					#	rain FUd FU FUseason
					# ------------------------------------------------
					if eTime >= self.forecast_day3 :
						backgroundFlg = 'y'
					elif eTime >=self.forecast_sTime :
						backgroundFlg = 'o'
					else :
						backgroundFlg = 'w'
					bFlg =  backgroundFlg
					if ( (self.postFung_blight_units >= self.criticalBU) and
					(eTime >= self.criticalTime) ) :
						bFlg = backgroundFlg +  'b'

					fuFlg = backgroundFlg
					flagInfo  = '%s,.,.,%s,%s,.,'%(backgroundFlg,bFlg,fuFlg)
					ave_tmp = degC_to_degF.convert(ave_tmp)
					s_time = "%s/%s %s"%(sTime.month,sTime.day,sTime.hour)
					e_time = "%s/%s %s"%(eTime.month,eTime.day,eTime.hour)
					bliteInfo =  ".,.,%s,%s,%s,"%(s_time,e_time,self.rh_hours)
					bliteInfo = bliteInfo + "%5.1f,%s,"%(ave_tmp,blight_units)
					bliteInfo = bliteInfo + "%s,"%(self.postFung_blight_units)
					bliteInfo = bliteInfo + "%s,"%(self.season_blight_units)
					fungInfo = '.,.,.,.\n'
					outStr = flagInfo + bliteInfo + fungInfo
					self.table_info.append(outStr)
					
					#
					# We are saving the following for disease alerts
					#
					if ( (eTime >=self.forecast_sTime) and (eTime <=self.final_fc_eTime )) :
						self.fc_blight_date = "%s/%s"%(eTime.month,eTime.day)
						self.fc_blight = self.postFung_blight_units
						self.saveBlightTableValues(self.fc_blight,eTime)
					elif (eTime >= self.forecast_sTime) :
						self.saveBlightTableValues(self.postFung_blight_units,eTime)
					elif (eTime < self.forecast_sTime) :
						self.obs_blight = self.postFung_blight_units
			
				self.init_wet_counters()
			except :
				print_exception()
				print 'hours',self.rh_hours
				sys.exit()

	def fix_day(self) :
		forecastFlg = 'no'

		backgroundFlg = 'w'
		if ((self.fungicideTime != None) and (self.today.year,self.today.month,self.today.day) == (self.fungicideTime.year,self.fungicideTime.month,self.fungicideTime.day)) :
				backgroundFlg = 'g'
		elif self.today >= self.final_fc_eTime :
			backgroundFlg = 'y'
			forecastFlg = 'fc_caution'
		elif self.today >= self.forecast_sTime :
			backgroundFlg = 'o'
			forecastFlg = 'fc'

		yyyy = self.today.year
		mm = self.today.month
		dd = self.today.day
		self.day = DateTime.DateTime(yyyy,mm,dd)
		today = "%s/%s"%(mm,dd)
		if self.bliteCritTime == self.day :
			sevFlg = 's'
		else :
			sevFlg = '.'

		missFlg = '.'
		if forecastFlg == 'no' and self.daily_missing_flg > 0 :
			missFlg = 'm'

		compareTime = DateTime.DateTime(yyyy,mm,dd,10)
		if compareTime  == self.fungicideTime :
			dose = self.fungicide[self.fungicideTime]	
			fungVal = "%s"%(dose)
		else :
			fungVal = '.'

		dayInfo = (backgroundFlg,sevFlg,missFlg,today,fungVal)

		return (dayInfo,forecastFlg)

		
	def get_fungicide_units(self) :
		fungicide_units = 0
		days = None	
		diff = self.day - self.fungicideDay
		days = diff.day


		if days == 1 :
			# -------------------------------------
			# we're going to have to know the hour of
			# application to know the day to use as
			# application day! 
			# -------------------------------------
			#self.init_fungicide_units()
			if  (self.daily_prcp <1) :
				fungicide_units = 1
			elif ( (self.daily_prcp >=1) and (self.daily_prcp < 1.5) ) :
				fungicide_units = 4
			elif ( (self.daily_prcp >=1.5) and (self.daily_prcp < 3.5) ) :
				fungicide_units = 5
			elif ( (self.daily_prcp >=3.5) and (self.daily_prcp <= 6.0 ) ) :
				fungicide_units = 6
			elif (self.daily_prcp > 6.0) :
				fungicide_units = 7

		elif days == 2 :
			if (self.daily_prcp < 1) :
				fungicide_units = 1
			elif ( (self.daily_prcp >=1) and (self.daily_prcp < 1.5) ) :
				fungicide_units = 3
			elif ( (self.daily_prcp >=1.5) and (self.daily_prcp < 4.5) ) :
				fungicide_units = 4
			elif ( (self.daily_prcp >=4.5) and (self.daily_prcp <= 8) ) :
				fungicide_units = 5 
			elif (self.daily_prcp > 8)  :
				fungicide_units = 6

		elif days == 3 :
			if (self.daily_prcp < 1) :
				fungicide_units = 1
			elif ( (self.daily_prcp >=1) and (self.daily_prcp < 2.5) ) :
				fungicide_units = 3
			elif ( (self.daily_prcp >=2.5) and (self.daily_prcp <= 5.0) ) :
				fungicide_units = 4
			elif (self.daily_prcp > 5)  :
				fungicide_units = 5

		elif ( (days >= 4) and (days <= 5 ) ):
			if (self.daily_prcp < 1) :
				fungicide_units = 1
			elif ( (self.daily_prcp >=1) and (self.daily_prcp < 2.5) ) :
				fungicide_units = 3
			elif ( (self.daily_prcp >=2.5) and (self.daily_prcp <= 8.0) ) :
				fungicide_units = 4
			elif (self.daily_prcp > 8)  :
				fungicide_units = 5

		elif ( (days >= 6) and (days <= 9 ) ):
			if (self.daily_prcp < 1) :
				fungicide_units=1
			elif ( (self.daily_prcp >=1) and (self.daily_prcp <= 4) ) :
				fungicide_units = 3
			elif (self.daily_prcp > 4)  :
				fungicide_units = 4

		elif ( (days >= 10) and (days <= 14 ) ):
			if (self.daily_prcp < 1) :
				fungicide_units = 1
			elif ( (self.daily_prcp >=1) and (self.daily_prcp < 1.5) ) :
				fungicide_units = 2
			elif ( (self.daily_prcp >=1.5) and (self.daily_prcp <= 8 ) ) :
				fungicide_units = 3
			elif (self.daily_prcp > 8)  :
				fungicide_units = 4

		elif days > 14:
			if (self.daily_prcp < 1) :
				fungicide_units = 1
			elif ( (self.daily_prcp >= 1)   and (self.daily_prcp <= 8) ) :
				fungicide_units = 2
			elif self.daily_prcp > 8 :
				fungicide_units = 3
		return (days,fungicide_units)
		

	def process_daily_events(self) :
		(dayInfo,forecastFlg) = self.fix_day()
		(backgroundFlg,sevFlg,missFlg,today,fungVal) = dayInfo

		if missFlg == 'm' :
			# ------------------------------------------------
			# Each Line:
			#	bkgrnd mFlg sevFlg buFlg fuFlg
			#	date fung wetS wetE hrs tmp
			#   BUd BU BUseason	rain FUd FU FUseason
			# ------------------------------------------------
			thisBackGround = backgroundFlg
			if forecastFlg == 'no'  and backgroundFlg == 'g' :
				thisBackGround = 'w'
			flags = '%s,%s,.,.,.,.,'%(thisBackGround,missFlg)
			missT_section = 'missing,.,.,.,.,%s hrs,'%(self.missT)
			missP_section = '.,.,.,%s hrs,.,.,.\n'%(self.missP)
			outStr = flags+missT_section + missP_section
			self.table_info.append(outStr)
			missFlg = '.'
			
		self.init_missing_flg()

		if self.fungicideDay :
			(days,fungicide_units) = self.get_fungicide_units()
			self.postFung_fung_units = self.postFung_fung_units + fungicide_units
			self.season_fung_units = self.season_fung_units + fungicide_units

		if forecastFlg == 'fc_caution' :
			reported_prcp = '.'
		else :
			reported_prcp = mm_to_inch.convert(self.daily_prcp)
			reported_prcp = "%6.2f"%(reported_prcp)
			reported_prcp = reported_prcp.strip()
				
		#
		#	weather must be missing
		#

		fUnitsFlg = backgroundFlg
		if not self.fungicideDay :
			fUnits_daily  = '.'
			fUnits_post = '.'
			fUnits_season = '.'

		elif days :
			fUnits_daily =  '-%d'%(fungicide_units)
			fUnits_post = '-%d'%(self.postFung_fung_units)
			fUnits_season = '-%d'%(self.season_fung_units) 
			if ( (self.postFung_fung_units>self.criticalFU) and
			(self.day >= self.criticalDay) ) :
				fUnitsFlg = fUnitsFlg +  "f"
		else :
			fUnits_daily = "0"
			fUnits_post = "0"
			fUnits_season = "-%d"%(self.season_fung_units)

		# ------------------------------------------------
		# Each Line:
		#	bkgrnd mFlg sevFlg buFlg fuFlg
		#	date fung wetS wetE hrs tmp BUd BU BUseason 
		#	rain FUd FU FUseason
		# ------------------------------------------------
		bFlg = backgroundFlg
		flagInfo  = "%s,%s,%s,%s,%s"%(backgroundFlg,missFlg,sevFlg,bFlg,fUnitsFlg)
		fungStart = "%s,%s,"%(today,fungVal)
		blightInfo = ".,.,.,.,.,.,.,"
		fungEnd = "%s,%s,%s,%s\n"%(reported_prcp,fUnits_daily,fUnits_post,fUnits_season)
		
		outStr = flagInfo + fungStart + blightInfo + fungEnd
		self.table_info.append(outStr)
			
		#
		#  Note :  we are now saving information for disease alerts
		#
			
		if ( (self.today  >= self.forecast_sTime) and (self.today <= self.final_fc_eTime)) :
			self.fc_fungicide_date = "%02d/%02d/%d"%(self.today.month,self.today.day,self.today.year)
			self.fc_fungicide = self.postFung_fung_units
			self.saveFungicideTableValues(self.fc_fungicide)
		elif ( self.today >= self.forecast_sTime) :
			self.saveFungicideTableValues(self.postFung_fung_units)
		elif (self.today < self.forecast_sTime) :	
			self.obs_fungicide = self.postFung_fung_units
		self.init_daily_prcp()
		

	def write_blight_table_info(self) :
		self.table_info.reverse()
#		for line in self.table_info :
#			sys.stdout.write(line)


	def loop_through_days(self) :
		self.table_info = []
		self.init_missing_flg()
		fungicide_apps = self.fungicide.keys()
		fungicide_apps.sort()
		if len(fungicide_apps) > 0 :
			self.fungicideTime = fungicide_apps[0]
			self.fungicideDay = DateTime.DateTime(self.fungicideTime.year,self.fungicideTime.month,self.fungicideTime.day)
			self.criticalTime = self.fungicideTime + DateTime.RelativeDateTime(days=+5)
			self.criticalDay = DateTime.DateTime(self.criticalTime.year,self.criticalTime.month,self.criticalTime.day)
		else :
			self.fungicideTime = None
			self.fungicideDay = None
			self.criticalTime = None
			self.criticalDay = None
		index = 0
		self.init_blight_units()
		self.init_fungicide_units()
		self.init_season_counters()

		self.init_wet_counters()
		self.init_daily_prcp()

		#
		# figure out  when  this  report  should  actually start
		#

		self.today = DateTime.DateTime(self.sTime.year,self.sTime.month,self.sTime.day,self.sTime.hour)
		while self.today <= self.eTime :
			if self.today <  self.report_sTime :
				self.today = self.today + DateTime.RelativeDate(hours=+1)
				index = index + 1
				continue
			if self.today in fungicide_apps :
				self.fungicideTime = self.today
				self.init_blight_units()
				self.init_fungicide_units()
				self.fungicideDay = DateTime.DateTime(self.fungicideTime.year,self.fungicideTime.month,self.fungicideTime.day)
				self.criticalTime = self.fungicideTime + DateTime.RelativeDateTime(days=+5)
				self.criticalDay = DateTime.DateTime(self.criticalTime.year,self.criticalTime.month,self.criticalTime.day)

			this_rh = self.rh[index]
			this_tmp = 	self.tmp[index]
			this_prcp = self.prcp[index]
			this_flag = self.flags[index]
			if this_prcp != self.missing :
				self.increment_prcp(this_prcp)
			else :
				self.daily_missing_flg = 1
				self.missP = self.missP+1
				
			if ( (this_rh != self.missing) and (this_tmp != self.missing) and
			(this_rh >= self.threshold) ):
				this_tmp = degF_to_degC.convert(this_tmp)
				self.increment_wet_counters(this_tmp)

				if self.today.hour == 11 :
					self.check_wet_counter()
					self.process_daily_events()

			else :
				if this_rh == self.missing :
					self.missR = self.missR + 1
					self.daily_missing_flg = 1
				if this_tmp == self.missing :
					self.missT = self.missT + 1
					self.daily_missing_flg = 1
				if self.today.hour == 11 :
					self.check_wet_counter()
					self.process_daily_events()
				else :
					self.check_wet_counter()
				

			self.today = self.today + DateTime.RelativeDate(hours=+1)
			index = index + 1
		self.check_wet_counter()
		
				
	def get_weather_data(self) :
		if len(self.dates) == 0 :
			print 'missing weather'
			sys.exit()

		self.forecast_day3 = self.forecast_sTime + DateTime.RelativeDate(days=+3)
		last_date = self.dates[-1]
		(yyyy,mm,dd,hh) = last_date
		self.fc_end = "%s/%s/%s"%(mm,dd,yyyy)
			 
		first_date = self.dates[0]
		self.sTime = apply(DateTime.Date,first_date)
		self.eTime = apply(DateTime.Date,last_date)


	def process_simcast(self,stn_name,resistance,doseVars,stnWeather) :
#		print 'here in general simcast'
		resultsD = {'length':0}

		try:
			self.identify_arrays(stnWeather)
			self.stn_name = stn_name
				
			if resistance == None :
#				print 'None branch',resistance
				self.resistance = None
			else :
				if 'fc_time' in stnWeather :	
					self.forecast_sTime = stnWeather['fc_time']
				elif 'forecastDayDate' in stnWeather :
					forecastDayDate = stnWeather['forecastDayDate']
					self.forecast_sTime = apply(DateTime.Date,forecastDayDate)
				self.final_fc_eTime = self.forecast_sTime + DateTime.RelativeDate(days=+3)
		
				self.identify_blight_dictionary(resistance)
				self.get_fungicide_times(doseVars)
				self.get_blitecast_time()
				self.establish_report_startTime()

			resultsD = self.finish_up()
		except:
			print_exception()
		return resultsD

			
	def finish_up(self) :		
#		print 'in finish up'
		resultsD = {'length':0}
		if self.report_sTime:
			self.get_weather_data()
#			print 'loop through days'
			self.loop_through_days()
			self.write_blight_table_info()
			bLength = len(self.blightList)
			fLength = len(self.fungicideList)
			length = min(bLength,fLength)
			resultsD = {'criticalBU': self.criticalBU,
				'length': length,
				'criticalFU': self.criticalFU,
				'bliteVals': self.blightList,
				'bliteCrit': self.blightCritList,
				'dates': self.blightDateList,
				'fungicideVals': self.fungicideList,
				'fungicideCrit': self.fungicideCritList}
		return resultsD
#		print 'finished'

	def get_potato_status(self, name) :
		if name == "" :
			return ('','')
		if name in potatoD :
			infoForName = potatoD[name]
		elif name in tomatoD :
			infoForName = tomatoD[name]
		else :
			return ('','')
		resistance = infoForName['resistance']
		maturity = infoForName['maturity']
		return (resistance,maturity)


#def run_simcast(stn,year,month,day,fDate,cultivar):
#	results = {}
#	try:
#		#initialize weather data dictionary
#		stnWeather = {'dates': [], 'forecastDayDate': None, 'tmpF': [], 'flags': [], 'prcpMM': [], 'rh': [] }
#
#		# obtain resisance of cultivar
#		(resistance,maturity) = general_simcast().get_potato_status(cultivar)
#
#		# setup dates
#		start_date_dt = DateTime.DateTime(year,month,day,0)
#		stnWeather['forecastDayDate'] = (start_date_dt.year,start_date_dt.month,start_date_dt.day)
#		end_date_dt = start_date_dt + DateTime.RelativeDate(days=+6) + DateTime.RelativeDate(hour=23,minute=0,second=0.0)
#
#		# determine station type
#		if stn[0:1] >= '1' and stn[0:1] <= '9' and stn[1:2] >= '0' and stn[1:2] <= '9':
#			station_type = 'njwx'
#		if len(stn) == 3:
#			station_type = 'newa'
#		elif len(stn) == 4:
#			station_type = 'icao'
#		elif len(stn) == 6:
#			station_type = 'cu_log'
#		else:
#			print 'Cannot determine station type for %s'%stn
#			sys.exit()
#
#		# get station name from metadata
#		ucanid, station_name = get_metadata (stn, station_type)
#		
#		# get hourly data
#		fDate_dt = fixDate(fDate)
#		start_input_dt = min(start_date_dt, fDate_dt)
#		hourly_data = collect_hourly_input(stn, start_input_dt, end_date_dt, ['temp','prcp','rhum'], station_type)
#		ks = hourly_data.keys()
#		# and format it for simcast use
#		if len(ks) > 0:
#			ks.sort()
#			for key_date in ks:
#				#print key_date,hourly_data[key_date]
#				#these times are in LT. Convert to EST for simcast.
#				theTime_dt = DateTime.DateTime(*key_date)
#				theTime_dt = theTime_dt + DateTime.RelativeDate(hours=-theTime_dt.dst)
#				est = (theTime_dt.year,theTime_dt.month,theTime_dt.day,theTime_dt.hour)
#				stnWeather['dates'].append(est)
#				stnWeather['tmpF'].append(hourly_data[key_date]['temp'][0])
#				if hourly_data[key_date]['prcp'][0] != -999:
#					prcp = inch_to_mm.convert(hourly_data[key_date]['prcp'][0])
#				else:
#					prcp = -999
#				stnWeather['prcpMM'].append(prcp)
#				if hourly_data[key_date]['rhum'][1] == "F":
#					stnWeather['rh'].append(min(100,hourly_data[key_date]['rhum'][0]+15))
#				else:
#					stnWeather['rh'].append(hourly_data[key_date]['rhum'][0])
#				stnWeather['flags'].append(hourly_data[key_date]['prcp'][1])
#			results = general_simcast().process_simcast(station_name,resistance,fDate,stnWeather) 
#		else:
#			return newaCommon_io.nodata()
#
#		if results.has_key('length') and results['length'] > 0:
#			print 'results:',results
###			return newaTester_io.potato_lb_html(station_name,download_time,wet_periods)
#		else:
#			return newaCommon_io.nodata()
#	except:
#		print_exception()
#		return newaCommon_io.errmsg('Unable to complete request')


#if __name__=='__main__':
#	if '/Users/keith/kleWeb/newaCommon' not in sys.path: sys.path.insert(1,'/Users/keith/kleWeb/newaCommon')
#	import newaCommon_io
#	from newaCommon import *
#	stn = 'ith'
#	year = 2012
#	month = 5
#	day = 7
#	fDate =  '04/25/2012'
#	cultivar = "Bake King"
#	run_simcast(stn,year,month,day,fDate,cultivar)


#Sample data dictionary
#			stnWeather = { 'dates': [(2012, 3, 1, 0), (2012, 3, 1, 1), (2012, 3, 1, 2), (2012, 3, 1, 3), (2012, 3, 1, 4), (2012, 3, 1, 5), (2012, 3, 1, 6), (2012, 3, 1, 7), (2012, 3, 1, 8), (2012, 3, 1, 9), (2012, 3, 1, 10), (2012, 3, 1, 11), (2012, 3, 1, 12), (2012, 3, 1, 13), (2012, 3, 1, 14), (2012, 3, 1, 15), (2012, 3, 1, 16), (2012, 3, 1, 17), (2012, 3, 1, 18), (2012, 3, 1, 19), (2012, 3, 1, 20), (2012, 3, 1, 21), (2012, 3, 1, 22), (2012, 3, 1, 23), (2012, 3, 2, 0), (2012, 3, 2, 1), (2012, 3, 2, 2), (2012, 3, 2, 3), (2012, 3, 2, 4), (2012, 3, 2, 5), (2012, 3, 2, 6), (2012, 3, 2, 7), (2012, 3, 2, 8), (2012, 3, 2, 9), (2012, 3, 2, 10), (2012, 3, 2, 11), (2012, 3, 2, 12), (2012, 3, 2, 13), (2012, 3, 2, 14), (2012, 3, 2, 15), (2012, 3, 2, 16), (2012, 3, 2, 17), (2012, 3, 2, 18), (2012, 3, 2, 19), (2012, 3, 2, 20), (2012, 3, 2, 21), (2012, 3, 2, 22), (2012, 3, 2, 23), (2012, 3, 3, 0), (2012, 3, 3, 1), (2012, 3, 3, 2), (2012, 3, 3, 3), (2012, 3, 3, 4), (2012, 3, 3, 5), (2012, 3, 3, 6), (2012, 3, 3, 7), (2012, 3, 3, 8), (2012, 3, 3, 9), (2012, 3, 3, 10), (2012, 3, 3, 11), (2012, 3, 3, 12), (2012, 3, 3, 13), (2012, 3, 3, 14), (2012, 3, 3, 15), (2012, 3, 3, 16), (2012, 3, 3, 17), (2012, 3, 3, 18), (2012, 3, 3, 19), (2012, 3, 3, 20), (2012, 3, 3, 21), (2012, 3, 3, 22), (2012, 3, 3, 23), (2012, 3, 4, 0), (2012, 3, 4, 1), (2012, 3, 4, 2), (2012, 3, 4, 3), (2012, 3, 4, 4), (2012, 3, 4, 5), (2012, 3, 4, 6), (2012, 3, 4, 7), (2012, 3, 4, 8), (2012, 3, 4, 9), (2012, 3, 4, 10), (2012, 3, 4, 11), (2012, 3, 4, 12), (2012, 3, 4, 13), (2012, 3, 4, 14), (2012, 3, 4, 15), (2012, 3, 4, 16), (2012, 3, 4, 17), (2012, 3, 4, 18), (2012, 3, 4, 19), (2012, 3, 4, 20), (2012, 3, 4, 21), (2012, 3, 4, 22), (2012, 3, 4, 23), (2012, 3, 5, 0), (2012, 3, 5, 1), (2012, 3, 5, 2), (2012, 3, 5, 3), (2012, 3, 5, 4), (2012, 3, 5, 5), (2012, 3, 5, 6), (2012, 3, 5, 7), (2012, 3, 5, 8), (2012, 3, 5, 9), (2012, 3, 5, 10), (2012, 3, 5, 11), (2012, 3, 5, 12), (2012, 3, 5, 13), (2012, 3, 5, 14), (2012, 3, 5, 15), (2012, 3, 5, 16), (2012, 3, 5, 17), (2012, 3, 5, 18), (2012, 3, 5, 19), (2012, 3, 5, 20), (2012, 3, 5, 21), (2012, 3, 5, 22), (2012, 3, 5, 23), (2012, 3, 6, 0), (2012, 3, 6, 1), (2012, 3, 6, 2), (2012, 3, 6, 3), (2012, 3, 6, 4), (2012, 3, 6, 5), (2012, 3, 6, 6), (2012, 3, 6, 7), (2012, 3, 6, 8), (2012, 3, 6, 9), (2012, 3, 6, 10), (2012, 3, 6, 11), (2012, 3, 6, 12), (2012, 3, 6, 13), (2012, 3, 6, 14), (2012, 3, 6, 15), (2012, 3, 6, 16), (2012, 3, 6, 17), (2012, 3, 6, 18), (2012, 3, 6, 19), (2012, 3, 6, 20), (2012, 3, 6, 21), (2012, 3, 6, 22), (2012, 3, 6, 23), (2012, 3, 7, 0), (2012, 3, 7, 1), (2012, 3, 7, 2), (2012, 3, 7, 3), (2012, 3, 7, 4), (2012, 3, 7, 5), (2012, 3, 7, 6), (2012, 3, 7, 7), (2012, 3, 7, 8), (2012, 3, 7, 9), (2012, 3, 7, 10), (2012, 3, 7, 11), (2012, 3, 7, 12), (2012, 3, 7, 13), (2012, 3, 7, 14), (2012, 3, 7, 15), (2012, 3, 7, 16), (2012, 3, 7, 17), (2012, 3, 7, 18), (2012, 3, 7, 19), (2012, 3, 7, 20), (2012, 3, 7, 21), (2012, 3, 7, 22), (2012, 3, 7, 23), (2012, 3, 8, 0), (2012, 3, 8, 1), (2012, 3, 8, 2), (2012, 3, 8, 3), (2012, 3, 8, 4), (2012, 3, 8, 5), (2012, 3, 8, 6), (2012, 3, 8, 7), (2012, 3, 8, 8), (2012, 3, 8, 9), (2012, 3, 8, 10), (2012, 3, 8, 11), (2012, 3, 8, 12), (2012, 3, 8, 13), (2012, 3, 8, 14), (2012, 3, 8, 15), (2012, 3, 8, 16), (2012, 3, 8, 17), (2012, 3, 8, 18), (2012, 3, 8, 19), (2012, 3, 8, 20), (2012, 3, 8, 21), (2012, 3, 8, 22), (2012, 3, 8, 23), (2012, 3, 9, 0), (2012, 3, 9, 1), (2012, 3, 9, 2), (2012, 3, 9, 3), (2012, 3, 9, 4), (2012, 3, 9, 5), (2012, 3, 9, 6), (2012, 3, 9, 7), (2012, 3, 9, 8), (2012, 3, 9, 9), (2012, 3, 9, 10), (2012, 3, 9, 11), (2012, 3, 9, 12), (2012, 3, 9, 13), (2012, 3, 9, 14), (2012, 3, 9, 15), (2012, 3, 9, 16), (2012, 3, 9, 17), (2012, 3, 9, 18), (2012, 3, 9, 19), (2012, 3, 9, 20), (2012, 3, 9, 21), (2012, 3, 9, 22), (2012, 3, 9, 23), (2012, 3, 10, 0), (2012, 3, 10, 1), (2012, 3, 10, 2), (2012, 3, 10, 3), (2012, 3, 10, 4), (2012, 3, 10, 5), (2012, 3, 10, 6), (2012, 3, 10, 7), (2012, 3, 10, 8), (2012, 3, 10, 9), (2012, 3, 10, 10), (2012, 3, 10, 11), (2012, 3, 10, 12), (2012, 3, 10, 13), (2012, 3, 10, 14), (2012, 3, 10, 15), (2012, 3, 10, 16), (2012, 3, 10, 17), (2012, 3, 10, 18), (2012, 3, 10, 19), (2012, 3, 10, 20), (2012, 3, 10, 21), (2012, 3, 10, 22), (2012, 3, 10, 23), (2012, 3, 11, 0), (2012, 3, 11, 1), (2012, 3, 11, 2), (2012, 3, 11, 3), (2012, 3, 11, 4), (2012, 3, 11, 5), (2012, 3, 11, 6), (2012, 3, 11, 7), (2012, 3, 11, 8), (2012, 3, 11, 9), (2012, 3, 11, 10), (2012, 3, 11, 11), (2012, 3, 11, 12), (2012, 3, 11, 13), (2012, 3, 11, 14), (2012, 3, 11, 15), (2012, 3, 11, 16), (2012, 3, 11, 17), (2012, 3, 11, 18), (2012, 3, 11, 19), (2012, 3, 11, 20), (2012, 3, 11, 21), (2012, 3, 11, 22), (2012, 3, 11, 23), (2012, 3, 12, 0), (2012, 3, 12, 1), (2012, 3, 12, 2), (2012, 3, 12, 3), (2012, 3, 12, 4), (2012, 3, 12, 5), (2012, 3, 12, 6), (2012, 3, 12, 7), (2012, 3, 12, 8), (2012, 3, 12, 9), (2012, 3, 12, 10), (2012, 3, 12, 11), (2012, 3, 12, 12), (2012, 3, 12, 13), (2012, 3, 12, 14), (2012, 3, 12, 15), (2012, 3, 12, 16), (2012, 3, 12, 17), (2012, 3, 12, 18), (2012, 3, 12, 19), (2012, 3, 12, 20), (2012, 3, 12, 21), (2012, 3, 12, 22), (2012, 3, 12, 23), (2012, 3, 13, 0), (2012, 3, 13, 1), (2012, 3, 13, 2), (2012, 3, 13, 3), (2012, 3, 13, 4), (2012, 3, 13, 5), (2012, 3, 13, 6), (2012, 3, 13, 7), (2012, 3, 13, 8), (2012, 3, 13, 9), (2012, 3, 13, 10), (2012, 3, 13, 11), (2012, 3, 13, 12), (2012, 3, 13, 13), (2012, 3, 13, 14), (2012, 3, 13, 15), (2012, 3, 13, 16), (2012, 3, 13, 17), (2012, 3, 13, 18), (2012, 3, 13, 19), (2012, 3, 13, 20), (2012, 3, 13, 21), (2012, 3, 13, 22), (2012, 3, 13, 23), (2012, 3, 14, 0), (2012, 3, 14, 1), (2012, 3, 14, 2), (2012, 3, 14, 3), (2012, 3, 14, 4), (2012, 3, 14, 5), (2012, 3, 14, 6), (2012, 3, 14, 7), (2012, 3, 14, 8), (2012, 3, 14, 9), (2012, 3, 14, 10), (2012, 3, 14, 11), (2012, 3, 14, 12), (2012, 3, 14, 13), (2012, 3, 14, 14), (2012, 3, 14, 15), (2012, 3, 14, 16), (2012, 3, 14, 17), (2012, 3, 14, 18), (2012, 3, 14, 19), (2012, 3, 14, 20), (2012, 3, 14, 21), (2012, 3, 14, 22), (2012, 3, 14, 23), (2012, 3, 15, 0), (2012, 3, 15, 1), (2012, 3, 15, 2), (2012, 3, 15, 3), (2012, 3, 15, 4), (2012, 3, 15, 5), (2012, 3, 15, 6), (2012, 3, 15, 7), (2012, 3, 15, 8), (2012, 3, 15, 9), (2012, 3, 15, 10), (2012, 3, 15, 11), (2012, 3, 15, 12), (2012, 3, 15, 13), (2012, 3, 15, 14), (2012, 3, 15, 15), (2012, 3, 15, 16), (2012, 3, 15, 17), (2012, 3, 15, 18), (2012, 3, 15, 19), (2012, 3, 15, 20), (2012, 3, 15, 21), (2012, 3, 15, 22), (2012, 3, 15, 23), (2012, 3, 16, 0), (2012, 3, 16, 1), (2012, 3, 16, 2), (2012, 3, 16, 3), (2012, 3, 16, 4), (2012, 3, 16, 5), (2012, 3, 16, 6), (2012, 3, 16, 7), (2012, 3, 16, 8), (2012, 3, 16, 9), (2012, 3, 16, 10), (2012, 3, 16, 11), (2012, 3, 16, 12), (2012, 3, 16, 13), (2012, 3, 16, 14), (2012, 3, 16, 15), (2012, 3, 16, 16), (2012, 3, 16, 17), (2012, 3, 16, 18), (2012, 3, 16, 19), (2012, 3, 16, 20), (2012, 3, 16, 21), (2012, 3, 16, 22), (2012, 3, 16, 23), (2012, 3, 17, 0), (2012, 3, 17, 1), (2012, 3, 17, 2), (2012, 3, 17, 3), (2012, 3, 17, 4), (2012, 3, 17, 5), (2012, 3, 17, 6), (2012, 3, 17, 7), (2012, 3, 17, 8), (2012, 3, 17, 9), (2012, 3, 17, 10), (2012, 3, 17, 11), (2012, 3, 17, 12), (2012, 3, 17, 13), (2012, 3, 17, 14), (2012, 3, 17, 15), (2012, 3, 17, 16), (2012, 3, 17, 17), (2012, 3, 17, 18), (2012, 3, 17, 19), (2012, 3, 17, 20), (2012, 3, 17, 21), (2012, 3, 17, 22), (2012, 3, 17, 23), (2012, 3, 18, 0), (2012, 3, 18, 1), (2012, 3, 18, 2), (2012, 3, 18, 3), (2012, 3, 18, 4), (2012, 3, 18, 5), (2012, 3, 18, 6), (2012, 3, 18, 7), (2012, 3, 18, 8), (2012, 3, 18, 9), (2012, 3, 18, 10), (2012, 3, 18, 11), (2012, 3, 18, 12), (2012, 3, 18, 13), (2012, 3, 18, 14), (2012, 3, 18, 15), (2012, 3, 18, 16), (2012, 3, 18, 17), (2012, 3, 18, 18), (2012, 3, 18, 19), (2012, 3, 18, 20), (2012, 3, 18, 21), (2012, 3, 18, 22), (2012, 3, 18, 23), (2012, 3, 19, 0), (2012, 3, 19, 1), (2012, 3, 19, 2), (2012, 3, 19, 3), (2012, 3, 19, 4), (2012, 3, 19, 5), (2012, 3, 19, 6), (2012, 3, 19, 7), (2012, 3, 19, 8), (2012, 3, 19, 9), (2012, 3, 19, 10), (2012, 3, 19, 11), (2012, 3, 19, 12), (2012, 3, 19, 13), (2012, 3, 19, 14), (2012, 3, 19, 15), (2012, 3, 19, 16), (2012, 3, 19, 17), (2012, 3, 19, 18), (2012, 3, 19, 19), (2012, 3, 19, 20), (2012, 3, 19, 21), (2012, 3, 19, 22), (2012, 3, 19, 23), (2012, 3, 20, 0), (2012, 3, 20, 1), (2012, 3, 20, 2), (2012, 3, 20, 3), (2012, 3, 20, 4), (2012, 3, 20, 5), (2012, 3, 20, 6), (2012, 3, 20, 7), (2012, 3, 20, 8), (2012, 3, 20, 9), (2012, 3, 20, 10), (2012, 3, 20, 11), (2012, 3, 20, 12), (2012, 3, 20, 13), (2012, 3, 20, 14), (2012, 3, 20, 15), (2012, 3, 20, 16), (2012, 3, 20, 17), (2012, 3, 20, 18), (2012, 3, 20, 19), (2012, 3, 20, 20), (2012, 3, 20, 21), (2012, 3, 20, 22), (2012, 3, 20, 23), (2012, 3, 21, 0), (2012, 3, 21, 1), (2012, 3, 21, 2), (2012, 3, 21, 3), (2012, 3, 21, 4), (2012, 3, 21, 5), (2012, 3, 21, 6), (2012, 3, 21, 7), (2012, 3, 21, 8), (2012, 3, 21, 9), (2012, 3, 21, 10), (2012, 3, 21, 11), (2012, 3, 21, 12), (2012, 3, 21, 13), (2012, 3, 21, 14), (2012, 3, 21, 15), (2012, 3, 21, 16), (2012, 3, 21, 17), (2012, 3, 21, 18), (2012, 3, 21, 19), (2012, 3, 21, 20), (2012, 3, 21, 21), (2012, 3, 21, 22), (2012, 3, 21, 23), (2012, 3, 22, 0), (2012, 3, 22, 1), (2012, 3, 22, 2), (2012, 3, 22, 3), (2012, 3, 22, 4), (2012, 3, 22, 5), (2012, 3, 22, 6), (2012, 3, 22, 7), (2012, 3, 22, 8), (2012, 3, 22, 9), (2012, 3, 22, 10), (2012, 3, 22, 11), (2012, 3, 22, 12), (2012, 3, 22, 13), (2012, 3, 22, 14), (2012, 3, 22, 15), (2012, 3, 22, 16), (2012, 3, 22, 17), (2012, 3, 22, 18), (2012, 3, 22, 19), (2012, 3, 22, 20), (2012, 3, 22, 21), (2012, 3, 22, 22), (2012, 3, 22, 23), (2012, 3, 23, 0), (2012, 3, 23, 1), (2012, 3, 23, 2), (2012, 3, 23, 3), (2012, 3, 23, 4), (2012, 3, 23, 5), (2012, 3, 23, 6), (2012, 3, 23, 7), (2012, 3, 23, 8), (2012, 3, 23, 9), (2012, 3, 23, 10), (2012, 3, 23, 11), (2012, 3, 23, 12), (2012, 3, 23, 13), (2012, 3, 23, 14), (2012, 3, 23, 15), (2012, 3, 23, 16), (2012, 3, 23, 17), (2012, 3, 23, 18), (2012, 3, 23, 19), (2012, 3, 23, 20), (2012, 3, 23, 21), (2012, 3, 23, 22), (2012, 3, 23, 23), (2012, 3, 24, 0), (2012, 3, 24, 1), (2012, 3, 24, 2), (2012, 3, 24, 3), (2012, 3, 24, 4), (2012, 3, 24, 5), (2012, 3, 24, 6), (2012, 3, 24, 7), (2012, 3, 24, 8), (2012, 3, 24, 9), (2012, 3, 24, 10), (2012, 3, 24, 11), (2012, 3, 24, 12), (2012, 3, 24, 13), (2012, 3, 24, 14), (2012, 3, 24, 15), (2012, 3, 24, 16), (2012, 3, 24, 17), (2012, 3, 24, 18), (2012, 3, 24, 19), (2012, 3, 24, 20), (2012, 3, 24, 21), (2012, 3, 24, 22), (2012, 3, 24, 23), (2012, 3, 25, 0), (2012, 3, 25, 1), (2012, 3, 25, 2), (2012, 3, 25, 3), (2012, 3, 25, 4), (2012, 3, 25, 5), (2012, 3, 25, 6), (2012, 3, 25, 7), (2012, 3, 25, 8), (2012, 3, 25, 9), (2012, 3, 25, 10), (2012, 3, 25, 11), (2012, 3, 25, 12), (2012, 3, 25, 13), (2012, 3, 25, 14), (2012, 3, 25, 15), (2012, 3, 25, 16), (2012, 3, 25, 17), (2012, 3, 25, 18), (2012, 3, 25, 19), (2012, 3, 25, 20), (2012, 3, 25, 21), (2012, 3, 25, 22), (2012, 3, 25, 23), (2012, 3, 26, 0), (2012, 3, 26, 1), (2012, 3, 26, 2), (2012, 3, 26, 3), (2012, 3, 26, 4), (2012, 3, 26, 5), (2012, 3, 26, 6), (2012, 3, 26, 7), (2012, 3, 26, 8), (2012, 3, 26, 9), (2012, 3, 26, 10), (2012, 3, 26, 11), (2012, 3, 26, 12), (2012, 3, 26, 13), (2012, 3, 26, 14), (2012, 3, 26, 15), (2012, 3, 26, 16), (2012, 3, 26, 17), (2012, 3, 26, 18), (2012, 3, 26, 19), (2012, 3, 26, 20), (2012, 3, 26, 21), (2012, 3, 26, 22), (2012, 3, 26, 23), (2012, 3, 27, 0), (2012, 3, 27, 1), (2012, 3, 27, 2), (2012, 3, 27, 3), (2012, 3, 27, 4), (2012, 3, 27, 5), (2012, 3, 27, 6), (2012, 3, 27, 7), (2012, 3, 27, 8), (2012, 3, 27, 9), (2012, 3, 27, 10), (2012, 3, 27, 11), (2012, 3, 27, 12), (2012, 3, 27, 13), (2012, 3, 27, 14), (2012, 3, 27, 15), (2012, 3, 27, 16), (2012, 3, 27, 17), (2012, 3, 27, 18), (2012, 3, 27, 19), (2012, 3, 27, 20), (2012, 3, 27, 21), (2012, 3, 27, 22), (2012, 3, 27, 23), (2012, 3, 28, 0), (2012, 3, 28, 1), (2012, 3, 28, 2), (2012, 3, 28, 3), (2012, 3, 28, 4), (2012, 3, 28, 5), (2012, 3, 28, 6), (2012, 3, 28, 7), (2012, 3, 28, 8), (2012, 3, 28, 9), (2012, 3, 28, 10), (2012, 3, 28, 11), (2012, 3, 28, 12), (2012, 3, 28, 13), (2012, 3, 28, 14), (2012, 3, 28, 15), (2012, 3, 28, 16), (2012, 3, 28, 17), (2012, 3, 28, 18), (2012, 3, 28, 19), (2012, 3, 28, 20), (2012, 3, 28, 21), (2012, 3, 28, 22), (2012, 3, 28, 23), (2012, 3, 29, 0), (2012, 3, 29, 1), (2012, 3, 29, 2), (2012, 3, 29, 3), (2012, 3, 29, 4), (2012, 3, 29, 5), (2012, 3, 29, 6), (2012, 3, 29, 7), (2012, 3, 29, 8), (2012, 3, 29, 9), (2012, 3, 29, 10), (2012, 3, 29, 11), (2012, 3, 29, 12), (2012, 3, 29, 13), (2012, 3, 29, 14), (2012, 3, 29, 15), (2012, 3, 29, 16), (2012, 3, 29, 17), (2012, 3, 29, 18), (2012, 3, 29, 19), (2012, 3, 29, 20), (2012, 3, 29, 21), (2012, 3, 29, 22), (2012, 3, 29, 23), (2012, 3, 30, 0), (2012, 3, 30, 1), (2012, 3, 30, 2), (2012, 3, 30, 3), (2012, 3, 30, 4), (2012, 3, 30, 5), (2012, 3, 30, 6), (2012, 3, 30, 7), (2012, 3, 30, 8), (2012, 3, 30, 9), (2012, 3, 30, 10), (2012, 3, 30, 11), (2012, 3, 30, 12), (2012, 3, 30, 13), (2012, 3, 30, 14), (2012, 3, 30, 15), (2012, 3, 30, 16), (2012, 3, 30, 17), (2012, 3, 30, 18), (2012, 3, 30, 19), (2012, 3, 30, 20), (2012, 3, 30, 21), (2012, 3, 30, 22), (2012, 3, 30, 23), (2012, 3, 31, 0), (2012, 3, 31, 1), (2012, 3, 31, 2), (2012, 3, 31, 3), (2012, 3, 31, 4), (2012, 3, 31, 5), (2012, 3, 31, 6), (2012, 3, 31, 7), (2012, 3, 31, 8), (2012, 3, 31, 9), (2012, 3, 31, 10), (2012, 3, 31, 11), (2012, 3, 31, 12), (2012, 3, 31, 13), (2012, 3, 31, 14), (2012, 3, 31, 15), (2012, 3, 31, 16), (2012, 3, 31, 17), (2012, 3, 31, 18), (2012, 3, 31, 19), (2012, 3, 31, 20), (2012, 3, 31, 21), (2012, 3, 31, 22), (2012, 3, 31, 23), (2012, 4, 1, 0), (2012, 4, 1, 1), (2012, 4, 1, 2), (2012, 4, 1, 3), (2012, 4, 1, 4), (2012, 4, 1, 5), (2012, 4, 1, 6), (2012, 4, 1, 7), (2012, 4, 1, 8), (2012, 4, 1, 9), (2012, 4, 1, 10), (2012, 4, 1, 11), (2012, 4, 1, 12), (2012, 4, 1, 13), (2012, 4, 1, 14), (2012, 4, 1, 15), (2012, 4, 1, 16), (2012, 4, 1, 17), (2012, 4, 1, 18), (2012, 4, 1, 19), (2012, 4, 1, 20), (2012, 4, 1, 21), (2012, 4, 1, 22), (2012, 4, 1, 23), (2012, 4, 2, 0), (2012, 4, 2, 1), (2012, 4, 2, 2), (2012, 4, 2, 3), (2012, 4, 2, 4), (2012, 4, 2, 5), (2012, 4, 2, 6), (2012, 4, 2, 7), (2012, 4, 2, 8), (2012, 4, 2, 9), (2012, 4, 2, 10), (2012, 4, 2, 11), (2012, 4, 2, 12), (2012, 4, 2, 13), (2012, 4, 2, 14), (2012, 4, 2, 15), (2012, 4, 2, 16), (2012, 4, 2, 17), (2012, 4, 2, 18), (2012, 4, 2, 19), (2012, 4, 2, 20), (2012, 4, 2, 21), (2012, 4, 2, 22), (2012, 4, 2, 23), (2012, 4, 3, 0), (2012, 4, 3, 1), (2012, 4, 3, 2), (2012, 4, 3, 3), (2012, 4, 3, 4), (2012, 4, 3, 5), (2012, 4, 3, 6), (2012, 4, 3, 7), (2012, 4, 3, 8), (2012, 4, 3, 9), (2012, 4, 3, 10), (2012, 4, 3, 11), (2012, 4, 3, 12), (2012, 4, 3, 13), (2012, 4, 3, 14), (2012, 4, 3, 15), (2012, 4, 3, 16), (2012, 4, 3, 17), (2012, 4, 3, 18), (2012, 4, 3, 19), (2012, 4, 3, 20)], 
#				'forecastDayDate': (2012, 3, 28), 
#				'tmpF': [36.0, 36.0, 36.0, 36.0, 35.0, 35.0, 35.0, 35.0, 35.0, 35.0, 36.0, 39.0, 40.0, 41.0, 41.0, 40.0, 40.0, 39.0, 39.0, 38.0, 38.0, 37.0, 37.0, 36.0, 36.0, 36.0, 36.0, 34.0, 35.0, 35.0, 33.0, 32.0, 37.0, 41.0, 42.0, 44.0, 46.0, 45.0, 46.0, 42.0, 40.0, 40.0, 39.0, 39.0, 39.0, 38.0, 37.0, 37.0, 38.0, 40.0, 40.0, 40.0, 42.0, 43.0, 44.0, 45.0, 48.0, 47.0, 47.0, 48.0, 50.0, 50.0, 49.0, 45.0, 42.0, 38.0, 37.0, 37.0, 36.0, 35.0, 34.0, 34.0, 34.0, 32.0, 32.0, 30.0, 29.0, 29.0, 30.0, 33.0, 33.0, 34.0, 31.0, 29.0, 29.0, 28.0, 29.0, 29.0, 27.0, 28.0, 27.0, 24.0, 23.0, 22.0, 21.0, 21.0, 19.0, 18.0, 17.0, 17.0, 16.0, 16.0, 16.0, 17.0, 17.0, 17.0, 17.0, 20.0, 21.0, 22.0, 23.0, 24.0, 23.0, 22.0, 22.0, 21.0, 21.0, 20.0, 19.0, 18.0, 15.0, 18.0, 17.0, 16.0, 15.0, 13.0, 14.0, 21.0, 29.0, 33.0, 32.0, 37.0, 39.0, 41.0, 41.0, 42.0, 40.0, 38.0, 36.0, 36.0, 35.0, 35.0, 36.0, 35.0, 36.0, 36.0, 36.0, 36.0, 36.0, 36.0, 37.0, 41.0, 47.0, 54.0, 58.0, 62.0, 65.0, 65.0, 65.0, 63.0, 58.0, 55.0, 53.0, 53.0, 54.0, 54.0, 54.0, 55.0, 55.0, 55.0, 55.0, 54.0, 55.0, 55.0, 56.0, 56.0, 56.0, 58.0, 59.0, 59.0, 54.0, 53.0, 55.0, 57.0, 58.0, 58.0, 58.0, 40.0, 38.0, 35.0, 33.0, 34.0, 34.0, 33.0, 32.0, 32.0, 30.0, 30.0, 29.0, 32.0, 34.0, 34.0, 35.0, 36.0, 35.0, 35.0, 36.0, 33.0, 31.0, 31.0, 29.0, 28.0, 27.0, 25.0, 25.0, 24.0, 23.0, 22.0, 22.0, 22.0, 21.0, 19.0, 19.0, 19.0, 20.0, 22.0, 25.0, 26.0, 31.0, 31.0, 34.0, 37.0, 37.0, 34.0, 31.0, 32.0, 32.0, 32.0, 32.0, 33.0, 34.0, 34.0, 34.0, 34.0, 33.0, 33.0, 33.0, 34.0, 42.0, 49.0, 52.0, 55.0, 58.0, 60.0, 63.0, 64.0, 65.0, 65.0, 62.0, 51.0, 45.0, 43.0, 47.0, 44.0, 41.0, 40.0, 37.0, 37.0, 35.0, 34.0, 33.0, 35.0, 39.0, 49.0, 62.0, 64.0, 65.0, 67.0, 65.0, 64.0, 62.0, 61.0, 60.0, 59.0, 57.0, 58.0, 57.0, 56.0, 56.0, 57.0, 57.0, 57.0, 55.0, 54.0, 54.0, 55.0, 60.0, 62.0, 62.0, 60.0, 62.0, 65.0, 66.0, 68.0, 67.0, 67.0, 62.0, 57.0, 59.0, 55.0, 54.0, 53.0, 52.0, 48.0, 49.0, 45.0, 40.0, 37.0, 35.0, 35.0, 44.0, 49.0, 51.0, 53.0, 55.0, 57.0, 59.0, 60.0, 61.0, 61.0, 57.0, 48.0, 46.0, 44.0, 41.0, 39.0, 39.0, 37.0, 37.0, 36.0, 36.0, 43.0, 46.0, 45.0, 52.0, 56.0, 61.0, 65.0, 67.0, 71.0, 73.0, 73.0, 73.0, 72.0, 63.0, 60.0, 58.0, 59.0, 59.0, 58.0, 55.0, 53.0, 52.0, 51.0, 51.0, 49.0, 48.0, 47.0, 47.0, 49.0, 54.0, 59.0, 63.0, 61.0, 63.0, 67.0, 65.0, 63.0, 60.0, 56.0, 54.0, 54.0, 53.0, 52.0, 51.0, 49.0, 49.0, 48.0, 48.0, 46.0, 45.0, 47.0, 47.0, 50.0, 60.0, 64.0, 65.0, 68.0, 72.0, 74.0, 75.0, 73.0, 70.0, 62.0, 60.0, 62.0, 61.0, 57.0, 59.0, 58.0, 58.0, 56.0, 56.0, 55.0, 54.0, 55.0, 57.0, 61.0, 66.0, 71.0, 74.0, 77.0, 78.0, 77.0, 77.0, 73.0, 71.0, 65.0, 63.0, 58.0, 59.0, 62.0, 61.0, 61.0, 60.0, 59.0, 59.0, 58.0, 57.0, 58.0, 60.0, 62.0, 67.0, 71.0, 75.0, 77.0, 78.0, 77.0, 74.0, 70.0, 67.0, 65.0, 67.0, 65.0, 62.0, 60.0, 58.0, 57.0, 56.0, 57.0, 56.0, 55.0, 53.0, 54.0, 60.0, 68.0, 69.0, 69.0, 70.0, 71.0, 73.0, 72.0, 74.0, 75.0, 70.0, 64.0, 60.0, 58.0, 56.0, 55.0, 53.0, 52.0, 50.0, 52.0, 49.0, 48.0, 50.0, 52.0, 60.0, 68.0, 71.0, 74.0, 75.0, 76.0, 77.0, 77.0, 78.0, 77.0, 73.0, 66.0, 65.0, 63.0, 62.0, 59.0, 59.0, 58.0, 57.0, 56.0, 55.0, 54.0, 54.0, 56.0, 62.0, 67.0, 71.0, 72.0, 74.0, 74.0, 74.0, 74.0, 74.0, 73.0, 71.0, 65.0, 60.0, 58.0, 56.0, 54.0, 53.0, 52.0, 51.0, 50.0, 49.0, 48.0, 48.0, 50.0, 54.0, 56.0, 58.0, 61.0, 63.0, 66.0, 68.0, 68.0, 69.0, 68.0, 65.0, 62.0, 60.0, 58.0, 54.0, 52.0, 50.0, 50.0, 51.0, 51.0, 51.0, 52.0, 57.0, 57.0, 58.0, 59.0, 62.0, 59.0, 61.0, 61.0, 61.0, 60.0, 59.0, 54.0, 54.0, 54.0, 54.0, 54.0, 51.0, 52.0, 48.0, 46.0, 46.0, 45.0, 45.0, 45.0, 45.0, 46.0, 47.0, 47.0, 48.0, 51.0, 54.0, 55.0, 53.0, 51.0, 49.0, 49.0, 49.0, 49.0, 48.0, 45.0, 43.0, 44.0, 43.0, 47.0, 45.0, 43.0, 41.0, 40.0, 35.0, 33.0, 32.0, 31.0, 30.0, 32.0, 32.0, 34.0, 35.0, 34.0, 34.0, 34.0, 33.0, 32.0, 32.0, 30.0, 29.0, 29.0, 27.0, 27.0, 26.0, 25.0, 24.0, 23.0, 22.0, 25.0, 27.0, 28.0, 30.0, 32.0, 35.0, 39.0, 39.0, 42.0, 44.0, 43.0, 42.0, 37.0, 38.0, 40.0, 41.0, 41.0, 42.0, 42.0, 36.049999999999997, 36.240000000000002, 36.630000000000003, 36.950000000000003, 37.539999999999999, 38.369999999999997, 40.009999999999998, 42.960000000000001, 46.789999999999999, 50.990000000000002, 54.240000000000002, 57.259999999999998, 59.990000000000002, 61.57, 62.359999999999999, 61.969999999999999, 60.43, 57.899999999999999, 54.950000000000003, 52.869999999999997, 50.909999999999997, 49.009999999999998, 47.200000000000003, 45.479999999999997, 43.969999999999999, 42.759999999999998, 41.770000000000003, 40.909999999999997, 40.299999999999997, 39.939999999999998, 40.009999999999998, 40.460000000000001, 41.219999999999999, 41.990000000000002, 42.380000000000003, 42.670000000000002, 43.07, 43.340000000000003, 43.490000000000002, 43.07, 41.799999999999997, 39.969999999999999, 38.030000000000001, 36.670000000000002, 35.420000000000002, 34.07, 32.600000000000001, 31.120000000000001, 29.93, 29.16, 28.629999999999999, 27.949999999999999, 27.68, 27.75, 29.030000000000001, 32.079999999999998, 36.329999999999998, 40.909999999999997, 43.990000000000002, 46.640000000000001, 49.009999999999998, 50.520000000000003, 51.359999999999999, 50.990000000000002, 49.409999999999997, 46.829999999999998, 43.969999999999999, 42.060000000000002, 40.439999999999998, 38.979999999999997, 37.530000000000001, 35.939999999999998, 34.07, 32.829999999999998, 31.469999999999999, 30.300000000000001, 29.629999999999999, 29.760000000000002, 31.010000000000002, 32.969999999999999, 35.950000000000003, 39.549999999999997, 43.340000000000003, 46.93, 49.909999999999997, 50.600000000000001, 50.450000000000003, 49.649999999999999, 48.359999999999999, 46.770000000000003, 45.049999999999997, 43.82, 42.539999999999999, 41.109999999999999, 39.439999999999998, 37.43, 34.969999999999999, 33.759999999999998, 32.390000000000001, 31.239999999999998, 30.699999999999999, 31.16, 32.990000000000002, 35.710000000000001, 39.68, 44.399999999999999, 49.359999999999999, 54.07, 58.009999999999998, 59.079999999999998, 59.090000000000003, 58.270000000000003, 56.829999999999998, 54.990000000000002, 52.969999999999999, 51.729999999999997, 50.439999999999998, 49.009999999999998, 47.369999999999997, 45.409999999999997, 43.07, 41.810000000000002, 40.399999999999999, 39.189999999999998, 38.490000000000002, 38.659999999999997, 40.009999999999998, 42.109999999999999, 45.289999999999999, 49.109999999999999, 53.130000000000003, 56.899999999999999, 59.990000000000002, 60.630000000000003, 60.350000000000001, 59.350000000000001, 57.829999999999998, 55.990000000000002, 54.049999999999997, 52.740000000000002, 51.43, 50.0, 48.340000000000003, 46.369999999999997, 43.969999999999999, 42.670000000000002, 41.200000000000003, 39.93, 39.210000000000001, 39.420000000000002, 40.909999999999997, 42.890000000000001, 45.990000000000002, 49.670000000000002, 53.399999999999999, 56.659999999999997, 58.909999999999997, 59.310000000000002, 58.619999999999997, 57.299999999999997, 55.799999999999997, 54.560000000000002, 54.049999999999997], 
#				'flags': ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''], 
#				'prcpMM': [2.5, 5.5999999999999996, 3.7999999999999998, 0.5, 0.5, 1.0, 0.0, 0.29999999999999999, 1.8, 0.5, 0.29999999999999999, 0.0, 0.0, 0.29999999999999999, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.5, 3.0, 0.29999999999999999, 0.0, 0.29999999999999999, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.29999999999999999, 0.0, 0.29999999999999999, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.80000000000000004, 3.0, 0.29999999999999999, 0.0, 0.0, 0.0, 0.0, 3.6000000000000001, 2.7999999999999998, 1.0, 1.0, 1.0, 0.29999999999999999, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.29999999999999999, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.29999999999999999, 0.0, 0.29999999999999999, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.29999999999999999, 0.5, 0.80000000000000004, 0.29999999999999999, 0.29999999999999999, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.29999999999999999, 0.29999999999999999, 0.29999999999999999, 0.29999999999999999, 0.29999999999999999, 0.29999999999999999, 0.17000000000000001, 0.17000000000000001, 0.17000000000000001, 0.17000000000000001, 0.17000000000000001, 0.17000000000000001, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.13, 0.13, 0.13, 0.13, 0.13, 0.13, 0.040000000000000001, 0.040000000000000001, 0.040000000000000001, 0.040000000000000001, 0.040000000000000001, 0.040000000000000001, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0, -999.0], 
#				'rh': [98.0, 100.0, 99.0, 98.0, 99.0, 100.0, 98.0, 99.0, 100.0, 100.0, 100.0, 97.0, 86.0, 81.0, 76.0, 70.0, 73.0, 76.0, 74.0, 77.0, 78.0, 80.0, 84.0, 84.0, 86.0, 85.0, 86.0, 94.0, 93.0, 92.0, 94.0, 96.0, 85.0, 76.0, 68.0, 64.0, 60.0, 65.0, 64.0, 72.0, 76.0, 78.0, 83.0, 84.0, 86.0, 95.0, 95.0, 95.0, 95.0, 93.0, 93.0, 95.0, 96.0, 95.0, 95.0, 94.0, 83.0, 61.0, 46.0, 42.0, 30.0, 32.0, 37.0, 40.0, 47.0, 64.0, 56.0, 56.0, 56.0, 58.0, 65.0, 62.0, 64.0, 66.0, 64.0, 65.0, 67.0, 70.0, 69.0, 64.0, 63.0, 61.0, 97.0, 100.0, 92.0, 100.0, 90.0, 87.0, 95.0, 75.0, 73.0, 100.0, 100.0, 100.0, 90.0, 86.0, 100.0, 100.0, 99.0, 95.0, 92.0, 94.0, 91.0, 87.0, 95.0, 85.0, 84.0, 76.0, 74.0, 74.0, 69.0, 64.0, 61.0, 62.0, 64.0, 64.0, 67.0, 70.0, 68.0, 77.0, 82.0, 80.0, 86.0, 89.0, 95.0, 100.0, 100.0, 95.0, 58.0, 49.0, 56.0, 49.0, 42.0, 43.0, 41.0, 41.0, 42.0, 43.0, 48.0, 50.0, 50.0, 53.0, 54.0, 58.0, 57.0, 57.0, 58.0, 58.0, 60.0, 61.0, 59.0, 51.0, 43.0, 36.0, 31.0, 29.0, 27.0, 29.0, 30.0, 29.0, 33.0, 38.0, 40.0, 42.0, 41.0, 42.0, 42.0, 45.0, 49.0, 53.0, 56.0, 58.0, 56.0, 56.0, 55.0, 56.0, 56.0, 55.0, 55.0, 57.0, 82.0, 92.0, 88.0, 83.0, 79.0, 79.0, 81.0, 97.0, 96.0, 99.0, 100.0, 100.0, 97.0, 88.0, 85.0, 72.0, 75.0, 75.0, 74.0, 72.0, 65.0, 63.0, 69.0, 80.0, 93.0, 86.0, 54.0, 81.0, 87.0, 75.0, 85.0, 68.0, 59.0, 63.0, 67.0, 68.0, 69.0, 73.0, 67.0, 74.0, 81.0, 82.0, 85.0, 86.0, 85.0, 81.0, 76.0, 69.0, 60.0, 58.0, 54.0, 47.0, 41.0, 46.0, 55.0, 52.0, 51.0, 50.0, 48.0, 48.0, 45.0, 44.0, 45.0, 47.0, 51.0, 52.0, 52.0, 53.0, 42.0, 33.0, 32.0, 33.0, 29.0, 29.0, 26.0, 25.0, 24.0, 23.0, 24.0, 40.0, 53.0, 56.0, 48.0, 53.0, 61.0, 63.0, 75.0, 72.0, 77.0, 79.0, 83.0, 79.0, 71.0, 60.0, 38.0, 34.0, 30.0, 29.0, 30.0, 32.0, 33.0, 33.0, 40.0, 45.0, 48.0, 48.0, 49.0, 53.0, 54.0, 55.0, 63.0, 74.0, 81.0, 86.0, 89.0, 88.0, 79.0, 75.0, 77.0, 89.0, 74.0, 57.0, 52.0, 50.0, 50.0, 44.0, 55.0, 68.0, 58.0, 64.0, 68.0, 68.0, 68.0, 69.0, 62.0, 78.0, 87.0, 95.0, 98.0, 99.0, 89.0, 65.0, 50.0, 46.0, 42.0, 32.0, 30.0, 28.0, 26.0, 26.0, 31.0, 53.0, 55.0, 60.0, 67.0, 70.0, 73.0, 79.0, 76.0, 82.0, 84.0, 54.0, 48.0, 50.0, 44.0, 39.0, 37.0, 37.0, 38.0, 36.0, 41.0, 43.0, 44.0, 45.0, 54.0, 69.0, 72.0, 59.0, 58.0, 61.0, 66.0, 70.0, 73.0, 76.0, 78.0, 86.0, 92.0, 94.0, 96.0, 95.0, 91.0, 80.0, 72.0, 77.0, 75.0, 68.0, 74.0, 77.0, 80.0, 91.0, 96.0, 97.0, 98.0, 98.0, 98.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 75.0, 57.0, 51.0, 43.0, 39.0, 32.0, 33.0, 34.0, 36.0, 50.0, 54.0, 47.0, 49.0, 58.0, 59.0, 64.0, 70.0, 76.0, 80.0, 84.0, 90.0, 89.0, 83.0, 77.0, 67.0, 60.0, 51.0, 48.0, 44.0, 43.0, 40.0, 43.0, 46.0, 67.0, 74.0, 84.0, 86.0, 73.0, 75.0, 77.0, 79.0, 80.0, 81.0, 83.0, 83.0, 82.0, 80.0, 77.0, 67.0, 59.0, 53.0, 47.0, 43.0, 46.0, 49.0, 58.0, 66.0, 72.0, 67.0, 72.0, 80.0, 85.0, 89.0, 94.0, 96.0, 93.0, 96.0, 96.0, 96.0, 99.0, 89.0, 71.0, 69.0, 68.0, 65.0, 62.0, 53.0, 56.0, 51.0, 47.0, 56.0, 68.0, 77.0, 84.0, 88.0, 88.0, 92.0, 93.0, 93.0, 91.0, 94.0, 99.0, 99.0, 97.0, 87.0, 68.0, 62.0, 55.0, 52.0, 47.0, 43.0, 43.0, 41.0, 40.0, 48.0, 60.0, 64.0, 70.0, 75.0, 82.0, 85.0, 86.0, 88.0, 90.0, 93.0, 94.0, 95.0, 93.0, 77.0, 68.0, 59.0, 60.0, 51.0, 53.0, 51.0, 51.0, 55.0, 53.0, 53.0, 64.0, 78.0, 83.0, 91.0, 93.0, 93.0, 97.0, 97.0, 100.0, 99.0, 100.0, 100.0, 100.0, 100.0, 99.0, 89.0, 85.0, 80.0, 67.0, 58.0, 60.0, 51.0, 42.0, 42.0, 45.0, 55.0, 61.0, 68.0, 73.0, 80.0, 80.0, 77.0, 77.0, 78.0, 72.0, 54.0, 52.0, 50.0, 46.0, 42.0, 44.0, 40.0, 38.0, 41.0, 46.0, 54.0, 73.0, 71.0, 68.0, 68.0, 60.0, 62.0, 60.0, 72.0, 79.0, 80.0, 80.0, 81.0, 81.0, 80.0, 78.0, 74.0, 82.0, 83.0, 79.0, 75.0, 80.0, 83.0, 94.0, 95.0, 95.0, 97.0, 96.0, 95.0, 98.0, 100.0, 100.0, 100.0, 82.0, 77.0, 76.0, 80.0, 88.0, 86.0, 75.0, 62.0, 59.0, 68.0, 58.0, 61.0, 52.0, 53.0, 47.0, 39.0, 41.0, 44.0, 38.0, 41.0, 45.0, 45.0, 42.0, 43.0, 42.0, 42.0, 47.0, 52.0, 57.0, 62.0, 55.0, 55.0, 51.0, 50.0, 46.0, 40.0, 36.0, 29.0, 26.0, 30.0, 28.0, 27.0, 42.0, 33.0, 28.0, 27.0, 29.0, 29.0, 32.0, 64.0, 65.0, 68.0, 74.0, 79.0, 84.0, 87.0, 84.0, 78.0, 71.0, 70.0, 70.0, 70.0, 70.0, 69.0, 68.0, 70.0, 73.0, 76.0, 79.0, 83.0, 86.0, 88.0, 89.0, 90.0, 92.0, 93.0, 94.0, 94.0, 92.0, 90.0, 87.0, 83.0, 79.0, 76.0, 75.0, 72.0, 70.0, 68.0, 67.0, 69.0, 72.0, 76.0, 78.0, 81.0, 84.0, 87.0, 90.0, 92.0, 92.0, 91.0, 89.0, 88.0, 87.0, 83.0, 76.0, 68.0, 59.0, 54.0, 50.0, 47.0, 45.0, 45.0, 46.0, 49.0, 53.0, 58.0, 61.0, 63.0, 65.0, 67.0, 70.0, 73.0, 76.0, 80.0, 84.0, 86.0, 88.0, 87.0, 84.0, 78.0, 72.0, 65.0, 58.0, 52.0, 51.0, 52.0, 53.0, 56.0, 58.0, 61.0, 63.0, 64.0, 66.0, 67.0, 70.0, 73.0, 76.0, 79.0, 81.0, 84.0, 84.0, 83.0, 80.0, 76.0, 70.0, 64.0, 58.0, 53.0, 53.0, 54.0, 56.0, 59.0, 63.0, 67.0, 70.0, 73.0, 76.0, 80.0, 84.0, 90.0, 94.0, 98.0, 100.0, 100.0, 100.0, 100.0, 100.0, 93.0, 85.0, 76.0, 67.0, 60.0, 58.0, 59.0, 61.0, 64.0, 69.0, 73.0, 76.0, 79.0, 83.0, 86.0, 90.0, 94.0, 96.0, 97.0, 98.0, 98.0, 97.0, 93.0, 89.0, 84.0, 78.0, 71.0, 66.0, 62.0, 61.0, 61.0, 63.0, 65.0, 67.0, 67.0]}
