import json

import requests


def get(url, headers={}):
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    else:
        return None


def post(url, headers={}, body={}):
    if isinstance(body, dict):
        body = json.dumps(body)
    resp = requests.post(url, headers=headers, data=body)
    if resp.status_code == 200:
        return resp.json()
    else:
        return None


def put(url, headers={}, body={}):
    resp = requests.put(url, headers=headers, data=json.dumps(body))
    if resp.status_code == 200:
        return resp.content
    else:
        return None


def patch(url, headers={}, body={}):
    resp = requests.patch(url, headers=headers, data=json.dumps(body))
    if resp.status_code == 200:
        return resp.content
    else:
        return None


def delete(url, headers={}):
    resp = requests.delete(url, headers=headers)
    if resp.status_code == 200:
        return resp.content
    else:
        return None
