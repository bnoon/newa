class Singleton(object):
	def __new__(cls, *args, **kwds):
		it = cls.__dict__.get("__it__")
		if it is not None:
			return it
		cls.__it__ = it = object.__new__(cls)
		it.init(*args, **kwds)
		return it
	def init(self, *args, **kwds):
		pass


class stationInfo (Singleton):
	def init (self):
		self.info = {}

	#
	# define a mapping interface to the info
	#
	
	def keys (self):
		return self.info.keys()

	def values (self):
		return [self[id] for id in self.keys()]

	def items (self):
		return [(id, self[id]) for id in self.keys()]

	def __getitem__ (self, key):
		return self.info[key]

	def get (self, key, default=None):
		try:
			return self[key]
		except KeyError:
			return default
			
	def getvar (self, key, var):
		if not self.info.has_key(key):
			self.info[key] = {}
			
		if self.info[key].has_key(var):
			pass
		else:
			if var in ['name','lat','lon','gmt_offset']:
				from station_searches import getHourlyStaInfo
				name,lat,lon,gmt_offset = getHourlyStaInfo(key)

#				get gmt offset from nearest coop station if not available
				if gmt_offset == -999 or gmt_offset == -99:
					from station_searches import getNearestCoop
					from ucanStandardRequests import get_metaDictionary
					varmajor=4; detailed_check=0
					sd=(1,1,1); ed=(9999,12,31)
					nearby_station = getNearestCoop(lat,lon,varmajor,sd,ed,detailed_check)
					e={}
					e=get_metaDictionary(str(nearby_station))
					try:
						gmt_offset=float(e[-1]['gmt_offset'])
					except:
						print 'Unknown gmt_offset for',name,key,'; assuming 5'
						gmt_offset=5

				self.setvar(key, 'lat', lat)
				self.setvar(key, 'lon', lon)
				self.setvar(key, 'gmt_offset', gmt_offset)
				self.setvar(key, 'name', name)
			elif var in ['asos_date']:
				from station_searches import getAsosCommissionDate
				self.info[key][var] = getAsosCommissionDate(key)
			else:
				self.info[key][var] = None
		return self.info[key][var]
		
	def setvar (self, key, var, value):
		if not self.info.has_key(key): self.info[key] = {}
		self.info[key][var] = value
		
	def has_key (self, key):
		print 'has_key'
		return self.info.has_key(key)

	def __setitem__ (self, key, value):
		self.info[key] = value

	def __delitem__ (self, key):
		del self.info[key]

	def __contains__(self, key):
		return key in self.info


