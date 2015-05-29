import downy_mildew
from mx import DateTime

eTime = apply(DateTime.Date,(2009,9,23))
smry_dict = {'accend': eTime,
		'cultivar': 'Concord',
		'sister': {'temp': 'mex', 'lwet': 'mex', 'prcp': 'mex', 'rhum': 'kfzy'},
		'stn': 'scr'}

for index in range(1):
	obj = downy_mildew.general_dm(smry_dict)
	smry_dict = obj.run_dm()
	print smry_dict.keys()
	if 'statMsg' not in smry_dict :
		print smry_dict['primary']
		print smry_dict['incubation']
		print smry_dict['els12']
	else :
		print smry_dict['statMsg']
	
