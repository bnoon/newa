# ------------------
# get_weather 
# ------------------
# imports
# ------------------
from print_exception import print_exception
from ucanCallMethods import hourly_ucan,general_ucan
import Data
import sys
from mx import DateTime
import subprocess
import newaModel.newaModel_io
from bsddb import hashopen
from cPickle import loads




# --------------------------
# Methods
# --------------------------
def show_all(vars) :
	print 'model_weather_routines'
	allKeys = vars.keys()
	allKeys.sort()
	for key in allKeys :
		print key,'\t',vars[key]
	print ''




def getLocalFromEST(date) :
	EST_time = apply(DateTime.Date,date)
	localTime = EST_time + DateTime.RelativeDate(hours=+EST_time.dst)
	day = localTime.day_of_year
	hour = localTime.hour
	return (day,hour)

def getLocalFromEST_time(EST_time) :
	localTime = EST_time + DateTime.RelativeDate(hours=+EST_time.dst)
	return localTime

class weatherError(Exception) :
	"""
	Exception raised because weather is missing.
	"""

# -------------------------
# Classes
# -------------------------
class general_weather(object) :

	def __init__(self,stn_id) :
		self.stn_id = stn_id
		self.tmp_unit = 'degC'
		self.prcp_unit = "millimeter"
		self.missing = -999.
		self.dmc_missing = -999.
		self.rh = None
		self.tmp = None
		self.prcp = None
		self.lwet = None

	
	def get_dates(self,obsTime,eTime) :
		sTime = DateTime.DateTime(obsTime.year,obsTime.month,obsTime.day,obsTime.hour)
		dateList = []
		while sTime < eTime :
			this_date = [sTime.year,sTime.month,sTime.day,sTime.hour]
			dateList.append(this_date)
			sTime = sTime + DateTime.RelativeDate(hours=+1)
		return dateList
			

	def get_observed(self,var,start,end) :
		try :
			var.setDateRange(start,end)
			values  = var.getDataSeqAsFloat()
			flgs = var.getValidFlagSeq()
			dates = var.getDateArraySeq()
			sum = 0
			for this_flg in flgs :
				if this_flg == 1 :
					sum = sum + 1
		except (Data.TSVar.UnavailableDateRange,Data.TSVarFactory.UnavailableDateRange) :
			beginTime = apply(DateTime.Date,start)
			stopTime = apply(DateTime.Date,end)
			diff = stopTime-beginTime
			numMissing = int(diff.hours)
			values = [self.dmc_missing,]*numMissing
			flgs = [False,]*numMissing
			dates = []
			sum = 0
				
		except :
			beginTime = apply(DateTime.Date,start)
			stopTime = apply(DateTime.Date,end)
			diff = stopTime-beginTime
			numMissing = int(diff.hours)
			values = [self.dmc_missing,]*numMissing
			flgs = [False,]*numMissing
			dates = []
			sum = 0
			# error seems to be handled, no need to report in log -kle 6/30/11
#			print 'bare except',self.stn_id,start,end
#			print_exception()
		return (sum,values,flgs,dates)


	def release_tmp(self) :
		if self.tmp:
			self.tmp.release()
			
	def release_rh(self) :
		if self.rh :
			self.rh.release()
			
	def release_prcp(self) :
		if self.prcp :
			self.prcp.release()

	def release_lwet(self) :
		if self.lwet :
			self.lwet.release()

	def return_observed_data(self) :
		return (self.obs_dates,self.obs_tmp,self.obs_rh,self.obs_prcp,self.obs_lwet)
				
	def init_tmp(self) :
		self.tmp.setUnits(self.tmp_unit)
		self.tmp.setMissingDataAsFloat(self.dmc_missing)

	def init_rh(self) :
		self.rh.setMissingDataAsFloat(self.dmc_missing)

	def init_prcp(self) :
		self.prcp.setUnits(self.prcp_unit)
		self.prcp.setMissingDataAsFloat(self.dmc_missing)

	def init_lwet(self) :
		self.lwet.setMissingDataAsFloat(self.dmc_missing)


