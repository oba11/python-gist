python-gist
============

A command line GitHub gist posting application in Python. 

As of July 2013, this uses API tokens.

As of November 2013, this has basic support for 2 Factor Authentication via application - I have not tested the SMS backup.

This application probably needs to be refactored (github_auth.py should not depend on the console/stdout!)

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

Removal
====
Delete the API token that python-gists requested from https://github.com/settings/applications

Delete the oauth.cfg file (%AppData%\python-gist on Windows, ~/.config/python-gist on *nix)

Todos
=====
* Add an option to deauthorise the script
* Make the script installable
* External editor? 

Thanks
======
* Amit Saha, for adding a whole lot of features
* HaveF, for telling me that my OAuth implementation was completely broken
* The author of https://help.github.com/articles/creating-an-oauth-token-for-command-line-use
