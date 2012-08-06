import sys
import os
import subprocess
import atexit

import ConfigParser


import requests
from requests_oauth2 import OAuth2



class gist(object):
    OAUTH_CONFIG_FILENAME = 'oauth.cfg'
    CONFIG_FILENAME = 'defaults.cfg'
    
    def __init__(self):
        atexit.register(self.cleanup)

        self.config = ConfigParser.RawConfigParser()
        self.config.read([self.OAUTH_CONFIG_FILENAME])
        self.config.filehandle = open(self.OAUTH_CONFIG_FILENAME,'wb')
        
        if not self.config.has_section('Credentials'):
            self.config.add_section('Credentials')

        self.ClientToken = self.config.get_quiet('Credentials','ClientToken')
        self.ClientID = self.config.get_quiet('Credentials','ClientID')
        self.ClientSecret = self.config.get_quiet('Credentials','ClientSecret')

        if self.ClientToken is None:
            if (self.ClientID or self.ClientSecret) is None:
                print "Please add a ClientID and ClientSecret to oauth.cfg under Credentials"
                self.config.set('Credentials','ClientID','your_id_here')
                self.config.set('Credentials','ClientSecret','your_secret_here')
                self.config.write(self.config.filehandle)
                sys.exit(1)

            self.authorise()
       
        else:
            print "Loaded saved access token, I'm good to go."
    
    def authorise(self):
        scopes = "gist"
               
        auth_handler = OAuth2(self.ClientID, self.ClientSecret, "https://github.com/login/", "http://voltagex.github.com/python-gists/oauth.html", authorization_url='oauth/authorize', token_url='oauth/access_token')
        get_auth_url = auth_handler.authorize_url(scopes)
        self.openbrowser(get_auth_url)

        code = raw_input('OK, if you have a code from the webpage, please enter it here: ')

        if code != None:
            self.config.set('Credentials', 'ClientToken',code)
            
            print "Thanks, I've saved that for later"
            sys.exit(0)
        else:
            print "Sorry, I didn't get a code there. Exiting now."
            sys.exit(1)

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
