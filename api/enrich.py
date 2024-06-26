from functools import partial
from flask import Blueprint, current_app, request
import json

import api.utils
from api.schemas import ObservableSchema
from api.utils import get_json, get_jwt, jsonify_data, format_docs
from api.xdr_automate import XdrAutomate
from uuid import uuid4

enrich_api = Blueprint('enrich', __name__)

get_observables = partial(get_json, schema=ObservableSchema(many=True))


def get_disposition(status):
    if status.lower() == 'malicious':
        return current_app.config['DISPOSITIONS']['malicious']
    elif status.lower() == 'suspicious':
        return current_app.config['DISPOSITIONS']['suspicious']
    elif status.lower() == 'clean':
        return current_app.config['DISPOSITIONS']['clean']
    elif status.lower() == 'common':
        return current_app.config['DISPOSITIONS']['common']
    else:
        return current_app.config['DISPOSITIONS']['unknown']


def get_verdict(observable_value, observable_type, disposition, valid_time):
    '''
        Format the observable disposition into the CTIM format
    '''
    if disposition[0] == 1:
        disposition_name = 'Clean'
    elif disposition[0] == 2:
        disposition_name = 'Malicious'
    elif disposition[0] == 3:
        disposition_name = 'Suspicious'
    elif disposition[0] == 4:
        disposition_name = 'Common'
    elif disposition[0] == 5:
        disposition_name = 'Unknown'
    else:
        disposition_name = 'Unknown'
    return {
        'type': 'verdict',
        'observable': {'type': observable_type, 'value': observable_value},
        'disposition': disposition[0],
        'disposition_name': disposition_name,
        'valid_time': valid_time
    }


def get_judgement(observable_value, observable_type, disposition, valid_time):
    # Prepare Judgement reply
    source_uri = 'https://xdr.us.security.cisco.com/automate'

    return {
        'id': f'transient:judgement-{uuid4()}',
        'observable': {'value': observable_value, 'type': observable_type},
        'disposition': disposition[0],
        'disposition_name': disposition[1],
        'type': 'judgement',
        'schema_version': '1.0.1',
        'source': 'Cisco XDR Automate Relay',
        'confidence': 'Low',
        'priority': 90,
        'severity': 'Medium',
        'valid_time': valid_time,
        'source_uri': source_uri
    }


def set_observable(ip):
    return {
                "value": ip,
                "type": "ip"
            }


def set_relation(src, dst, relation):
    return {
        "origin": "Cisco XDR Automate Relay",
        "relation": relation,
        "source": {
            "value": src,
            "type": "ip"
        },
        "related": {
            "value": dst,
            "type": "ip"
        }
    }


def get_doc():
    return {
        "description": "Cisco XDR Automate Relay Doc",
        "schema_version": "1.1.3",
        "relations": [
        ],
        "observables": [
        ],
        "type": "sighting",
        "source": "Cisco XDR Automate",
        "targets": [
        ],
        "resolution": "detected",
        "internal": True,
        "count": 1,
        "id": '',
        "severity": "Unknown",
        "tlp": "white",
        "confidence": "High",
        "observed_time": {
            "start_time": "2021-04-19T03:01:27.000Z",
            "end_time": "2021-04-19T03:01:27.000Z"
        },
        "sensor": "network.sensor"
    }


def set_doc(s):
    doc = get_doc()
    doc['count'] = 1
    doc['id'] = "transient:" + s['agentName']
    times = api.utils.set_time(1)
    doc['observed_time']['start_time'] = times['start_time']
    doc['observed_time']['end_time'] = times['end_time']
    return doc


def get_model():
    return {
            "sightings": {
                "count": 0,
                "docs": [
                ]
            }
        }


def group_observables(relay_input):
    # Leave only unique observables ( deduplicate observable )  and select some specific observable type
    result = []
    for observable in relay_input:
        o_value = observable['value']
        o_type = observable['type'].lower()

        # Get only supported types by this third party
        if o_type in current_app.config['CCT_OBSERVABLE_TYPES']:
            obj = {'type': o_type, 'value': o_value}
            if obj in result:
                continue
            result.append(obj)
    return result


@enrich_api.route('/deliberate/observables', methods=['POST'])
def deliberate_observables():
    auth = get_jwt()
    automate = XdrAutomate(auth)
    response = {'verdicts': {}, 'judgements': {}}
    ob = group_observables(get_observables())
    valid_time = api.utils.set_time(1)
    for o in ob:
        try:
            disposition = get_disposition(automate.get_deliberation(o['type'], o['value']))
            if disposition:
                response['verdicts'].append(get_verdict(o['value'], o['type'], disposition, valid_time))
                response['judgements'].append(get_judgement(o['value'], o['type'], disposition, valid_time))
        except Exception as e:
            print(e)
            continue
    if not response['verdicts'] and not response['judgements']:
        return jsonify_data({})
    if response['verdicts']:
        response['verdicts'] = format_docs(response['verdicts'])
    if response['verdicts']:
        response['judgements'] = format_docs(response['judgements'])
    return jsonify_data(response)


@enrich_api.route('/observe/observables', methods=['POST'])
def observe_observables():
    r = request
    response = get_model()
    auth = get_jwt()
    automate = XdrAutomate(auth)
    ob = group_observables(get_observables())
    for o in ob:
        try:
            observe = json.loads(automate.get_observation(o['type'], o['value']))
            if observe:
                response['sightings']['count'] += 1
                response['sightings']['docs'].append(observe)
        except Exception as e:
            print(e)
            continue
    return jsonify_data(response)


@enrich_api.route('/refer/observables', methods=['POST'])
def refer_observables():
    _ = get_jwt()
    _ = get_observables()
    return jsonify_data([])
