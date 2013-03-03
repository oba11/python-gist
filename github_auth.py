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
    def __init__(self, **kwargs): #app_name = None, app_url = None, client_id = None,  client_secret = None, username = None, password = None):
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
        self.app_name = kwargs.get('app_name')
        self.app_url = kwargs.get('app_url')
        self.client_id = kwargs.get('client_id')
        self.client_secret = kwargs.get('client_secret')
        #todo, probably need to handle clienttoken here too
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.session = None

    def get_session_simple(self, scopes, token_auth_callback=None, username=None, password=None):
        """ Get a requests Session object, as long as either OAuth token auth or username and password is passed in

            :param scopes: Single or multiple OAuth scopes, comma separated as defined at: http://developer.github.com/v3/oauth/#scopes
            :type scopes: str.

            :param token_auth_callback: Callback to deal with second step of OAuth - GitHub returns a URL where the user will have to confirm your requested access
            :type token_auth_callback: instancemethod.

            :param username: GitHub username
            :type username: str.

            :param password: GitHub password
            :type password: str.
        """
        if token_auth_callback is None: #http://stackoverflow.com/questions/1802971/nameerror-name-self-is-not-defined
            token_auth_callback = self.console_authorise_callback

        if self.client_id is not None and self.client_secret is not None:
            token = self.authorise_web(scopes, token_auth_callback)
        else:
            token = self.authorise_password(username, password)
        if token is not None:
            return self.get_session(token)
        else:
            raise(Exception('Could not get token, please check your credentials'))
         #todo: more checks

    def get_session(self, token):
        """
        Return a requests Session object, given an OAuth token value

        :param token: OAuth token value
        :type token: str.
        """
        auth_header = {"Authorization": str.format("token {0}", token)}
        if self.session is None:
            new_session = requests.session()
            new_session.headers = auth_header
            new_session.headers['User-Agent'] = self.app_name + " via github_auth.py, see github.com/voltagex/python-gist"
            new_session.verify = True
        self.session = new_session
        return self.session

    def authorise_web(self, redir=None, scopes=None, callback_function=None):
        """
        Perform OAuth authorisation via a web page

        :param redir: URL to redirect to - specified when you created your OAuth client ID
        :type redir: str.

        :param scopes: Single or multiple OAuth scopes, comma separated as defined at: http://developer.github.com/v3/oauth/#scopes
        :type scopes: str.

        :param callback_function: callback that will be passed the URL
        :type callback_function: instancemethod.
        """
        auth_handler = OAuth2(self.client_id,
                              self.client_secret,
                              "https://github.com/login/",
                              redir,
                              authorization_url='oauth/authorize',
                              token_url='oauth/access_token')
        auth_url = auth_handler.authorize_url(scopes)

        if callback_function is None:
            callback_function = self.console_authorise_callback

        code = callback_function(auth_url)

        if code != None:
            return code
        else: raise('Could not get OAuth authorisation code')

    def authorise_password(self, scopes, username, password):
        """
        Get an OAuth token using a GitHub username and password

        :param scopes: Single or multiple OAuth scopes, comma separated as defined at: http://developer.github.com/v3/oauth/#scopes
        :type scopes: str.

        :param username: GitHub username
        :type username: str.

        :param password: GitHub password
        :type password: str.
        """
        response = requests.get('https://api.github.com/authorizations', auth=(username, password))

        if response.ok:
            token_response = self.get_existing_token(response)
            if token_response is not None:
                return token_response
            else:
                return self.get_new_token(scopes, (username, password))
        elif response.status_code == 401:
            raise(Exception("Username or password incorrect, try again."),'AuthenticationError')

    def get_existing_token(self, response):
        """
        Get an existing OAuth token after a request to https://api.github.com/authorizations

        :param response: requests Response object containing authentication data
        :type response: dict.
        """
        for auth_dictionary in response.json:
            if self.app_name in auth_dictionary['app']['name']:
                return auth_dictionary['token']
        return None

    def get_new_token(self, scopes, cached_credentials):
        """
        Get a new token via request to https://api.github.com/authorizations
        :param scopes: Single or multiple OAuth scopes, comma separated as defined at: http://developer.github.com/v3/oauth/#scopes
        :type scopes: str.

        :param cached_credentials: GitHub credentials saved from previous functions, tuple of (username, password)
        :type cached_credentials: tuple.
        """
        headers = {'accept': 'application/json'}
        payload = {'scopes': scopes, 'note': 'Requested by ' + self.app_name, 'note_url': self.app_url}
        response = requests.post('https://api.github.com/authorizations', auth=cached_credentials, data=json.dumps(payload), headers=headers)

        if response.ok:
            return response.json['token']
        else:
            raise(Exception(str.format("Couldn't get client token - {0}: {1}", response.status_code, response.text)),'AuthenticationError') #yes, this is likely to be a json response but I want to make sure I see the error

    def console_authorise_callback(self, auth_url):
        """
        Example function used as a callback for the authorisation process - ask the user to enter a code after displaying it in their default browser

        :param auth_url: Authorisation URL passed in by the calling function
        :type auth_url: str.
        """
        self.openbrowser(auth_url)
        code = raw_input('OK, if you have a code from the webpage, please enter it here: ')
        return code

    def openbrowser(self, url):
        """
        Open the user's default web browser after notifying them

        :param url: URL to open
        :type url: str.
        """
        friendly_message = "I need an OAuth token to work." + '\n' + \
                           "Press Enter if you'd like to go to " + url + '\n' + \
                           "with your default browser to authorise this script on GitHub, otherwise hit ctrl/command-C now"
        raw_input(friendly_message)
        webbrowser.open_new_tab(url)