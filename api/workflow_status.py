import sys
import json
import base64
import requests
import time


user = sys.argv[1]
pwd = sys.argv[2]
search_wf = sys.argv[3]


def get_securex_token(i, s):
    url = 'https://visibility.amp.cisco.com/iroh/oauth2/token'
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


def get_sxo_token(token):
    url = 'https://visibility.amp.cisco.com/iroh/ao/gen-jwt'
    header = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'text/plain'
    }
    payload = "-----------------------------65382287034206060103800739838\nContent-Disposition: form-data; name=\"request_body\"\n\n{}\n-----------------------------65382287034206060103800739838--"
    response = requests.post(url, headers=header, data=payload)
    if response.status_code == 200:
        return response.text[1:-1]


def sxo_get(path):
    url = 'https://securex-ao.us.security.cisco.com' + path
    header = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=header)
    if response.status_code == 200:
        return response.json()


def sxo_post(path, data={}):
    url = 'https://securex-ao.us.security.cisco.com' + path
    header = {
        'Authorization': 'Bearer ' + token,
    }
    if data != {}:
        data = json.dumps(data)
    response = requests.post(url, headers=header, data=data)
    return response

response = {'status': '', 'message': ''}
wf = None

token = get_sxo_token(get_securex_token(user, pwd))
workflows = sxo_get('/be-console/api/v1/workflows?is_atomic=false')
for w in workflows:
    if w['name'] == search_wf:
        wf = w
        break

if wf:
    trigger_check = sxo_get('/be-console/api/v1/workflows/' + wf['id'] + '/triggers')
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


