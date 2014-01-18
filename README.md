python-gist
============

A command line GitHub gist posting application in Python. 

Your options for authentication:

* Basic support for 2 Factor Authentication - I have not tested the SMS backup.

* Username/password combos - python-gists will request an authorisation and save a token. See https://github.com/settings/applications

* Personal Access Tokens - these are the same ones you use for git-over-HTTPS if you've got 2FA enabled. See https://github.com/settings/applications, create a new token, then launch python-gist with the -o option


Usage
=====
	$ python python-gist.py --help
	Usage: python-gist.py [options]

	Options:
	-h, --help            show this help message and exit
	-o, --oauth           Use a Personal Access Token instead of a username/password
	-d DESC, --description="a description"
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
* Add an option to deauthorise/cleanup the script
* Make the script installable
* Package this for Windows
* Ability to use an external editor
* Implement the rest of the GitHub API, in github_auth.py
* More unit tests
* Tag an actual release
* Pin the API use to a version, instead of using the "beta"
* Python 3 version 

Thanks
======
* Amit Saha, for adding a whole lot of features
* HaveF, for telling me that my OAuth implementation was completely broken
* The author of https://help.github.com/articles/creating-an-oauth-token-for-command-line-use
