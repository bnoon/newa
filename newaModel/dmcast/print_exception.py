
import sys
def print_exception(type=None, value=None, tb=None, limit=None):
	if type is None:
		type, value, tb = sys.exc_info()
	import traceback
	list = traceback.format_tb(tb, limit) + traceback.format_exception_only(type, value)
	print 'Traceback'
	for item in list:
		print item	
