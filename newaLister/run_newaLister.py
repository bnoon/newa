#!/usr/bin/python
import sys
sys.path.insert(1,'/usr/local/share/tsvar')

from quixote.publish import Publisher
from quixote.server.scgi_server import QuixoteHandler
from scgi.quixote_handler import main

from newaLister.program_interface import RootDirectory
	
pname = 'newaLister'
pnum = 4010

script_name = '/%s'%pname

def create_publisher():
	return Publisher(RootDirectory(),
					 error_log="newaLister_err.log",
					 access_log="newaLister_acc.log",
					 display_exceptions="plain" )

def create_handler(parent_fd):
	return QuixoteHandler (parent_fd, create_publisher, script_name)

if __name__ == '__main__':
    main(create_handler)
