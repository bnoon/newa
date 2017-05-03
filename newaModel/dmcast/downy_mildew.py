# ----------------------------------------
# dmc.py
# ----------------------------------------
# imports
# ----------------------------------------
import ctypes as C
import sys,os
import array
import copy
import get_weather
import units
import dm_cultivars
from print_exception import print_exception
from mx import DateTime


# --------------------------------------------------
# Note:
#   The model requires the following units for climate data:
#     temperature  degC 
#     precipitation millimeter 
#
#  We therefore need to convert units for the output
#
# --------------------------------------------------
#  NOTE: ????? for disease warnings, if there is no leaf wetness,  this
#                  is set to 0.  I've set aveTmp to '-999.0', for missing.
#                  It is '-'  on the dm output page.
#
# smry_dict return information:
#
# 'warnings' keyword: dictionary 
#	dictionary key words are "mm/dd".  
#	For each "mm/dd" there is a dictionary with the
#       following keys:
#         'hours':  list of 24 hours which can be:
#              	 '', 'W', 'P', or 'WP'
#                'W':  warning
#                'P':  rainfall
#                'WP': rainfall and warning
#                'lwet': floating point value (%5.1f), e.g  12.8
#                'aveTmp': floating point(%5.1f), temp(F.), e.g. 58.8
#                'prcp':   floating point(%5.2f), prcp (in.) e.g. 0.14
#	    example dictionary:
#      		keyword "08/11': {'hours': ['P','W','W','WP','WP','W','W','W','W',
#                              '','','','','','','','','','','','','','',''],
#                              'lwet': '12.8','aveTmp': '58.8','prcp': '0.14'}
#
#  'history'  keyword:   dictionary
#       dictionary key words:  simply regular numbers, 1,2,3, etc.  
#                               1  is first wet period, 2 is second
#                               wet period, etc.
#       For each number, there is a dictionary with the following keys:
#             'start', e.g. 01/18 05:00
#             'end', e.g.   01/18 09:00
#             'duration', e.g. 5
#             'lwet', e.g.     8.3
#             'ave_c', e.g.   15.6
#             'ave_f', e.g.   60.0
#          example history dictionary:
#                                   
#             keyword  1: {'start': '01/18 05:00', 'end': '01/18 09:00',
#			'duration': '5','lwet': '8.3','ave_c': '15.6',
#                       'ave_f': '60.0' }
#
#  datetime constants:  'els12', 'primary', 'incubation'
#
# --------------------------------------------------
global degC_to_degF, mm_to_inch
degC_to_degF = units.new('degC','degF')
mm_to_inch = units.new('millimeter','inch')
global systemInfo
systemInfo = os.uname()
if systemInfo[0] == 'Darwin' :
	#_dmC  = C.cdll.LoadLibrary("/newa/newaModel/newaModel/dmcast/libdmcast.dylib")
	_dmC  = C.cdll.LoadLibrary("newaModel/dmcast/libdmcast.dylib")
else :
	_dmC  = C.cdll.LoadLibrary("newaModel/dmcast/libdmcast.so")




