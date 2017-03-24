from mx import DateTime
from bsddb import hashopen
from cPickle import loads
from print_exception import print_exception

def get_hourly_forecast (stn,start_date_dt,end_date_dt):
	hourly_fcst = []
	miss = -999
	try:
		stn = stn.upper()
		pdict = hashopen('/ndfd/hourly_forecasts.db','r')
		if pdict.has_key(stn):
			stndict = loads(pdict[stn])
			pdict.close()
			firstday_hour = start_date_dt.hour
			lastday_hour = end_date_dt.hour
			start_date_dt = start_date_dt + DateTime.RelativeDate(hour=0)
			end_date_dt = end_date_dt + DateTime.RelativeDate(hour=0)
			theDate_dt = start_date_dt
			while theDate_dt <= end_date_dt:
				theDate = (theDate_dt.year,theDate_dt.month,theDate_dt.day)
				if stndict['temp'].has_key(theDate): temp = stndict['temp'][theDate]
				else: temp = [miss]*24
				if stndict['rhum'].has_key(theDate): rhum = stndict['rhum'][theDate]
				else: rhum = [miss]*24
				if stndict['wspd'].has_key(theDate): wspd = stndict['wspd'][theDate]
				else: wspd = [miss]*24
				if stndict['qpf'].has_key(theDate): qpf = stndict['qpf'][theDate]
				else: qpf = [miss]*24
				if theDate_dt == start_date_dt:
					shour = firstday_hour
				else:
					shour = 0
				if theDate_dt == end_date_dt:
					ehour = lastday_hour
				else:
					ehour = 23
				for hr in range(shour,ehour+1):
					theTime = (theDate_dt.year,theDate_dt.month,theDate_dt.day,hr)
					eflags = ('F', 'F', 'M', 'F', 'F', 'M', 'M', 'M')
					hourly_fcst.append((theTime,temp[hr],qpf[hr],miss,rhum[hr],wspd[hr],miss,miss,miss,eflags))
					#tempv,prcpv,lwetv,rhumv,wspdv,wdirv,sradv,st4iv
					# distribute precipitation over last 6 hours
					if qpf[hr] != miss:
						x = len(hourly_fcst)-1
						for i in range(x,x-6,-1):
							if i >= 0: 
								hourly_fcst[i] = hourly_fcst[i][0:2] + (qpf[hr]/6.,) + hourly_fcst[i][3:]
				theDate_dt = theDate_dt + DateTime.RelativeDate(days = +1)
	except:
		print_exception()
	return hourly_fcst

#stn = 'gen'
#start_date_dt = DateTime.DateTime(2009,3,1,8)
#end_date_dt = DateTime.DateTime(2009,3,8,8)
#forecast_dict = get_hourly_forecast(stn,start_date_dt,end_date_dt)
#for item in forecast_dict:
#	print item