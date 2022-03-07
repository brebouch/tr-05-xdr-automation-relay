import json

import requests
import base64
import sys

class SXO:
    sxo_url = 'https://securex-ao.us.security.cisco.com/be-console/api/v1'
    token = ''

    def get_securex_token(self, i, s):
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

    def get_sxo_token(self, token):
        url = 'https://visibility.amp.cisco.com/iroh/ao/gen-jwt'
        header = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'text/plain'
        }
        payload = "-----------------------------65382287034206060103800739838\nContent-Disposition: form-data; name=\"request_body\"\n\n{}\n-----------------------------65382287034206060103800739838--"
        response = requests.post(url, headers=header, data=payload)
        if response.status_code ==200:
            return response.text[1:-1]

    def sxo_get(self, path):
        url = self.sxo_url + path
        header = {
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=header)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            self.refresh_token()
            self.sxo_get(path)

    def sxo_post(self, path, data):
        url = self.sxo_url + path
        header = {
            'Authorization': 'Bearer ' + self.token,
        }
        response = requests.post(url, headers=header, files=dict(request_body=json.dumps(data)))
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            self.refresh_token()
            self.sxo_post(path, data)

    def get_instance(self, instance_id):
        complete = False
        while not complete:
            instance = self.sxo_get('/instances/' + instance_id)
            if instance is None:
                return
            if instance['status']['state'] != 'running' and instance['status']['state'] != 'created':
                return instance

    def get_action(self, instance_id, action_id):
        return self.sxo_get('/instances/' + instance_id + '/actions/' + action_id)

    def run_workflow(self, workflow_id, workflow_inputs=None):
        if workflow_inputs is None:
            data = {}
        else:
            data = workflow_inputs
        run = self.sxo_post('.1/workflows/ui/start?workflow_id=' + workflow_id, data)
        return self.get_instance(run[0]['id'])

    def get_all_workflows(self):
        return self.sxo_get('/workflows?is_atomic=false')

    def get_workflows_config(self, workflow_name):
        workflows = self.get_all_workflows()
        for w in workflows:
            if w['name'] == workflow_name:
                return w

    def get_workflow(self, workflow_name):
        workflow = self.get_workflows_config(workflow_name)
        start_config = self.sxo_get('/workflows/start_config?workflow_id=' + workflow['id'])
        return {'workflow': workflow, 'start_config': start_config}
    
    def get_deliberation(self, observable_type, observable_value):
        wf = self.get_workflow(self.deliberate_name)
        data = {}
        try:
            for i in range(len(wf['start_config']['input_variables'])):
                if wf['start_config']['input_variables'][i]['properties']['name'] == 'observable_type':
                    data.update({wf['start_config']['input_variables'][i]['id']: observable_type})
                if wf['start_config']['input_variables'][i]['properties']['name'] == 'observable_value':
                    data.update({wf['start_config']['input_variables'][i]['id']: observable_value})
            instance = self.run_workflow(wf['workflow']['id'], data)
            for inst in instance['variables']:
                if inst['properties']['name'] == self.deliberate_variable:
                    return inst['properties']['value']
        except Exception as e:
            return

    def get_observation(self, observable_type, observable_value):
        wf = self.get_workflow(self.observe_name)
        data = {}
        try:
            for i in range(len(wf['start_config']['input_variables'])):
                if wf['start_config']['input_variables'][i]['properties']['name'] == 'observable_type':
                    data.update({wf['start_config']['input_variables'][i]['id']: observable_type})
                if wf['start_config']['input_variables'][i]['properties']['name'] == 'observable_value':
                    data.update({wf['start_config']['input_variables'][i]['id']: observable_value})
            instance = self.run_workflow(wf['workflow']['id'], data)
            for inst in instance['variables']:
                if inst['properties']['name'] == self.observe_variable:
                    return inst['properties']['value']
        except Exception as e:
            return

    def get_variables(self):
        return self.sxo_get('/variables/')

    def get_variable_by_id(self, variable_id):
        return self.sxo_get('/variables/' + variable_id)

    def get_table(self, table_id, offset=0, rows=100):
        return self.sxo_get('/tables/' + table_id +
                            '?table_id=' + table_id +
                            '&offset=' + str(offset) +
                            '&rows=' + str(rows))

    def get_variable(self, variable_name):
        variables = self.get_variables()
        for v in variables:
            try:
                if v['properties']['name'] == variable_name:
                    if v['properties']['type'] == 'datatype.table':
                        return self.get_table(self.get_variable_by_id(v['id'])['table_id'])
                    else:
                        return v
            except Exception as e:
                continue

    def get_tile_modules(self):
        tiles = []
        tile_table = self.get_variable('SXO Relay Dashboard Tiles')
        for t in tile_table['rows']:
            try:
                tile = [t['column_data']['title'], t['column_data']['dashboard_type'],
                        t['column_data']['tags'].split(','), t['column_data']['description'],
                        t['column_data']['short_description'], t['column_data']['workflow_name']]
                periods = []
                if t['column_data']['last_hour']:
                    periods.append('last_hour')
                if t['column_data']['last_24_hours']:
                    periods.append('last_24_hours')
                if t['column_data']['last_7_days']:
                    periods.append('last_7_days')
                if t['column_data']['last_30_days']:
                    periods.append('last_30_days')
                if t['column_data']['last_90_days']:
                    periods.append('last_90_days')
                tile.append(periods)
                tile.append(t['column_data']['default_period'])
                tiles.append(tile)
            except:
                continue
        return tiles


    def get_tile_workflow_name(self, tile_type):
        if tile_type == 'metric_group':
            return 'SXO Relay Create Metric Tile'
        elif tile_type == 'markdown':
            return 'SXO Relay Create Markdown Tile'
        elif  'bar_chart' in tile_type:
            return 'SXO Relay Create Bar Chart Tile'
        elif 'line_chart' in tile_type:
            return 'SXO Relay Create Line Chart Tile'
        elif 'donut_graph' in tile_type:
            return 'SXO Relay Create Donut Tile'

    def run_tile_workflow(self, workflow_name, tile_type):
        tile_workflow_name = self.get_tile_workflow_name(tile_type)
        workflow = self.get_workflow(workflow_name)
        instance = self.run_workflow(workflow['workflow']['id'], {})
        if 'actions' not in instance.keys():
            print(str(instance))
        for a in instance['actions']:
            if a['title'] == tile_workflow_name:
                tile_instance = self.get_action(instance['id'], a['id'])
                if tile_type:
                    for resp in tile_instance['output']['response'].values():
                        try:
                            return json.loads(resp)
                        except Exception as e:
                            continue

    def refresh_token(self):
        self.token = self.get_sxo_token(self.get_securex_token(self.client_id, self.client_secret))

    def __init__(self, auth):
        self.client_id = auth['API_CLIENT']
        self.client_secret = auth['API_SECRET']
        self.deliberate_name = auth['DELIBERATE_WORKFLOW']
        self.deliberate_variable = auth['DELIBERATE_VARIABLE']
        self.observe_name = auth['OBSERVE_WORKFLOW']
        self.observe_variable = auth['OBSERVE_VARIABLE']
        self.refresh_token()
        #with open('api/ao_api.json', 'r') as json_file:
        #    self.ao_spec = json.load(json_file)


