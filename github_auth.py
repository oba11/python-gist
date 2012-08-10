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


class github_auth(object):
    def __init__(self,appName = None,appURL = None, ClientID = None, ClientSecret = None, username = None, password = None):
        self.appName = appName
        self.appURL = appURL
        self.ClientID = ClientID
        self.ClientSecret = ClientSecret
        #todo, probably need to handle clienttoken here too
        self.username = username
        self.password = password
        self.session = None

    def get_session_simple(self,scopes,token_auth_callback=None,username=None,password=None):
        if token_auth_callback is None: #http://stackoverflow.com/questions/1802971/nameerror-name-self-is-not-defined
            token_auth_callback = self.console_authorise_callback

        if self.ClientID is not None and self.ClientSecret is not None:
            token = self.authorise_web(scopes,token_auth_callback)
        else:
            token = self.authorise_password(username,password)
        if token is not None:
            return self.get_session(token)
        else:
            raise('Could not get token, please check your credentials')
         #todo: more checks

    def get_session(self, token):
        auth_header = {"Authorization": str.format("token {0}",token)}
        if self.session is None: self.session = requests.Session(headers=auth_header, verify=True)
        return self.session

    def authorise_web(self,redir=None,scopes=None,callback_function=None):
        auth_handler = OAuth2(self.ClientID, self.ClientSecret, "https://github.com/login/", redir, authorization_url='oauth/authorize', token_url='oauth/access_token')
        get_auth_url = auth_handler.authorize_url(scopes)
        code = callback_function()

        if code != None:
            return code
        else: raise('Could not get OAuth authorisation code')

    def authorise_password(self,username,password):
        response = requests.get('https://api.github.com/authorizations', auth=(username, password))

        if response.ok:
            token_response = self.get_existing_token(response)
            if token_response is not None:
                return token_response
            else:
                return self.get_new_token((username,password))
        elif response.status_code==401:
            raise("Username or password incorrect, try again.")
        #    
        #else:
        #    self.handle_http_error(self,response)
        #

    def get_existing_token(self, response):
        for auth_dictionary in response.json:
            if self.appName in auth_dictionary['app']['name']:
                return auth_dictionary['token']
        return None
        
    def get_new_token(self,cached_credentials):
        headers = {'accept': 'application/json'}
        payload = {'scopes': 'gist', 'note': 'Requested by ' + self.appName, 'note_url': self.appURL}
        response = requests.post('https://api.github.com/authorizations', auth=cached_credentials, data=json.dumps(payload), headers=headers)
        
        if response.ok:
            return response.json['token']
        else:
            raise(str.format("Couldn't get client token - {0}: {1}", response.status_code, response.text)) #yes, this is likely to be a json response but I want to make sure I see the error    

    def console_authorise_callback(self):
        self.openbrowser(get_auth_url)
        code = raw_input('OK, if you have a code from the webpage, please enter it here: ')
        return code

    def openbrowser(self,url):
        friendly_message = "Press Enter if you'd like to go to " + url + " with your default browser to authorise this script on GitHub, otherwise hit ctrl/command-C now"
        raw_input(friendly_message)

        #from http://stackoverflow.com/questions/1795111/is-there-a-cross-platform-way-to-open-a-file-browser-in-python
        if sys.platform=='win32':
            os.startfile(url)
        elif sys.platform=='darwin':
            subprocess.Popen(['open', url])
        else:
            try:
                subprocess.Popen(['xdg-open', url])
            except OSError:
                str.format("Couldn't open a browser on your system ({0}), please go to {1}",sys.platform,url)
