#!/usr/bin/python
import sys
sys.path[0]='.'
sys.path.insert(1,'/usr/local/share/tsvar')
sys.path.insert(1,'/newa')

from quixote.publish import Publisher
from quixote.server.scgi_server import QuixoteHandler
from scgi.quixote_handler import main

from newaModel.program_interface import RootDirectory
	
pname = 'newaModel'
pnum = 4012

script_name = '/%s'%pname

def create_publisher():
	return Publisher(RootDirectory(),
					 error_log="%s_err.log"%pname,
					 access_log="%s_acc.log"%pname,
					 display_exceptions="plain" )

def create_handler(parent_fd):
	return QuixoteHandler (parent_fd, create_publisher, script_name)

if __name__ == '__main__':
    main(create_handler)
