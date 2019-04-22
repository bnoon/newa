class WeatherData:
	weatherTable = {}
	numDays = 0
	def __init__(self, weatherData):

	# Assumes array of arrays (TimeInterval, MinTemp, MaxTemp, TotalRadition) passed to routine
	# TimeInterval is one day in this growth model implementation

		try:
			self.numDays = len(weatherData)
			for day in weatherData:
				dayIndex = int(day[0])
				for y in range(1,len(day)):
					self.weatherTable[(dayIndex,y)] = float(day[y])
		except:
			print "Error reading weather data"

	def minTemp(self, index):
		return self.weatherTable[(index, 1)]

	def maxTemp(self, index):
		return self.weatherTable[(index, 2)]

	def totalRadiation(self, index):
		return self.weatherTable[(index, 3)]

	def numberOfDays(self):
		return self.numDays