#!/usr/bin/python
from quixote.publish import Publisher
from quixote.server.scgi_server import QuixoteHandler
from scgi.quixote_handler import main

from newaTools.program_interface import RootDirectory
	
pname = 'newaTools'
pnum = 4017

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
