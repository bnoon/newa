#!/usr/local/bin/python

import sys
from mx import DateTime
from print_exception import print_exception
import newaInput_io, newaModel_io
class program_exit (Exception):
	pass

def apple_biofix_process (request):
	try:
#	 	retrieve input
		if request.form:
			try:
				now = DateTime.now()
				if request.form['submit field'] == 'Submit':
					outfil = open('/Users/keith/Sites/NEWA/apple_biofix_%s.txt'%now.year,'w')
					for key in request.form.keys():
						if key != 'submit field' and request.form[key] != '':
							outfil.write('%s, %s\n' % (key,request.form[key]))
					outfil.close
					return newaInput_io.apple_biofix_results('Biofix results saved.')
				else:
					return newaInput_io.apple_biofix_results('No changes saved.')
			except:
				print_exception()
				raise program_exit('Error processing form')
		else:
			return newaModel_io.errmsg('Error processing form; no form')
	except program_exit,msg:
		print msg
		return newaModel_io.errmsg('Error processing form')
	except:
		print_exception()
		return newaModel_io.errmsg('Unexpected error')

def apple_biofix_input ():
	try:
		now = DateTime.now()
		biofix_dict = {}
		outfil = open('/Users/keith/Sites/NEWA/apple_biofix_%s.txt'%now.year,'r')
		for line in outfil.readlines():
			key,val = line.split(',')
			biofix_dict[key] = val
		outfil.close
		return newaInput_io.apple_biofix_input(biofix_dict)
	except:
		print_exception()
		return newaModel_io.errmsg('Error obtaining previous data')
