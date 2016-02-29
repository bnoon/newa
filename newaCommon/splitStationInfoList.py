from print_exception import print_exception

try:
	from stn_info import stn_info
	state_dicts = {}
	for stn in stn_info.keys():
		state = stn_info[stn]['state']
		stn_info[stn]['name'] = stn_info[stn]['name'].replace(', %s' % state.upper(), '')
		if not state_dicts.has_key(state):
			state_dicts[state] = {}
		state_dicts[state][stn] = stn_info[stn]
			
	outfil_all = open('stn_info_all.py', 'w')
	outfil_all.write('stn_info = {')

	for state in state_dicts.keys():
		print 'processing:',state

		outfil = open('stn_info_%s.py' % state.lower(), 'w')
		outfil.write('stn_info = {')
		for stn in state_dicts[state].keys():
			outfil.write("'%s': %s,\n" % (stn, state_dicts[state][stn]))
##			state_dicts[state][stn]['name'] = '%s, %s' %(state_dicts[state][stn]['name'], state_dicts[state][stn]['state'])
			outfil_all.write("'%s': %s,\n" % (stn, state_dicts[state][stn]))
		outfil.write('}')
		outfil.close()	

	outfil_all.write('}')
	outfil_all.close()	

except:
	print "Error encountered"
	print_exception()