class icao_weather(general_weather) :
	def __init__(self,stn) :
		stn = stn.upper()
		general_weather.__init__(self,stn)

	def initialize_ucan(self) :
		ucan = general_ucan(user_name="potato_blight_page")
		self.data = ucan.get_data()

		
	def initialize_tmp(self) :
		self.tmp = self.data.newTSVarNative(23,0,self.stn_id)
		self.init_tmp()
		
	def initialize_rh(self) :
		self.rh = self.data.newTSVarNative(24,0,self.stn_id)
		self.init_rh()
		
	def initialize_prcp(self) :
		self.prcp = self.data.newTSVarNative(5,0,self.stn_id)
		self.init_prcp()


	
class newa_weather(general_weather) :

	def initialize_ucan(self) :
		ucan = general_ucan(user_name="downy_mildew")
		self.data = ucan.get_data()
		if self.type == 'miwx':
			self.stn_id = self.stn_id[3:]		
		elif self.type == 'nysm':
			self.stn_id = self.stn_id[5:]		
		q = ucan.get_query()
		r = q.getUcanFromIdAsSeq(self.stn_id,self.type)
		q.release()
		if len(r) > 2 or len(r) == 0:
			print 'init ucan failure',self.stn_id,self.type,r
			sys.exit()
				
		self.ucanId = r[0].ucan_id

		
	def initialize_tmp(self) :
		try:
			self.tmp = self.data.newTSVar(self.tmp_major,self.tmp_minor,self.ucanId)
			self.init_tmp()
		except Data.TSVarFactory.UnknownUcanId:
#			print 'Unknown ucan id',var
			pass
		except:
#			print "Error initializing:",var
			pass


	def initialize_rh(self) :
		try:
			self.rh = self.data.newTSVar(self.rh_major,self.rh_minor,self.ucanId)
			self.init_rh()
		except Data.TSVarFactory.UnknownUcanId:
#			print 'Unknown ucan id',var
			pass
		except:
#			print "Error initializing:",var
			pass
		
	def initialize_prcp(self) :
		try:
			self.prcp = self.data.newTSVar(self.prcp_major,self.prcp_minor,self.ucanId)
			self.init_prcp()
		except Data.TSVarFactory.UnknownUcanId:
#			print 'Unknown ucan id',var
			pass
		except:
#			print "Error initializing:",var
			pass

	def initialize_lwet(self) :
		try:
			self.lwet = self.data.newTSVar(self.lwet_major,self.lwet_minor,self.ucanId)
			self.init_lwet()
		except Data.TSVarFactory.UnknownUcanId:
#			print 'Unknown ucan id',var
			pass
		except:
#			print "Error initializing:",var
			pass
			


class newa_vars(newa_weather) :
	def __init__(self,stn_id) :
		self.type = 'newa'
		self.tmp_major = 23
		self.tmp_minor = 0
		self.rh_major = 24
		self.rh_minor = 0
		self.prcp_major = 5
		self.prcp_minor = 0
		self.lwet_major = 118
		self.lwet_minor = 0
		newa_weather.__init__(self,stn_id)

class njwx_vars(newa_weather) :
	def __init__(self,stn_id) :
		self.type = 'njwx'
		self.tmp_major = 23
		self.tmp_minor = 0
		self.rh_major = 24
		self.rh_minor = 0
		self.prcp_major = 5
		self.prcp_minor = 0
		self.lwet_major = 118
		self.lwet_minor = 0
		newa_weather.__init__(self,stn_id)
	
class culog_vars(newa_weather) :
	def __init__(self,stn) :
		self.type = 'cu_log'
		self.tmp_major =  126
		self.tmp_minor = 1
		self.rh_major = 24
		self.rh_minor = 6
		self.prcp_major = 5
		self.prcp_minor =7
		self.lwet_major = 118
		self.lwet_minor = 2
		newa_weather.__init__(self,stn)
		
class miwx_vars(newa_weather) :
	def __init__(self,stn_id) :
		self.type = 'miwx'
		self.tmp_major = 126
		self.tmp_minor = 7
		self.rh_major = 143
		self.rh_minor = 3
		self.prcp_major = 5
		self.prcp_minor = 12
		self.lwet_major = 118
		self.lwet_minor = 6
		newa_weather.__init__(self,stn_id)		