class general_dm(object):

	def __init__(self,dict) :
		self.smry_dict = dict
		self.all_days = {}
		self.warnings = {}
		self.warnings_history = {}
		self.entryNum = 0
		self.pending_hours = []
		self.pending_day = None
		self.wet_threshold = 0.1666
		self.missing = -999.0


	def run_dm(self) :
		try :
			self.eTime = self.smry_dict['accend']
			self.eDate = (self.eTime.year,self.eTime.month,self.eTime.day)
			self.cultivar = self.smry_dict['cultivar']
			self.stn = self.smry_dict['stn']
			self.process_weather()
			self.process_cultivar()
			self.process_disease()
			self.get_results()
			self.smry_dict['els12'] = self.get_els12()
			self.smry_dict['primary'] = self.get_primary_inf()
			self.smry_dict['incubation'] = self.incubationTime
			self.smry_dict['warnings'] = self.get_warnings()
			self.smry_dict['history'] = self.get_history()
			return self.smry_dict
		except get_weather.weatherError :
			return self.smry_dict
		
	
	def dm_date(self,eTime) :
		self.eTime = eTime 
		self.eDate = (self.eTime.year,self.eTime.month,self.eTime.day)


	def get_warning_day(self) :
		self.warning_sTime = self.eTime + DateTime.RelativeDate(days=-14)
		self.warning_sDay = self.warning_sTime.day_of_year
		self.warning_eDay = self.eTime.day_of_year


	def update_all_days(self) :
		eTime = apply(DateTime.Date,self.eDate)
		#
		# PLEASE NOTE:  
		# For the current program to work, we must start on Jan. 1
		# This has impact on figuring out indexes among other things.
		#               
		sTime = DateTime.DateTime(self.eDate[0],1,1)
		while sTime <= eTime : 
			this_date = "%02d/%02d"%(sTime.month,sTime.day)
			self.all_days[sTime.day_of_year] = this_date
			sTime = sTime + DateTime.RelativeDate(days=+1)

		

	def dm_stn(self,stn) :
		self.stn = stn

	def dm_cultivar(self,cultivar) :
		self.cultivar = cultivar

				

	def process_weather(self,test=None):
		# -----------------------------------
		# weather array setup
		# -----------------------------------
		yearOfHours = 366*24
		intPtr = C.POINTER(C.c_int*yearOfHours)
		doublePtr = C.POINTER(C.c_double*yearOfHours)
		YearIntArray = C.c_int*yearOfHours
		YearDoubleArray = C.c_double*yearOfHours
		sister = self.smry_dict['sister']


		all_weather = get_weather.get_mildew_weather(self.stn,self.eDate,sister)
		if len(all_weather) == 1 :
			self.smry_dict['statMsg'] = 'Insufficient data for model'
			raise get_weather.weatherError
		(statFlg,self.dates,hours,days,tmp,rh,prcp,lwet,ok) = all_weather
		if test :
			oFile = open('test_weather.txt','w')
			for index in range(len(self.dates)) :
				this_date = self.dates[index]
				(yy,mm,dd,hh) = this_date
				this_hour = hours[index]
				this_day = days[index]
				this_tmp = tmp[index]
				this_rh = rh[index]
				this_prcp = prcp[index]
				this_lwet = lwet[index]
				this_ok = ok[index]
				oFile.write("%d,%d,%d,%d,%d,%d,%5.2f,%5.2f,%5.2f,%5.1f,%d\n"%(yy,mm,dd,hh,this_hour,this_day,this_tmp,this_rh,this_prcp,this_lwet,this_ok))
				oFile.flush()
			oFile.close()
				

		if not self.eTime.is_leapyear :
			lastIndex = len(ok)  - 25
		else :
			lastIndex = len(ok) - 1

		hours = array.array('I',hours)
		self.c_hours = YearIntArray(*hours)
		hourPtr = C.pointer(self.c_hours)

		self.dayList = copy.copy(days)
		days = array.array('I',days)
		self.c_days = YearIntArray(*days)
		dayPtr = C.pointer(self.c_days)
		
		tmp = array.array('d',tmp)
		self.c_tmp = YearDoubleArray(*tmp)
		tmpPtr = C.pointer(self.c_tmp)
		
		rh = array.array('d',rh)
		self.c_rh = YearDoubleArray(*rh)
		rhPtr = C.pointer(self.c_rh)

		prcp = array.array('d',prcp)
		self.c_prcp = YearDoubleArray(*prcp)
		prcpPtr = C.pointer(self.c_prcp)

		lwet = array.array('d',lwet)
		self.c_lwet = YearDoubleArray(*lwet)
		lwetPtr = C.pointer(self.c_lwet)

		ok = array.array('d',ok)
		self.c_ok = YearDoubleArray(* ok)
		okPtr = C.pointer(self.c_ok)

		retCode = _dmC.setup_dm()

		cWeather = _dmC.read_weatherdata
		cWeather.argtypes = [C.c_int,intPtr,intPtr,doublePtr,doublePtr,doublePtr,doublePtr,doublePtr]
		retCode = cWeather(lastIndex,dayPtr,hourPtr,tmpPtr,rhPtr,prcpPtr,lwetPtr,okPtr)
		retCode =  _dmC.process_weatherdata()
		
		
		

	def process_cultivar(self):
		info = dm_cultivars.cultivars[self.cultivar]
		A = info['A']
		B = info['B']
		k = info['k']
		m = info['m']

		cult = _dmC.grape_phenology
		cult.argtypes = [C.c_double,C.c_double,C.c_double,C.c_double]
		retCode = cult(A,B,k,m)
		retCode = _dmC.primary_infection()
		retCode = _dmC.incubation_period()



	def process_disease(self) :
		# -----------------------------------
		# disease setup
		# -----------------------------------
		intPtr = C.POINTER(C.c_int*367)
		YearIntArray = C.c_int*367
		#
		# parm fields: 
		#  - number of warnings
		#  - els12
		#  - primary_inf
		#  - incubation
		#
		parmArray = C.c_int*4
		constantPtr = C.POINTER(C.c_int*4)
		
		empty_vals = [0,]*367
		vals = array.array('I',empty_vals)
		
		self.sdays = YearIntArray(*vals)
		sdaysPtr = C.pointer(self.sdays)

		self.shours = YearIntArray(*vals)
		shoursPtr = C.pointer(self.shours)

		self.edays = YearIntArray(*vals)
		edaysPtr = C.pointer(self.edays)

		self.ehours = YearIntArray(*vals)
		ehoursPtr = C.pointer(self.ehours)

		self.duration = YearIntArray(*vals)
		durationPtr = C.pointer(self.duration)

		parm_vals = [0, ]*4
		vals = array.array('I',parm_vals)
		c_parms = parmArray(*vals)
		parmPtr = C.pointer(c_parms)


		disease = _dmC.run_disease_model
		disease.argtypes = [intPtr,intPtr,intPtr,intPtr,intPtr,constantPtr]


		retCode = disease(sdaysPtr,shoursPtr,edaysPtr,ehoursPtr,durationPtr,parmPtr)
		self.dm_warnings = c_parms[0]
		self.els12 = c_parms[1]
		self.primary_inf = c_parms[2]
		self.incubation = c_parms[3]
		

	
	def get_els12(self) :
		els12Time = self.getTimeFromDay(self.els12)
		return els12Time 

	def get_primary_inf(self) :
		primaryTime = self.getTimeFromDay(self.primary_inf)
		return primaryTime 

	def get_incubation(self) :
		incubationTime = self.getTimeFromDay(self.incubation)
		return incubationTime

	def getTimeFromDay(self,day) :
		try:
			day_string = self.all_days[day]
			mm = int(day_string[0:2])
			dd = int(day_string[3:5])
			this_time = apply(DateTime.Date,(self.eTime.year,mm,dd))
		except:
			this_time = None
		return this_time

	def get_warnings(self) :
		return self.warnings

	def get_history(self) :
		return self.warnings_history

	def getDayIndex(self,sDay) :
		start_index = self.dayList.index(sDay)

		val = 0
		while( (self.c_days[start_index + val] == sDay) and 
		((start_index + val)<len(self.c_days)) ):
			val = val + 1
			if val > 30 :        #changed from 27 to 30 -kle
				print 'big error'
				sys.exit()
		stop_index = start_index + val


		return (start_index,stop_index)


	def get_24hour_weather(self,startIndex,stopIndex,all_hours) :
		lwet_24hr = 0
		sumWetTmpC = 0
		numWetTmp = 0.0
		prcp_24hr_mm = 0 

		for index in range(startIndex,stopIndex) :
			if self.c_ok[index] == 0 :
				continue
			else :
				if self.c_lwet[index] > self.wet_threshold :
					numWetTmp = numWetTmp + 1.0
					tmpC = self.c_tmp[index]
					sumWetTmpC = sumWetTmpC + tmpC
					
				lwet_24hr = lwet_24hr + self.c_lwet[index]
				prcp = self.c_prcp[index]
				if prcp > 0 :
					hour = self.c_hours[index]
					all_hours[hour] = all_hours[hour] + 'P'	
				prcp_24hr_mm = prcp_24hr_mm + prcp 


		if numWetTmp == 0 :
			lwet = 0.0
			aveWetTmpF = self.missing
			prcp_24hr_in = mm_to_inch.convert(prcp_24hr_mm)
		else :
			aveWetTmpC = sumWetTmpC/numWetTmp
			aveWetTmpF = degC_to_degF.convert(aveWetTmpC)
			prcp_24hr_in = mm_to_inch.convert(prcp_24hr_mm)
			lwet = lwet_24hr/60.0
		return (lwet,aveWetTmpF,prcp_24hr_in,all_hours)
		




		
	def process_risk(self,day,indexList,startIndex,stopIndex) :
		warning_key = self.all_days[day]
			
		
		all_hours = ['',]*24

		if len(self.pending_hours) > 0 :
			this_hour = self.pending_hours[0]
			end_hour = self.pending_hours[-1]
			while this_hour <= end_hour :
				all_hours[this_hour] = 'W'
				this_hour = this_hour + 1
			self.pending_hours = []
			self.pending_day = None

		for wIndex in indexList :
			shour = self.shours[wIndex]
			ehour = self.ehours[wIndex]
			sday = self.sdays[wIndex]
			eday = self.edays[wIndex]

			this_hour = shour
			
			if sday == eday :
				while this_hour <= ehour :
					all_hours[this_hour] = 'W'
					this_hour = this_hour + 1
			else :
				today_end = 23
				while this_hour <= today_end :
					all_hours[this_hour] = 'W'
					this_hour = this_hour + 1

				self.pending_day = eday
				this_hour = 0
				end_hour = ehour
				while this_hour <= end_hour :
					self.pending_hours.append(this_hour)
					this_hour = this_hour + 1
					
		(lwet_amount,ave_tmp,sum_prcp,all_hours) = self.get_24hour_weather(startIndex,stopIndex,all_hours)
		self.warnings[warning_key] = {'hours':all_hours,
						'lwet': lwet_amount,
						'aveTmp': ave_tmp,
						'prcp':sum_prcp}

	
	def process_disease_warnings(self,day,indexList) :
		if  (  (len(self.pending_hours) > 0 ) and
		( self.pending_day != day )  ):
			(startIndex,stopIndex) = self.getDayIndex(self.pending_day)
			self.process_risk(self.pending_day,[],startIndex,stopIndex)

		(startIndex,stopIndex) = self.getDayIndex(day)
		self.process_risk(day,indexList,startIndex,stopIndex)


	def get_missing_disease_warnings(self) :
		indexList = []
		sDay = self.warning_sDay
		while sDay <= self.warning_eDay :
			warning_key = self.all_days[sDay]
			if warning_key in self.warnings :
				sDay = sDay + 1
				continue
			(startIndex,stopIndex) = self.getDayIndex(sDay)
			self.process_risk(sDay,indexList,startIndex,stopIndex)
			sDay = sDay + 1

		
	

	def get_wp_indexes(self,sday,shour,eday,ehour) :
		# -------------------------------------
		# figure out wp start_index
		# -------------------------------------
		val = 0
		#start_index = (sday-1)*24
		start_index = self.dayList.index(sday)
		this_hour = self.c_hours[start_index]
		while this_hour < shour :
			val = val + 1
			if val == 30 :        #changed from 27 to 30 -kle
				print 'we have a problem',sday,shour,eday,ehour
				sys.exit()
			this_hour = self.c_hours[start_index+val]
			if this_hour == shour :
				start_index = start_index + val
				break
		val = 0
		lwet = self.c_lwet[start_index]
		while lwet > self.wet_threshold :
			val = val + 1
			if val > 30 :        #changed from 27 to 30 -kle
				print 'we have a problem',sday,shour,eday,ehour
				sys.exit()
			lwet = self.c_lwet[start_index -val]
			if lwet <= self.wet_threshold :
				start_index = start_index - val+1
				break

		# -------------------------------------
		# figure out wp end_index
		# -------------------------------------
		val = 0
		#end_index = (eday-1)*24
		end_index = self.dayList.index(eday)
		this_hour = self.c_hours[end_index]
		while this_hour < ehour :
			val = val + 1
			if val == 30 :        #changed from 27 to 30 -kle
				print 'we have a problem',sday,shour,eday,ehour
				sys.exit()
			this_hour = self.c_hours[end_index + val]
			if this_hour == ehour :
				end_index = end_index + val
				break
		val = 0
		lwet = self.c_lwet[end_index]
		while lwet > self.wet_threshold :
			val = val + 1
			if val > 30 :        #changed from 27 to 30 -kle
				print 'we have a problem',sday,shour,eday,ehour
				sys.exit()
			lwet = self.c_lwet[end_index + val]
			if lwet <= self.wet_threshold :
				end_index = end_index + val
				break
		return (start_index,end_index)
			
		

	def get_wp_weather(self,sday,shour,eday,ehour) :
		startIndex,stopIndex = self.get_wp_indexes(sday,shour,eday,ehour)
		
		wp_lwet = 0
		sumWetTmpC = 0
		numWetTmp = 0.0
		for index in range(startIndex,stopIndex) :
			if self.c_ok[index] == 0 :
				continue
			else :
				numWetTmp = numWetTmp + 1.0
				tmpC = self.c_tmp[index]
				sumWetTmpC = sumWetTmpC + tmpC
					
				wp_lwet = wp_lwet + self.c_lwet[index]


		if numWetTmp == 0 :
			print 'we have a problem,0 wet temp',self.dates[startIndex],self.dates[stopIndex]
			sys.exit()
			
		sumWetTmpF = degC_to_degF.convert(sumWetTmpC)
		aveWetTmpC = sumWetTmpC/numWetTmp
		aveWetTmpF = degC_to_degF.convert(aveWetTmpC)
		lwet = wp_lwet/60.0
		return (lwet,aveWetTmpC,aveWetTmpF)
		

		
	def process_all_warnings(self) :
		all_search_keys = self.search_dictionary.keys()
		all_search_keys.sort()


		for day in all_search_keys :
			if not self.postIncubation :
				warningTime = self.getTimeFromDay(day)
				if warningTime >= self.incubationTime :
					self.postIncubation = 1
			
			indexList = self.search_dictionary[day]
			if day >= self.warning_sDay :
				self.process_disease_warnings(day,indexList)


			for wIndex in indexList :
				sDay = self.sdays[wIndex]
				sHour = self.shours[wIndex]
				eDay = self.edays[wIndex]
				eHour = self.ehours[wIndex]
				duration = self.duration[wIndex]
				sday_string = self.all_days[sDay]
				eday_string = self.all_days[eDay]
				start_string = "%s %02d:00"%(sday_string,sHour)
				end_string = "%s %02d:00"%(eday_string,eHour)
				self.entryNum = self.entryNum + 1
				(lwet,ave_c,ave_f) = self.get_wp_weather(sDay,sHour,eDay,eHour)
				self.warnings_history[self.entryNum] = {'start': start_string,
									'end': end_string,
									'duration': duration,
									'lwet': lwet,
									'ave_c': ave_c,
									'ave_f': ave_f}
				if not self.postIncubation :
					self.warnings_history[self.entryNum]['incomplete'] = 1
		self.get_missing_disease_warnings()

			

	def create_search_dictionary(self) :
		self.search_dictionary = {}
		for index in range(self.dm_warnings) :
			day = self.sdays[index]
			if day not in self.search_dictionary :
				self.search_dictionary[day] = [index,]
			else :
				day_list = self.search_dictionary[day]
				day_list.append(index)
				self.search_dictionary[day] = day_list
			
		

	def get_results(self) :
		self.get_warning_day()
		self.update_all_days()
		self.incubationTime = self.get_incubation()
		self.postIncubation = None
		self.create_search_dictionary()
		self.process_all_warnings()



	# ------------------------------------------------------------
	#  Methods used when testing this program
	# ------------------------------------------------------------
	def test_get_weather(self) :
		iFile = open('fre_2008_weather.txt','r')
		all_lines = iFile.readlines()
		self.dates = ['',]*len(all_lines)
		self.c_tmp = ['',]*len(all_lines)
		self.c_rh = ['',]*len(all_lines)
		self.c_prcp = ['',]*len(all_lines)
		self.c_lwet = ['',]*len(all_lines)
		self.c_ok = ['',]*len(all_lines)
		self.c_days = ['',]*len(all_lines)
		self.c_hours = ['',]*len(all_lines)
		for index in range(len(all_lines)) :
			line = all_lines[index]
			line = line.strip()
			line = line.split(',')
			[yy,mm,dd,hh,hour,day,tmp,rh,prcp,lwet,ok] = line
			date = [int(yy),int(mm),int(dd),int(hh)]
			self.dates[index] = date
			self.c_hours[index] = int(hour)
			self.c_days[index] = int(day)
			self.c_tmp[index] = float(tmp)
			self.c_prcp[index] = float(prcp)
			self.c_lwet[index] = float(lwet)
			self.c_ok[index] = int(ok)

				

	def test_write_warning_data(self) :
		tFile = open('test_file.txt','w')
		for index in range(self.dm_warnings) :
			tFile.write("%d,%d,%d,%d,%d\n"%(self.sdays[index],self.shours[index],self.edays[index],self.ehours[index],self.duration[index]))
			tFile.flush()
		tFile.close()

	def test_write_history(self,all_history):
		oFile = open('test_history.html','w')
		string = """
		<html>
		<table>
		<tr>
		<th>Num</th><th>Start</th><th>End</th><th>Hours</th>
		<th>Leaf Wet</th><th>Temp C</th><th>Temp F</th>
		</tr>
		"""
		oFile.write("%s"%(string))
		for word in all_history:
			dictionary = self.warnings_history[word]
			oFile.write('\n<tr>')
			string = '<td>%s</td>'%(word)
			oFile.write("%s"%(string))
			string = '<td>%s</td>'%(dictionary['start'])
			oFile.write("%s"%(string))
			string = '<td>%s</td>'%(dictionary['end'])
			oFile.write("%s"%(string))
			string = '<td>%s</td>'%(dictionary['duration'])
			oFile.write("%s"%(string))
			string = '<td>%5.1f</td>'%(dictionary['lwet'])
			oFile.write("%s"%(string))
			string = '<td>%5.1f</td>'%(dictionary['ave_c'])
			oFile.write("%s"%(string))
			string = '<td>%5.1f</td>'%(dictionary['ave_f'])
			oFile.write("%s"%(string))
			oFile.write('</tr>')
		oFile.write('</table></html>')
		oFile.close()

	def test_write_warnings(self,all_warnings) :
		oFile = open('test_warnings.html','w')
		string = """
		<html>
		<table>
		<tr>
		<th>Date</th>
		<th>0</th><th>1</th><th>2</th><th>3</th><th>4</th>
		<th>5</th><th>6</th><th>7</th><th>8</th><th>9</th>
		<th>10</th><th>11</th><th>12</th><th>13</th><th>14</th>
		<th>15</th><th>16</th><th>17</th><th>18</th><th>19</th>
		<th>20</th><th>21</th><th>22</th><th>23</th>
		<th>Leaf Wet</th>
		<th>Tmp</th>
		<th>Prcp</th>
		</tr>
		"""
		oFile.write("%s"%(string))

		for word in all_warnings :
			dictionary = self.warnings[word]
			oFile.write("\n<tr>")
			string = "<td>%s</td>"%(word)
			oFile.write("%s"%(string))
			hours = dictionary['hours']
			for item in hours :
				string = "<td>%s</td>"%(item)
				oFile.write("%s"%(string))
			string = "<td>%5.1f</td>"%(dictionary['lwet'])
			oFile.write("%s"%(string))
			string = "<td>%5.1f</td>"%(dictionary['aveTmp'])
			oFile.write("%s"%(string))
			string = "<td>%5.2f</td>"%(dictionary['prcp'])
			oFile.write("%s"%(string))
			oFile.write("</tr>")

			

	
		
	def test_show_results(self):
		all_warnings = self.warnings.keys()
		all_warnings.sort()
		all_history = self.warnings_history.keys()
		all_history.sort()
		self.test_write_history(all_history)
		self.test_write_warnings(all_warnings)

			
	def test_read_warning_data(self) :
		iFile = open('test_file.txt','r')
		all_lines = iFile.readlines()
		self.sdays = ['',]*len(all_lines)
		self.shours = ['',]*len(all_lines)
		self.edays = ['',]*len(all_lines)
		self.ehours = ['',]*len(all_lines)
		self.duration = ['',]*len(all_lines)
		for index in range(len(all_lines)) :
			line = all_lines[index]
			line = line.strip()
			line = line.split(',')
			(sday,shour,eday,ehour,duration) = line
			self.sdays[index] = int(sday)
			self.shours[index] = int(shour)
			self.edays[index] = int(eday)
			self.ehours[index] = int(ehour)
			self.duration[index] = int(duration)

			

if __name__ == '__main__' :
	dict=None
	obj = general_dm(dict)
	stn = 'ith'
	eDate = (2009,9,21)
	eTime = apply(DateTime.Date,eDate)
	obj.dm_date(eTime)
	obj.dm_stn(stn)
	cultivar='Concord'
	obj.dm_cultivar(cultivar)

	print 'going to process weather'
	obj.process_weather()
	obj.process_cultivar()

	print 'going to process disease'
	obj.process_disease()

	print 'going to get results'
	obj.get_results()
	inf = obj.get_primary_inf()
	print inf.month,inf.day,inf.year
	inc = obj.get_incubation()
	print inc.month,inc.day,inc.year
	els12 = obj.get_els12()
	print els12.month,els12.day,els12.year

	#print 'going to do show results - test phase'
	#obj.test_show_results()
	# ---------------------------------
	#
	# run in test mode
	#
	# ---------------------------------
	try :
		pass
		#obj.process_weather(test=1)
		#obj.test_write_warning_data()
		#obj.test_get_weather()
		#obj.test_read_warning_data()
		#obj.get_results()
		#obj.test_show_results()
	except :
		print_exception()