if __name__ == '__main__':
    auth = {
        'API_CLIENT': sys.argv[1],
        'API_SECRET': sys.argv[2],
        'DELIBERATE_WORKFLOW': '',
        'DELIBERATE_VARIABLE': '',
        'OBSERVE_WORKFLOW': '',
        'OBSERVE_VARIABLE': ''
    }
    s = SXO(auth)
    t = s.get_table("01UELOH0J8GII45MWhzUVz9Xufwd4YIUIQo")
    wf = s.get_workflow('SXO Relay Update Tile Data')
    modules = s.get_tile_modules()
    for m in modules:
        t = s.run_tile_workflow(m[5], m[1])
    #variables = sxo_get('/variables/01U656A3KBBKW2XXdkVXgLIF29bRDF0aF4C', sxo_token)
    #wf = sxo_get('/workflows/start_config?workflow_id=01U61ZH5071EG7GSRgott0DkcQzW4nGamXC', sxo_token)
    data = {}
    #for i in range(len(wf['start_config']['input_variables'])):
    #    data.update({wf['start_config']['input_variables'][i]['id']: 'Test: ' + str(i)})
    instance = s.run_workflow(wf['workflow']['id'], data)
    #w = sxo_post('.1/workflows/ui/start?workflow_id=01U61ZH5071EG7GSRgott0DkcQzW4nGamXC', sxo_token, json.dumps(data))
    #instance = sxo_get('/instances/01UDQ1BIY5R5K5SLabTz41vAynSYF8LNqHK', sxo_token)
    print('hi')