class ucc_vars(newa_weather) :
	def __init__(self,stn_id) :
		self.type = 'ucc'
		self.tmp_major = 126
		self.tmp_minor = 8
		self.rh_major = 141
		self.rh_minor = 3
		self.prcp_major = 5
		self.prcp_minor = 18
		self.lwet_major = 118
		self.lwet_minor = 11
		newa_weather.__init__(self,stn_id)		

class oardc_vars(newa_weather) :
	def __init__(self,stn_id) :
		self.type = 'oardc'
		self.tmp_major = 23
		self.tmp_minor = 10
		self.rh_major = 24
		self.rh_minor = 12
		self.prcp_major = 5
		self.prcp_minor = 13
		self.lwet_major = 118
		self.lwet_minor = 7
		newa_weather.__init__(self,stn_id)		
				
class nysm_vars(newa_weather) :
	def __init__(self,stn_id) :
		self.type = 'nysm'
		self.tmp_major = 23
		self.tmp_minor = 11
		self.rh_major = 24
		self.rh_minor = 13
		self.prcp_major = 5
		self.prcp_minor = 14
		self.lwet_major = 118	#doesn't exist
		self.lwet_minor = 0		#doesn't exist
		newa_weather.__init__(self,stn_id)		
				
class nwon_vars(newa_weather) :
	def __init__(self,stn_id) :
		self.type = 'nwon'
		self.tmp_major = 23
		self.tmp_minor = 14
		self.rh_major = 24
		self.rh_minor = 16
		self.prcp_major = 5
		self.prcp_minor = 17
		self.lwet_major = 118
		self.lwet_minor = 10
		newa_weather.__init__(self,stn_id)		
				
class general_dm_weather(object) :

	def __init__(self,stn,eDate,sister) :
		# a statFlg of None means that everything is fine.
		self.statFlg = None 
		self.sisters = sister	
		self.rhVar = None
		self.prcpVar = None
		self.tmpVar = None
		self.lwetVar = None
		self.initialize_main_station(stn)
		self.setup_time(eDate)
		self.setup_arrays()
		self.nativeStnID = stn

	def setup_time(self,eDate) :
		(year,month,day) = eDate
		eTime = apply(DateTime.Date,(year,month,day,23))
		self.eTime = eTime + DateTime.RelativeDate(hours=+1)
		self.sTime = DateTime.DateTime(year,1,1,0)



	def get_tsvar_class(self,stn) :
		if stn[0:3] == '42.' or stn[0:3] == '43.':
			obj = ucc_vars(stn)
			return obj
		elif stn[0:1] >= '1' and stn[0:1] <= '9' and stn[1:2] >= '0' and stn[1:2] <= '9':
			obj = njwx_vars(stn)
			return obj
		elif len(stn) == 4 and stn[0:1].upper() == 'K':
			obj = icao_weather(stn)
			return obj
		elif len(stn) == 4 :
			obj = oardc_vars(stn)
			return obj
		elif len(stn) == 6 and (stn[0:3] == "cu_" or stn[0:3] == "um_" or stn[0:3] == "uc_" or stn[0:3] == "un_") :
			obj = culog_vars(stn)
			return obj
		elif stn[0:3] == "ew_":
			obj = miwx_vars(stn)
			return obj
		elif stn[0:5] == "nysm_":
			obj = nysm_vars(stn)
			return obj
		elif len(stn) == 7 and stn[2:3] == '_':
			obj = nwon_vars(stn)
			return obj
		elif len(stn) == 3 or len(stn) == 6 :
			obj = newa_vars(stn)
			return obj
		else :
			print 'unknown station'
			sys.exit()
		

	def setup_sister_tmp(self) :
		stnId = self.sisters['temp']
		self.tmpVar = self.get_tsvar_class(stnId)
		self.tmpVar.initialize_ucan()
		self.tmpVar.initialize_tmp()
		
	def setup_sister_prcp(self) :
		stnId = self.sisters['prcp']
		self.prcpVar = self.get_tsvar_class(stnId)
		self.prcpVar.initialize_ucan()
		self.prcpVar.initialize_prcp()
		
	def setup_sister_rh(self) :
		stnId = self.sisters['rhum']
		self.rhVar = self.get_tsvar_class(stnId)
		self.rhVar.initialize_ucan()
		self.rhVar.initialize_rh()
		
	def setup_sister_lwet(self) :
		stnId = self.sisters['lwet']
		self.lwetVar = self.get_tsvar_class(stnId)
		self.lwetVar.initialize_ucan()
		self.lwetVar.initialize_lwet()


	def initialize_main_station(self,stn) :
		if len(stn) >= 3 and len(stn) <= 6 :
			self.stn = self.get_tsvar_class(stn)
			self.stn.initialize_ucan()
			self.stn.initialize_tmp()
			self.stn.initialize_rh()
			self.stn.initialize_prcp()
			self.stn.initialize_lwet()
		else :
			print 'I do not think %s is a Newa Station'%(stn)
			sys.exit()
		

	

	def setup_arrays(self) :
		self.dates = []
		self.rh_vals = []
		self.rh_flgs = []
		self.tmp_vals = []
		self.tmp_flgs = []
		self.prcp_vals = []
		self.prcp_flgs = []
		self.lwet_vals = []
		self.lwet_flgs = []

