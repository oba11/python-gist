import atexit

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
    OAUTH_CONFIG_FILENAME = 'oauth.cfg'
    CONFIG_FILENAME = 'defaults.cfg'
    
    def choose_authmethod(self):
        choice = raw_input('Please select an authorisation method.\r\n \
                            1. Open a web browser, cut and paste the access token.\r\n \
                            2. Use your GitHub username and password to get a token automagically.\r\n \
                            (Default is 2): ')
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
        self.config.filehandle = open(self.OAUTH_CONFIG_FILENAME, 'a')
        
        if not self.config.has_section('Credentials'):
            self.config.add_section('Credentials')

        self.client_token = self.config.get_quiet('Credentials', 'client_token')
        self.client_id = self.config.get_quiet('Credentials', 'client_id')
        self.client_secret = self.config.get_quiet('Credentials', 'client_secret')
        self.redir_url = "http://voltagex.github.com/python-gists/oauth.html"
        self.auth = GitHubAuth("python-gist", "http://github.com/voltagex/python-gist", self.client_id, self.client_secret)

        if self.client_token is None:
            self.choose_authmethod()
        #else:
        #    print "Loaded saved access token, I'm good to go." 
    
    def authorise_web(self):
        return self.auth.authorise_web(self, redir=self.redir_url, scopes="gist")

    def authorise_password(self):
        username = raw_input("Please enter your username: ")
        password = getpass.getpass("Please enter your password: ")
        return self.auth.authorise_password(username, password)


    def post_gist(self, description="Posted by python-gist", public=False, gist_files=None, content=None):
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
        else: print "Error " + response.text
        return
    
    def cleanup(self):
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
    raw_input()
