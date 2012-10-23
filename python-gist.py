#!/usr/bin/env python
import atexit
import configpaths
import ConfigParser
import getpass
import sys

try:
    import requests
except ImportError:
    print "Please pip install requests (and probably requests_oauth2)"
    sys.exit(1)
try:
    from requests_oauth2 import OAuth2
except ImportError:
    print "Please pip install requests_oauth2"
    sys.exit(1)

import json

from github_auth import GitHubAuth

class Gist(object):
    """
    Methods for working with GitHub Gists
    """
    OAUTH_CONFIG_FILENAME = configpaths.get_config_path('python-gists','oauth.cfg')
  
    def choose_authmethod(self):
        choice = None
        try:
            choice = raw_input('Please select an authorisation method.\r\n \t1. Open a web browser, cut and paste the access token.\r\n \t2. Use your GitHub username and password to get a token automagically.\r\n \t(Default is 2): ')
        except EOFError:
            pass
        if not choice:
            choice = raw_input()
        choice = choice.strip()

        if choice == '2' or choice == '':
            self.authorise_password() 
            return
        if choice == '1':
            self.authorise_web()
            return
        else: self.choose_authmethod()

    def __init__(self):
        """
        Read and set up config, set up authentication
        """
        atexit.register(self.cleanup)

        self.config = ConfigParser.RawConfigParser()
        self.config.read([self.OAUTH_CONFIG_FILENAME])
        self.config.filehandle = open(self.OAUTH_CONFIG_FILENAME, 'a')
        
        if not self.config.has_section('Credentials'):
            self.config.add_section('Credentials')

        self.client_token = self.config.get_quiet('Credentials', 'client_token')
        self.client_id = self.config.get_quiet('Credentials', 'client_id')
        if self.client_id is None:
            self.client_id = "6aa08c7fa4d67e09a26f" #todo, don't do this.
        self.client_secret = self.config.get_quiet('Credentials', 'client_secret')
        self.redir_url = "http://voltagex.github.com/python-gist/oauth.html"

        self.auth = GitHubAuth(app_name="python-gist", app_url="http://github.com/voltagex/python-gist", client_id=self.client_id, client_secret=self.client_secret)

        if (self.client_token is None or self.client_id is None) and sys.stdin.isatty():
            self.choose_authmethod()
        elif not sys.stdin.isatty():
            print "Sorry, can't accept anything on stdin until I have some GitHub credentials to work with"
            sys.exit(1)
       



        #else:
        #    print "Loaded saved access token, I'm good to go." 
    
    def authorise_web(self):
        """
        Authorise this script via web browser
        """
        return self.auth.authorise_web(redir=self.redir_url, scopes="gist")

    def authorise_password(self):
        """
        Authorise this script via GitHub username and password
        """
        username = raw_input("Please enter your username: ")
        password = getpass.getpass("Please enter your password: ")
        return self.auth.authorise_password(username, password)


    def post_gist(self, description="Posted by python-gist", public=False, gist_files=None, content=None):
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
            files = {"python-gist-post.txt": {"content": content}}
        elif gist_files is not None: 
            files = gist_files 
        else:
            raise("Either content or gist_files must be set")
        payload = {
                    "description": description,
                    "public": public,
                    "files": files,
                   }
        response = self.auth.get_session(self.client_token).post("https://api.github.com/gists", data=json.dumps(payload))
        if response.ok:
            return response.json['html_url']
        else: 
            print "Error " + response.text
            return

    def cleanup(self):
        """
        Cleanup, set config and flush before exisiting
        """
        self.config.set('Credentials', 'Client_ID', self.client_id)
        self.config.set('Credentials', 'Client_Secret', self.client_secret)
        self.config.set('Credentials', 'Client_Token', self.client_token)
        self.config.write(self.config.filehandle)
        
        self.config.filehandle.flush()
        self.config.filehandle.close()
        
if __name__ == "__main__":
    def get_quiet(self, section, value):
        if self.has_option(section, value):
            return self.get(section, value)
        return None
    ConfigParser.RawConfigParser.get_quiet = get_quiet
    
gist = Gist()
if (sys.stdin):
    print gist.post_gist(content=sys.stdin.readlines())