#	ndfd data access added 9/23/2015 - kle
	def get_fcst_data (self, stn, requested_var, requested_time):
		hourly_fcst = -999
		try:
			forecast_db = hashopen('/ndfd/hourly_forecasts.db','r')
			try:
				stn_dict = loads(forecast_db[stn.upper()])
			except:
				stn_dict = {}
			forecast_db.close()
			if requested_var == 'prcp': requested_var = 'qpf'
			dkey = tuple(requested_time[0:3])
			if stn_dict.has_key(requested_var) and stn_dict[requested_var].has_key(dkey):
				hr = requested_time[3]
				hourly_fcst = stn_dict[requested_var][dkey][hr]
#			else:
#				print 'stn_dict does not have key',stn_dict.has_key(requested_var),stn_dict[requested_var].has_key(dkey)
		except:
			print_exception()
		return hourly_fcst


	def get_temperature(self,start,end) :
		tmp = self.stn.tmp
		(sum,values,flags,dates) = self.stn.get_observed(tmp,start,end)

		if sum==0 :
			if self.tmpVar == None :
				self.setup_sister_tmp()
			(sum,values,flags,dates) = self.tmpVar.get_observed(self.tmpVar.tmp,start,end)
			if sum == 0 :
				self.statFlg = 1	
				raise weatherError

		elif sum < len(values) :
			missing_indices = []
			for index in range(len(flags)) :
				if flags[index] != 1 :
					missing_indices.append(index)
			if self.tmpVar == None:
				self.setup_sister_tmp()
			(sSum,sVals,sFlgs,sDates) = self.tmpVar.get_observed(self.tmpVar.tmp,start,end)

			if sSum != 0 :
				fixed = 0
				for index in missing_indices:
					if sFlgs[index] == 1 :
						flags[index] = 1
						values[index] = sVals[index]
						fixed = fixed + 1
					# added following section 9/23/2015 -kle
					else:
						fval = self.get_fcst_data (self.nativeStnID, 'temp', sDates[index])
						if fval != -999:
							flags[index] = 1
							values[index] = (5.0/9.0) * (fval - 32.0)
							fixed = fixed + 1
						
		self.dates = self.dates + dates
		self.tmp_vals = self.tmp_vals + values
		self.tmp_flgs = self.tmp_flgs + flags


	def get_precipitation(self,start,end) :
		prcp = self.stn.prcp
		(sum,values,flags,data) = self.stn.get_observed(prcp,start,end)

		if sum==0 :
			if self.prcpVar == None :
				self.setup_sister_prcp()
			(sum,values,flags,dates)=self.prcpVar.get_observed(self.prcpVar.prcp,start,end)
			if sum==0 :
				self.statFlg = 1 
				raise weatherError

		elif sum < len(values) :
			missing_indices = []
			for index in range(len(flags)) :
				if flags[index] != 1 :
					missing_indices.append(index)
			if self.prcpVar == None:
				self.setup_sister_prcp()
			(sSum,sVals,sFlgs,sDates)=self.prcpVar.get_observed(self.prcpVar.prcp,start,end)

			if sSum != 0 :
				fixed = 0
				for index in missing_indices:
					if sFlgs[index] == 1 :
						flags[index] = 1
						values[index] = sVals[index]
						fixed = fixed + 1
					# added following section 9/23/2015 -kle
					else:
						fval = self.get_fcst_data (self.nativeStnID, 'prcp', sDates[index])
						if fval != -999:
							flags[index] = 1
							values[index] = fval
							fixed = fixed + 1
						else:
							flags[index] = 1
							values[index] = 0.00	#set missing to zero precip
							fixed = fixed + 1
						
		self.prcp_vals = self.prcp_vals + values
		self.prcp_flgs = self.prcp_flgs + flags


	def get_rh(self,start,end) :
		rh = self.stn.rh
		(sum,values,flags,data) = self.stn.get_observed(rh,start,end)

		if sum==0 :
			if self.rhVar == None :
				self.setup_sister_rh()
			(sum,values,flags,dates)=self.rhVar.get_observed(self.rhVar.rh,start,end)

			if sum == 0 :
				self.statFlg = 1 
				raise weatherError

		elif sum < len(values) :
			missing_indices = []
			for index in range(len(flags)) :
				if flags[index] != 1 :
					missing_indices.append(index)
			if self.rhVar == None:
				self.setup_sister_rh()
			(sSum,sVals,sFlgs,sDates)=self.rhVar.get_observed(self.rhVar.rh,start,end)

			if sSum != 0 :
				fixed = 0
				for index in missing_indices:
					if sFlgs[index] == 1 :
						flags[index] = 1
						values[index] = sVals[index]
						fixed = fixed + 1
					# added following section 9/23/2015 -kle
					else:
						fval = self.get_fcst_data (self.nativeStnID, 'rhum', sDates[index])
						if fval != -999:
							flags[index] = 1
							values[index] = fval
							fixed = fixed + 1
						
		self.rh_vals = self.rh_vals + values
		self.rh_flgs = self.rh_flgs + flags


	def get_lwet(self,start,end) :
		lwet = self.stn.lwet
		(sum,values,flags,data) = self.stn.get_observed(lwet,start,end)

		if sum==0 :
			if self.lwetVar == None :
				self.setup_sister_lwet()
			(sum,values,flags,dates)=self.lwetVar.get_observed(self.lwetVar.lwet,start,end)
			# if there is no sister lwet, try estimating from RH
			if sum == 0 :
				fixed = 0
				for index in range(len(values)) :
					trh = self.rh_vals[index]
					if trh != -999:
						flags[index] = 1
						if trh >= 90:
							values[index] = 60
						else:
							values[index] = 0
						fixed = fixed + 1
		elif sum < len(values) :
			missing_indices = []
			for index in range(len(flags)) :
				if flags[index] != 1 :
					missing_indices.append(index)
			if self.lwetVar == None:
				self.setup_sister_lwet()
			(sSum,sVals,sFlgs,sDates)=self.lwetVar.get_observed(self.lwetVar.lwet,start,end)
			if sSum != 0 :
				fixed = 0
				for index in missing_indices:
					if sFlgs[index] == 1 :
						flags[index] = 1
						values[index] = sVals[index]
						fixed = fixed + 1
					# added following section 9/23/2015 -kle
					else:
						trh = self.rh_vals[index]
						if trh != -999:
							flags[index] = 1
							if trh >= 90:
								values[index] = 60
							else:
								values[index] = 0
							fixed = fixed + 1
						
		self.lwet_vals = self.lwet_vals + values
		self.lwet_flgs = self.lwet_flgs + flags



	def loop_through_time(self) :

		obsTime = DateTime.DateTime(self.sTime.year,self.sTime.month,self.sTime.day,self.sTime.hour)
		nexTime = obsTime + DateTime.RelativeDate(months=+1)

		while obsTime < self.eTime :
			
			if nexTime > self.eTime :
				end = (self.eTime.year,self.eTime.month,self.eTime.day,self.eTime.hour)
			else :
				end = (nexTime.year,nexTime.month,nexTime.day,nexTime.hour)
			
			start = (obsTime.year,obsTime.month,obsTime.day,obsTime.hour)
			
			try :
				self.get_temperature(start,end)
				self.get_precipitation(start,end)
				self.get_rh(start,end)
				self.get_lwet(start,end)
			except weatherError :
				break
			except :
				print_exception()
				break
			
			obsTime = DateTime.DateTime(nexTime.year,nexTime.month,nexTime.day,nexTime.hour)
			nexTime = obsTime + DateTime.RelativeDate(months=+1)
			
		self.stn.release_tmp()
		if self.tmpVar :
			self.tmpVar.release_tmp()
		self.stn.release_rh()
		if self.rhVar :
			self.rhVar.release_rh()
		self.stn.release_prcp()
		if self.prcpVar :
			self.prcpVar.release_prcp()
		self.stn.release_lwet()
		if self.lwetVar :
			self.lwetVar.release_lwet()

	
	def get_mildew_missing(self) :
		last_date = self.dates[-1]
		last_time = apply(DateTime.Date,last_date)
		sTime = last_time + DateTime.RelativeDate(hours=+1)
		eTime = DateTime.DateTime(sTime.year+1,1,1,0)
		missing_hours = []
		missing_days = []

		while sTime < eTime :
			localTime =  getLocalFromEST_time(sTime) 
			missing_days.append(localTime.day_of_year)
			missing_hours.append(localTime.hour)
			sTime = sTime + DateTime.RelativeDate(hours=+1)
		return (missing_days,missing_hours)


	def get_downy_mildew_weather(self) :
		if ( (len(self.dates) != len(self.tmp_vals)) or
		( len(self.tmp_vals) != len(self.rh_vals)) or
		( len(self.rh_vals) != len(self.prcp_vals) ) or
		( len(self.prcp_vals) != len(self.lwet_vals) )   )  :
			print 'length problem',len(self.dates),len(self.tmp_vals),len(self.rh_vals),len(self.prcp_vals),len(self.lwet_vals)
			return [0]
		days = [0,]*len(self.dates)
		hours = [0,]*len(self.dates)
		yearOfHours = 24*366
		ok = [0,]*yearOfHours

		for index in range(len(self.dates)) :
			try :
				this_date = self.dates[index]
				(day,hour) = getLocalFromEST(this_date)

				days[index] = day
				hours[index] = hour
				tmpFlg = self.tmp_flgs[index]
				rhFlg = self.rh_flgs[index]
				prcpFlg = self.prcp_flgs[index]
				lwetFlg = self.lwet_flgs[index]
				
				if (tmpFlg) and (rhFlg) and (prcpFlg) and (lwetFlg) :
					ok[index] = 1 
					
			except :
				print_exception()
				break
	

		# --------------------------------------------
		# We need our lists to be 366*24, for the
		# downy mildew program (dmcast)
		# --------------------------------------------
		diffNum = len(ok) - len(self.dates)
		missing_list = [-999.0,]*diffNum
		tmp = self.tmp_vals + missing_list
		rh = self.rh_vals + missing_list
		prcp = self.prcp_vals + missing_list
		lwet = self.lwet_vals + missing_list

		(missing_days,missing_hours) = self.get_mildew_missing()	
		days = days + missing_days
		hours = hours + missing_hours
		return (self.statFlg,self.dates,hours,days,tmp,rh,prcp,lwet,ok)


	
def get_mildew_weather(stn,eDate,sister) :
	obj = general_dm_weather(stn,eDate,sister)
	obj.loop_through_time()
	if obj.statFlg:
		return [obj.statFlg,]
	results = obj.get_downy_mildew_weather()
	return results

	#(dates,hours,days,tmp,rh,prcp,lwet,ok) = obj.get_downy_mildew_weather()
	#ofile = open('new_weather.txt','w')
	#for index in range(len(dates)) :
	#	hh = hours[index]
	#	dd = days[index]
	#	t = tmp[index]
	#	r = rh[index]
	#	p = prcp[index]
	#	lw = lwet[index]
	#	o = ok[index]
	#	ofile.write("%d,%d,%5.2f,%4.0f,%5.2f,%5.2f,%d\n"%(dd,hh,t,r,p,lw,o))


if __name__ == '__main__' :
	stn = 'fre'
	eDate = (2009,8,25)
	sister = {'temp': 'cu_gfr',
			'prcp': 'cu_gfr',
			'lwet': 'fre', 
			'rhum': 'cu_gfr',
			'wspd': 'cu_gfr', 
			'wdir': 'cu_gfr', 
			'srad': 'cu_gfr'}
	get_mildew_weather(stn,eDate,sister)
