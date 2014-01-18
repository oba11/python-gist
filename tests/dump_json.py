#This shouldn't be run, it's just a useful tool for developing something like github_auth
import requests
import json
agent = "Dumping json responses to file for github_auth.py, see github.com/voltagex/python-gist"
session = requests.session()
session.headers['User-Agent'] = agent

def dump_response(response, filename):
    response_dict = dict()
    response_dict['url'] = response.url
    response_dict['headers'] = response.headers.items()
    response_dict['status_code'] = response.status_code
    response_dict['reason'] = response.reason
    response_dict['text'] = response.text
    
    with open(filename,'w') as f:
        f.write(json.dumps(response_dict))
        f.close()
def invalid_response(session):
    response = session.get('https://api.github.com/authorizations', auth=("invalid", "password"))
    dump_response(response,'invalid.response')

def normal_response(session):
    import getpass
    print('Enter a GitHub username/password combo that\'s secured by 2FA')
    username = raw_input("Please enter your username: ")
    password = getpass.getpass("Please enter your password: ")
    
    response = session.get('https://api.github.com/authorizations', auth=(username, password))
    dump_response(response,'manually_entered.response')

def otp_login(session):
    import getpass
    
    print('Enter a GitHub username/password combo that\'s secured by 2FA')
    username = raw_input("Please enter your username: ")
    password = getpass.getpass("Please enter your password: ")
    
    response = session.get('https://api.github.com/authorizations', auth=(username, password))
    dump_response(response,'twofactor.response')


if __name__ == '__main__':
    import sys
    sys.exit(0)
