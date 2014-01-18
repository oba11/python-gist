import sys

try:
    import requests
except ImportError:
    print "Please pip install requests"
    sys.exit(1)

import json
import logging

class GitHubAuth(object):
    """Class handling authentication to GitHub via OAuth/token request"""
    def __init__(self, **kwargs): #app_name = None, app_url = None, client_id = None, client_secret = None,
                                  #username = None, password = None):
        """ Initialise a GitHubAuth object
            Note either client_id and client_secret for OAuth or
            username and password for token request via basic auth
            are required

            :param app_name: Application name, displayed on the user's Applications page
            :type app_name: str.

            :param app_url: Application URL, displayed on the user's Applications page
            :type app_url: str.

            :param client_secret: OAuth client secret
            :type client_secret: str.

            :param username: Username for basic auth/token request
            :type username: str.

            :param password: Password for basic auth/token request
            :type password: str.
        """
        self.app_name = kwargs.get('app_name')
        self.app_url = kwargs.get('app_url')
        self.client_token = kwargs.get('client_token')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.scopes = []
        self.session = requests.session()
        self.session.headers.update({'User-Agent': self.app_name + " via github_auth.py, see github.com/voltagex/python-gist"})

    def get_session_simple(self, scopes=['gist'], username=None, password=None):
        """ Get a requests Session object, as long as either OAuth token auth or username and password is passed in

            :param scopes: Single or multiple OAuth scopes, comma separated as defined at: http://developer.github.com/v3/oauth/#scopes
            :type scopes: str.

            :param username: GitHub username
            :type username: str.

            :param password: GitHub password
            :type password: str.
        """

        if token is not None:
            return self.get_session(token)
        elif password is not None:
             token = self.authorise_password(scopes, username, password)
        else:
            raise(Exception('Could not get token, please check your credentials'))

    def get_session(self, token):
        """
        Return a requests Session object, given an OAuth token value

        :param token: OAuth token value
        :type token: str.
        """
        auth_header = {"Authorization": str.format("token {0}", token)}
        self.session.headers.update(auth_header)
        return self.session

    def get_token_with_password(self, scopes, username, password, otp_callback=None):
        """
        TODO: Don't let this recurse, it's too confusing.
        Get an OAuth token using a GitHub username and password

        :param scopes: Single or multiple OAuth scopes, comma separated as defined at: http://developer.github.com/v3/oauth/#scopes
        :type scopes: str.

        :param username: GitHub username
        :type username: str.

        :param password: GitHub password
        :type password: str.
        """
        headers = None
        logging.log(3,'Sending a request without a 2 factor auth code first')
        response = self.session.get('https://api.github.com/authorizations', auth=(username, password), headers={})
        
        if not self.username:
            self.username = username
        if not self.password:
            self.password = password
        self.scopes = scopes

        if not response.ok:
            message = response.text #todo, get this as a dict
            if ("OTP" in message):
                if (otp_callback):
                    code_received_via = response.headers['X-GitHub-OTP']
                    code = otp_callback(code_received_via)
                    response = self.get_token_with_twofactorauth(code)
                else:
                    raise(Exception("GitHub asked for 2FA but no otp_callback was specified"))
            else: #actually unauthorized/in an error state at this point
                logging.log(3,"Unauthorised, GitHub returned {0} with {1}",(response.status_code,message))
                raise(Exception("Username or password incorrect, try again."),'AuthenticationError')

        token_response = self.get_existing_token(response)
        if token_response is not None:
            print 'Got existing token'
            return token_response
        else:
            return self.get_new_token()


    def get_token_with_twofactorauth(self, code):
            session.headers.update({'X-Github-OTP', code})
            logging.log('Sending auth request  for {0} including two factor auth code',(username))
            response = session.get('https://api.github.com/authorizations', auth=(self.username, self.password), headers=headers)
       
        
    def get_existing_token(self, response):
        """
        Get an existing OAuth token after a request to https://api.github.com/authorizations

        :param response: requests Response object containing authentication data
        :type response: dict.
        """
        for auth_dictionary in response.json():
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
           return response.json()['token']
        else:
            raise(Exception(str.format("Couldn't get client token - {0}: {1}", response.status_code, response.text)),'AuthenticationError') #yes, this is likely to be a json response but I want to make sure I see the error

    def check_personal_access_token(self, token):
        return self.session.get('https://api.github.com/user',auth=(token,'x-oauth-basic')).ok