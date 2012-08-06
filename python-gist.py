import sys
import os
import subprocess
import atexit

import ConfigParser
import getpass

import requests
from requests_oauth2 import OAuth2




class gist(object):
    OAUTH_CONFIG_FILENAME = 'oauth.cfg'
    CONFIG_FILENAME = 'defaults.cfg'
    
    def choose_authmethod(self):
        choice = raw_input('Please select an authorisation method.\r\n1. Open a web browser, cut and paste the access token.\r\n2. Use your GitHub username and password to get a token automagically.\r\n(Default is 2): ')
        if choice == '2':
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
        self.config.filehandle = open(self.OAUTH_CONFIG_FILENAME,'wb')
        
        if not self.config.has_section('Credentials'):
            self.config.add_section('Credentials')

        self.ClientToken = self.config.get_quiet('Credentials','client_token')
        self.ClientID = self.config.get_quiet('Credentials','client_id')
        self.ClientSecret = self.config.get_quiet('Credentials','client_secret')

        if self.ClientToken is None:
            if (self.ClientID or self.ClientSecret) is None:
                print "Please add a ClientID and ClientSecret to oauth.cfg under Credentials"
                self.config.set('Credentials','client_id','your_id_here')
                self.config.set('Credentials','client_secret','your_secret_here')
                self.config.write(self.config.filehandle)
                sys.exit(1)
            
            self.choose_authmethod()
        else:
            print "Loaded saved access token, I'm good to go."
        
       
    
    def authorise_web(self):
        scopes = "gist"
               
        auth_handler = OAuth2(self.ClientID, self.ClientSecret, "https://github.com/login/", "http://voltagex.github.com/python-gists/oauth.html", authorization_url='oauth/authorize', token_url='oauth/access_token')
        get_auth_url = auth_handler.authorize_url(scopes)
        self.openbrowser(get_auth_url)

        code = raw_input('OK, if you have a code from the webpage, please enter it here: ')

        if code != None:
            self.config.set('Credentials', 'client_token', code)
            print "Thanks, I've saved that for later"
        else:
            print "Sorry, I didn't get a code there. Exiting now."
            sys.exit(1)

        payload = {'client_id': self.ClientID, 'client_secret': self.ClientSecret, 'code': code}
        headers = {'accept': 'application/json'}
        response = requests.post('https://github.com/login/oauth/access_token',payload,headers=headers)
        self.ClientToken = response.json['access_token']
        self.config.set('Credentials','client_token', response.json['access_token'])
        self.config.write(self.config.filehandle)

    def openbrowser(self,url):
        friendly_message = "Press Enter if you'd like to go to " + url + " with your default browser to authorize this script on GitHub, otherwise hit ctrl/command-C now"
        raw_input(friendly_message)

        #from http://stackoverflow.com/questions/1795111/is-there-a-cross-platform-way-to-open-a-file-browser-in-python
        if sys.platform=='win32':
            os.startfile(url)
            #subprocess.Popen(['start', url], shell= True)
        elif sys.platform=='darwin':
            subprocess.Popen(['open', url])
        else:
            try:
                subprocess.Popen(['xdg-open', url])
            except OSError:
                # er, think of something else to try
                # xdg-open *should* be supported by recent Gnome, KDE, Xfce
                str.format("Couldn't open a browser on your system ({0}), please go to {1}",sys.platform,url)


    def authorise_password(self):
        username = raw_input("Please enter your username: ")
        password = getpass.getpass("Please enter your password: ")

        response = requests.get('https://api.github.com/authorizations', auth=(username, password))
        for auth_dictionary in response.json:
            if auth_dictionary['app']['name'] == 'python-gists':
                self.config.set('Credentials','client_token',auth_dictionary['token'])
                self.ClientToken = auth_dictionary['token']
                self.config.write(self.config.filehandle)
                print "Found existing auth token"
                return
    
    def cleanup(self):
        self.config.filehandle.flush()
        self.config.filehandle.close()

if __name__ == "__main__":
    def get_quiet(self,section,value):
        if self.has_option(section,value):
            return self.get(section,value)
        return None
    ConfigParser.RawConfigParser.get_quiet = get_quiet
    



    test = gist()
    raw_input()
