from mx import DateTime
from bsddb import hashopen
from cPickle import loads
from print_exception import print_exception

def get_precip_forecast (stn,start_date_dt,end_date_dt):
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
				if stndict['qpf'].has_key(theDate): qpf = stndict['qpf'][theDate]
				else: qpf = [miss]*24
				if stndict['pop12'].has_key(theDate): pop12 = stndict['pop12'][theDate]
				else: pop12 = [miss]*24
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
					hourly_fcst.append((theTime,qpf[hr],pop12[hr]))
					# distribute precipitation over last 6 hours
					if qpf[hr] != miss:
						x = len(hourly_fcst)-1
						for i in range(x,x-6,-1):
							if i >= 0: 
								hourly_fcst[i] = hourly_fcst[i][0:1] + (qpf[hr]/6.,) + hourly_fcst[i][2:]
				theDate_dt = theDate_dt + DateTime.RelativeDate(days = +1)
	except:
		print_exception()
	return hourly_fcst

#stn = 'cli'
#start_date_dt = DateTime.DateTime(2009,4,16,8)
#end_date_dt = DateTime.DateTime(2009,4,22,23)
#forecast_dict = get_precip_forecast(stn,start_date_dt,end_date_dt)
#for item in forecast_dict:
#	print item