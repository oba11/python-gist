import sys
import os
import subprocess
import atexit

import ConfigParser
import getpass

import json

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

import github_auth

class gist(object):
    OAUTH_CONFIG_FILENAME = 'oauth.cfg'
    CONFIG_FILENAME = 'defaults.cfg'
    
    def choose_authmethod(self):
        choice = raw_input('Please select an authorisation method.\r\n1. Open a web browser, cut and paste the access token.\r\n2. Use your GitHub username and password to get a token automagically.\r\n(Default is 2): ')
        choice = choice.strip()
        if choice == '2' or choice == '':
            self.authorise_password() 
            return
        if choice == '1':
            self.authorise_web()
            return
        else: self.choose_authmethod()

    def __init__(self):
        atexit.register(self.cleanup)

        self.config = ConfigParser.RawConfigParser()
        self.config.read([self.OAUTH_CONFIG_FILENAME])
        self.config.filehandle = open(self.OAUTH_CONFIG_FILENAME,'a')
        
        if not self.config.has_section('Credentials'):
            self.config.add_section('Credentials')

        self.ClientToken = self.config.get_quiet('Credentials','client_token')
        self.ClientID = self.config.get_quiet('Credentials','client_id')
        self.ClientSecret = self.config.get_quiet('Credentials','client_secret')
        self.redir_url = "http://voltagex.github.com/python-gists/oauth.html"
        self.auth = github_auth.github_auth("python-gist","http://github.com/voltagex/python-gist",self.ClientID,self.ClientSecret)

        if self.ClientToken is None:
            self.choose_authmethod()
        #else:
        #    print "Loaded saved access token, I'm good to go." 
    
    def authorise_web():
        return self.auth.authorise_web(self,redir=self.redir_url,scopes="gist")

    def authorise_password():
        username = raw_input("Please enter your username: ")
        password = getpass.getpass("Please enter your password: ")
        return self.auth.authorise_password(username,password)


    def post_gist(self,description="Posted by python-gist", public=False, gist_files=None, content=None):
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
        response = self.auth.get_session(self.ClientToken).post("https://api.github.com/gists", data=json.dumps(payload))
        if response.ok:
            return response.json['html_url']
        else: print "Error " + response.text
        return
    
    def cleanup(self):
        self.config.set('Credentials', 'Client_ID', self.ClientID)
        self.config.set('Credentials', 'Client_Secret', self.ClientSecret)
        self.config.set('Credentials', 'Client_Token', self.ClientToken)
        self.config.write(self.config.filehandle)
        
        self.config.filehandle.flush()
        self.config.filehandle.close()
        
if __name__ == "__main__":
    def get_quiet(self,section,value):
        if self.has_option(section,value):
            return self.get(section,value)
        return None
    ConfigParser.RawConfigParser.get_quiet = get_quiet
    
gist = gist()
if (sys.stdin):
    print gist.post_gist(content=sys.stdin.readlines())
    raw_input()