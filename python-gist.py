#!/usr/bin/env python
import atexit
import configpaths
import ConfigParser
import getpass
import sys
import optparse
import os
import logging

root = logging.getLogger()

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

try:
    import requests
except ImportError:
    print "Please pip install requests"
    sys.exit(1)

finally:
    version = int(requests.__version__[0])
    if (version < 2):
        raise(Exception("Unfortunately I only support requests v2 for now, you have " + requests.__version__))

import json
from github_auth import GitHubAuth

class Gist(object):
    """
    Methods for working with GitHub Gists
    """
    OAUTH_CONFIG_FILENAME = configpaths.get_config_path('python-gist', 'oauth.cfg')

    def __init__(self):
        """
        Read and set up config, set up authentication
        """
        atexit.register(self.save_configuration)
        self.client_secret = None #allow cleanup to run even if we don't finish __init__

        self.config = ConfigParser.RawConfigParser()
        self.config.read([self.OAUTH_CONFIG_FILENAME])
        self.config.filehandle = open(self.OAUTH_CONFIG_FILENAME, 'a')

        if not self.config.has_section('Credentials'):
            self.config.add_section('Credentials')

        self.client_token = self.config.get_quiet('Credentials', 'client_token')
        self.auth = GitHubAuth(app_name="python-gist", app_url="http://github.com/voltagex/python-gist")

        #todo, this logic sucks.
    def authorise(self,use_personal_access_token):
        if (self.client_token is None) and sys.stdin.isatty():
                self.authorise_password(use_personal_access_token)
        elif not sys.stdin.isatty() and self.client_token is None:
                # In case a pipe is trying to write to us
                print "Sorry, can't accept anything on stdin until I have some GitHub credentials to work with"
                sys.exit(1)
        else:
                print "Loaded saved access token, I'm good to go."

    def authorise_password(self, use_personal_access_token = False):
        """
        Authorise this script via GitHub username and password
        """
        try:
            username = raw_input("Please enter your username: ")
            if not use_personal_access_token:
                password = getpass.getpass("Please enter your password: ")
                token = self.auth.get_token_with_password('gist', username, password)
            else:
                token = getpass.getpass("Please enter your personal access token: ")
                if not self.auth.check_personal_access_token(token):
                    raise(Exception("Incorrect token"))

            self.client_token = token
            print "Saved your token, start this script again to post gists"
            sys.exit(0)
        except Exception as ex:
            print ex.message
        sys.exit(1)

    def twofactor(self,code_type):
        return raw_input('Enter your 2FA code: ')

    def post_gist(self, description, public, gist_files, content):
        """
        Post a gist, either single text string or a dictionary of files in the form of
        {"filename.ext": {"content": "some text"}}

        :param description: Gist description
        :type: str.

        :param public: Post a public or private Gist
        :type: bool.

        :param gist_files: dictionary of files for Gist
        :type: dict.

        :param content: string content for Gist
        :type: str.
        """
        if content is not None:
            files = {"gist.txt": {"content": str(content)}}
        elif gist_files is not None:
            files = gist_files
        else:
            raise ("Either content or gist_files must be set")
        payload = {
            "description": description,
            "public": public,
            "files": files,
        }

        authorised_client = self.auth.get_session(self.client_token)
        response = authorised_client.post("https://api.github.com/gists", data=json.dumps(payload))

        if response.ok:
            return response.json()['html_url']
        else:
            print "Error " + response.text
            return

    def save_configuration(self):
        """
        Cleanup, set config and flush before exiting
        """
        #recheck the config file in case it's changed during runtime
        current_token = self.config.get_quiet('Credentials','client_token')

        if (self.client_token != current_token and self.client_token is not None):
            self.config.set('Credentials', 'client_token', self.client_token)

            self.config.write(self.config.filehandle)
            self.config.filehandle.flush()
            self.config.filehandle.close()

if __name__ == "__main__":
    def get_quiet(self, section, value):
        if self.has_option(section, value):
            data = self.get(section,value)
            if data.strip() != '':
                return data
        return None
    ConfigParser.RawConfigParser.get_quiet = get_quiet



# setup options
parser = optparse.OptionParser()
parser.add_option('-o', '--oauth',action="store_true",help='Use a Personal Access Token instead of a username/password',dest='oauth')
parser.add_option('-d', '--description',help='Description for the gist',dest='desc')
parser.add_option('-f', '--files', help='Comma separated list of file(s) to post as a gist', dest='files')
parser.add_option('-p', '--private',help='Use to post a private gist', action='store_true',dest='private')

oauth = False
public = True

(opts, args) = parser.parse_args()

#check the options

if opts.__dict__['oauth']:
    oauth = True

if opts.__dict__['desc']:
    description = opts.__dict__['desc']
else:
    description = 'python-gist gist'

if opts.__dict__['private']:
    public = False
 
gist = Gist()
gist.authorise(oauth)

gist_files = None
if opts.__dict__['files']:
    content = None
    gist_files = {}
    for fname in opts.__dict__['files'].split(','):
        with open(fname) as f:
            gist_files[fname] = {'content':f.read()}

else:
    if sys.platform == 'win32':
        exit_char = '^Z'
    else:
        exit_char = '^D'

    print 'Enter your Gist contents'
    print '***********************'
    print '****',exit_char,'when done ****'

    content = ''.join(sys.stdin.readlines()) #Don't do this.
    
    print gist.post_gist(description, public, gist_files, content)
