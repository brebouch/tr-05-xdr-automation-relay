import base64
import json
import sys
import os

import requests

user = sys.argv[1]
pwd = sys.argv[2]
search_wf = sys.argv[3]
xdr_url = os.environ.get('XDR_URL')
automate_url = os.environ.get('AUTOMATE_URL')


def get_xdr_token(i, s):
    url = f'{xdr_url}/iroh/oauth2/token'
    b64 = base64.b64encode((i + ':' + s).encode()).decode()
    header = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'Authorization': 'Basic ' + b64
    }
    payload = 'grant_type=client_credentials'
    response = requests.post(url, headers=header, data=payload)
    if response.status_code == 200:
        return response.json()['access_token']


def xdr_get(path):
    url = f'{automate_url}{path}'
    header = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=header)
    if response.status_code == 200:
        return response.json()


def xdr_post(path, data={}):
    url = f'{automate_url}{path}'
    header = {
        'Authorization': 'Bearer ' + token,
    }
    if data != {}:
        data = json.dumps(data)
    response = requests.post(url, headers=header, data=data)
    return response


response = {'status': '', 'message': ''}
wf = None

token = get_xdr_token(user, pwd)
workflows = xdr_get('/workflows?is_atomic=false')
for w in workflows:
    if w['name'] == search_wf:
        wf = w
        break

if wf:
    trigger_check = xdr_get('/workflows/' + wf['id'] + '/triggers')
    if trigger_check:
        for t in trigger_check:
            if t['disabled']:
                response = {'status': 'failed', 'message': 'Trigger is currently Disabled'}
                break
            if t['status']['state'] != 'started-polling':
                response = {'status': 'failed', 'message': 'Trigger is in errored state. \nMsg: ' +
                                                           t['status']['error_msg']}
                break
else:
    response['status'] = 'failed'
    response['message'] = 'Unable to find workflow ID by provided name'

response = {'status': 'success', 'message': 'Trigger is polling as expected'}

output = json.dumps(response)

print(output)
