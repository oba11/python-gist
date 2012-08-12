import webbrowser

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

class GitHubAuth(object):
    """Class handling authentication to GitHub via OAuth/token request"""
    def __init__(self, app_name = None, app_url = None, client_id = None, 
                 client_secret = None, username = None, password = None):
        """ Initialise a GitHubAuth object
            Note either client_id and client_secret for OAuth or
            username and password for token request via basic auth
            are required

            :param app_name: Application name, displayed on the user's Applications page
            :type app_name: str.

            :param app_url: Application URL, displayed on the user's Applications page
            :type app_url: str.
            
            :param client_id: OAuth client ID
            :type client_id: str.

            :param client_secret: OAuth client secret
            :type client_secret: str.

            :param username: Username for basic auth/token request
            :type username: str.

            :param password: Password for basic auth/token request
            :type password: str.          
        """
        self.app_name = app_name
        self.app_url = app_url
        self.client_id = client_id
        self.client_secret = client_secret
        #todo, probably need to handle clienttoken here too
        self.username = username
        self.password = password
        self.session = None

    def get_session_simple(self, scopes, token_auth_callback=None, username=None, password=None):
        """  """
        if token_auth_callback is None: #http://stackoverflow.com/questions/1802971/nameerror-name-self-is-not-defined
            token_auth_callback = self.console_authorise_callback

        if self.client_id is not None and self.client_secret is not None:
            token = self.authorise_web(scopes, token_auth_callback)
        else:
            token = self.authorise_password(username, password)
        if token is not None:
            return self.get_session(token)
        else:
            raise('Could not get token, please check your credentials')
         #todo: more checks

    def get_session(self, token):
        auth_header = {"Authorization": str.format("token {0}", token)}
        if self.session is None: 
            self.session = requests.Session(headers=auth_header, verify=True)
        return self.session

    def authorise_web(self, redir=None, scopes=None, callback_function=None):
        auth_handler = OAuth2(self.client_id, 
                              self.client_secret, 
                              "https://github.com/login/", 
                              redir, 
                              authorization_url='oauth/authorize', 
                              token_url='oauth/access_token')
        auth_url = auth_handler.authorize_url(scopes)
        code = callback_function(auth_url)

        if code != None:
            return code
        else: raise('Could not get OAuth authorisation code')

    def authorise_password(self, username, password):
        response = requests.get('https://api.github.com/authorizations', auth=(username, password))

        if response.ok:
            token_response = self.get_existing_token(response)
            if token_response is not None:
                return token_response
            else:
                return self.get_new_token((username, password))
        elif response.status_code == 401:
            raise("Username or password incorrect, try again.")
        #    
        #else:
        #    self.handle_http_error(self,response)
        #

    def get_existing_token(self, response):
        for auth_dictionary in response.json:
            if self.app_name in auth_dictionary['app']['name']:
                return auth_dictionary['token']
        return None
        
    def get_new_token(self, cached_credentials):
        headers = {'accept': 'application/json'}
        payload = {'scopes': 'gist', 'note': 'Requested by ' + self.app_name, 'note_url': self.app_url}
        response = requests.post('https://api.github.com/authorizations', auth=cached_credentials, data=json.dumps(payload), headers=headers)
        
        if response.ok:
            return response.json['token']
        else:
            raise(str.format("Couldn't get client token - {0}: {1}", response.status_code, response.text)) #yes, this is likely to be a json response but I want to make sure I see the error    

    def console_authorise_callback(self, auth_url):
        self.openbrowser(auth_url)
        code = raw_input('OK, if you have a code from the webpage, please enter it here: ')
        return code

    def openbrowser(self, url):
        friendly_message = "Press Enter if you'd like to go to " + url + \
                           "with your default browser to authorise this script on GitHub, \
                            otherwise hit ctrl/command-C now"
        raw_input(friendly_message)
        webbrowser.open_new_tab(url)