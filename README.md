***NOTE: Currently to use this script with __OAuth__, you'll have to add your own application in your GitHub profile 
and add the client ID and client secret to the config. I've been advised not to distribute the client secret in open source code - 
therefore I'll need to build a workaround, probably an OAuth proxy. For now, your username and password will work to get the same token that's created at the end of the OAuth process***

python-gists
============

A command line GitHub gist posting application in Python. 

Usage
=====
	$ python python-gist.py --help
	Usage: python-gist.py [options]

	Options:
	-h, --help            show this help message and exit
	-d DESC, --description=DESC
        Description for the gist
	-f FILES, --files=FILES
        Comma seperated list of file(s) to post as a gist
	-p, --private         Use to post a private gist

	$ python python-gist.py 
	Loaded saved access token, I'm good to go.
	Enter your Gist contents
	***********************
	****^D  when done******
	This is a gist
	https://gist.github.com/4096470

	$ python python-gist.py -d 'Multi file gist' -f python-gist.py,README.md
	Loaded saved access token, I'm good to go.
	Uploading files..
	https://gist.github.com/4096475
	
	$ python python-gist.py -d 'Multi file gist' -f python-gist.py,README.md -p
	Loaded saved access token, I'm good to go.
	Uploading files..
	https://gist.github.com/b766c2becf1874b1665b

Todos
=====
* OAuth proxy
* Code refactoring
* Make the script installable
* External editor? 

Thanks
======
* Amit Saha, for adding a whole lot of features
* HaveF, for telling me that my OAuth implementation was completely broken
