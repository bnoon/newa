import os
from print_exception import print_exception

try:
	os.chdir("/Users/keith/kleweb/newaUtil")
	os.system("sh restart_newaUtil.sh")
	os.chdir("/Users/keith/kleweb/newaLister")
	os.system("sh restart_newaLister.sh")
	os.chdir("/Users/keith/kleweb/newaDisease")
	os.system("sh restart_newaDisease.sh")
	os.chdir("/Users/keith/kleweb/newaModel")
	os.system("sh restart_newaModel.sh")
	os.chdir("/Users/keith/kleweb/newaTools")
	os.system("sh restart_newaTools.sh")
	os.chdir("/Users/keith/kleweb/newaGraph")
	os.system("sh restart_newaGraph.sh")
	os.chdir("/Users/keith/kleweb/newaVegModel")
	os.system("sh restart_newaVegModel.sh")
	print "Restart complete"
except:
	print "Error restarting jobs"
	print_exception()