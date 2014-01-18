import unittest
import json
import requests
import httpretty
from listhelper import header_list_to_dict
try:
    import github_auth
except ImportError:
    import os,sys,inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir)
    import github_auth

class unauthorized(unittest.TestCase):
    @httpretty.activate
    def test_fail_authorisation(self):
        request_object = None
        with open('./test_data/invalid.response','r') as f:
            request_object = json.load(f)
        headers=header_list_to_dict(request_object['headers'])
        headers.pop('status')
        httpretty.register_uri(httpretty.GET,'https://api.github.com/authorizations'
                               ,body=request_object['text']
                               ,status=request_object['status_code']
                               ,adding_headers=headers)
        g = github_auth.GitHubAuth()
        g.get_token_with_password('','invalid','password')
    
    @httpretty.activate
    def test_twofactor_authorisation(self):
        request_object = None
        with open('./test_data/twofactor.response','r') as f:
            request_object = json.load(f)
        headers=header_list_to_dict(request_object['headers'])
        headers.pop('status')
        httpretty.register_uri(httpretty.GET,'https://api.github.com/authorizations'
                               ,body=request_object['text']
                               ,status=request_object['status_code']
                               ,adding_headers=headers)
        g = github_auth.GitHubAuth()
        g.get_token_with_password('noscope','invalid','password', otp_callback = self.simple_callback)

    def simple_callback(self, scopes, username, password, code_received_via):
        print scopes
        print username
        print password
        print code_received_via
       

if __name__ == '__main__':
    unittest.main()
