def getNearestCoop (baselat, baselon, varmajor, sd, ed, detailed_check):
	import math
	from mx import DateTime
	from omniORB import CORBA
	import Meta, Data, ucanCallMethods

	NameAny = Meta.MetaQuery.NameAnyPair
	LatLonDistance = Meta.MetaQuery.LatLonDistance
	any = CORBA.Any
	tc = CORBA.TypeCode
	tc_shortseq = tc(Meta.ShortSeq)
	tc_floatseq = tc(Meta.FloatSeq)
	tc_LatLonDistance = CORBA.TypeCode(Meta.MetaQuery.LatLonDistance)
	
	ucan = ucanCallMethods.general_ucan()
	
	if detailed_check == 1:
		sd_dt = DateTime.DateTime(sd[0],sd[1],sd[2],0)
		ed_dt = DateTime.DateTime(ed[0],ed[1],ed[2],0)
	
	search_rad = 40.			# initial radius 40 miles
	non_matches = []

	query = ucan.get_query()

	while search_rad < 101:
		qual = [
			NameAny('var_major_id',any(tc_shortseq,[varmajor])),
			NameAny('begin_date',any(tc_shortseq,sd)),
			NameAny('end_date',any(tc_shortseq,ed)),
			NameAny('near_latlon',any(tc_LatLonDistance,LatLonDistance(baselat,baselon,search_rad,'miles'))),
			]

		results = query.getStnInfoAsSeq(qual, ('coop_id',))
		if len(results) > 0:
			for r in results :
				d = ucanCallMethods.NameAny_to_dict(r)
				cid = d.get('coop_id','')
				uid = d.get('ucan_id','')
				if cid != '' and uid != '':
					if cid in non_matches:
						continue		#already checked
						
					if detailed_check == 1:
						# Make sure the valid date range is within dates of interest
						try:
							data_daily = ucan.get_data()
							vals = None
							vals = data_daily.newTSVar(varmajor,0,uid)
							dates = vals.getValidDateRange()
							svd_dt = DateTime.DateTime(*dates[0])
							evd_dt = DateTime.DateTime(*dates[1])
							vals.release()
						except:
							if vals: vals.release()
							non_matches.append(cid)
							output = ucanCallMethods.print_exception()
							for i in output: print i
							continue
				
					if detailed_check == 0 or \
					  (detailed_check == 1 and sd_dt >= svd_dt and ed_dt <= evd_dt):
					  	query.release()
						return (cid)
					else:
						non_matches.append(cid)
		
		search_rad = search_rad + 60.       #increase radius by 60 miles
		
	query.release()
	return (-1)	
	
def getHourlyStaInfo(stn):
	from bsddb import hashopen
	import cPickle
	from ucanCallMethods import print_exception
	
	try:
		stn_info = hashopen('/newa/morecs/icao_info.pydb','r')
		keys = stn_info.keys()
		if stn in keys:
			stn_data = cPickle.loads(stn_info[stn])
			name = stn_data.get('station_name','Unknown')
			lat  = stn_data.get('lat',-999.)
			lon  = stn_data.get('lon',-999.)
			gmt_offset = stn_data.get('gmt_offset',-999.)
		else:
			name = 'Unknown'
			lat,lon,gmt_offset = -999.,-999.,-999
			print 'No data for',stn,'in station info file.'
	except:
		output = print_exception()
		for i in output: print i

	return (name,lat,lon,gmt_offset)

def getAsosCommissionDate(stn):
	# Obtain ASOS commissioning date from text file
	import string
	a_date=[9999,99,99]
	i1 = open('/newa/morecs/ASOS_sites.txt','r')
	while 1:
		l1=i1.readline()
		if len(l1)==0:
			break
			
		info=string.split(l1)
		stn_asos = info[2]
		if stn==stn_asos:
			a_date=[int(info[5][0:4]), int(info[5][4:6]), int(info[5][6:8])]
			break

	i1.close()
	return a_date
