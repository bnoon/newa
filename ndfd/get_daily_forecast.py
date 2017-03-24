import sys
from mx import DateTime
from bsddb import hashopen
from cPickle import loads
from print_exception import print_exception
from get_precip_forecast import get_precip_forecast

def get_daily_forecast (stn,start_date_dt,end_date_dt):
	daily_fcst = []
	miss = -999
	try:
		stn = stn.upper()
##NEW: next line
		forecast_dict = hashopen('/ndfd/daily_forecasts.db','r')
		if forecast_dict.has_key(stn):
	#		get all daily precip for period
			hourly_fcst = get_precip_forecast(stn,start_date_dt,end_date_dt)
			dly_ppt = {}
			ppt_cnt = 0
			ppt_sum = 0.0
			for dt,qpf,pop in hourly_fcst:
				if qpf != miss:
					ppt_sum = ppt_sum + qpf
					ppt_cnt = ppt_cnt + 1
				if dt[3] == 23:
					if ppt_cnt > 0: dly_ppt[dt[0:3]] = ppt_sum
					ppt_cnt = 0
					ppt_sum = 0.0
	#		get temps and combine with precip, if available
			stndict = loads(forecast_dict[stn])
			theDate_dt = start_date_dt
			while theDate_dt <= end_date_dt:
				int_date = (theDate_dt.year,theDate_dt.month,theDate_dt.day)
				if stndict.has_key(int_date):
					tmax,tmin = stndict[int_date]
					tave = (tmax+tmin)/2.
					eflags = ('', '', '', 'M', 'M', 'M', 'M', 'M')
				else:
					tmax,tmin,tave = miss,miss,miss
					eflags = ('M', 'M', 'M', 'M', 'M', 'M', 'M', 'M')
				if dly_ppt.has_key(int_date):
					rain = dly_ppt[int_date]
					eflags = (eflags[0],eflags[1],eflags[2],"",'M', 'M', 'M', 'M')
				else:
					rain = miss
				daily_fcst.append(([int_date[0],int_date[1],int_date[2]],tave,tmax,tmin,rain,miss,miss,miss,miss,miss,miss,miss,eflags))
				theDate_dt = theDate_dt + DateTime.RelativeDate(days = +1)
		forecast_dict.close()
	except:
		print_exception()
	return daily_fcst

#stn = 'cu_gfr'
#start_date_dt = DateTime.DateTime(2009,5,1)
#end_date_dt = DateTime.DateTime(2009,5,18)
#forecast_dict = get_daily_forecast(stn,start_date_dt,end_date_dt)
#for item in forecast_dict:
#	print item