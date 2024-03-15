import json
from datetime import datetime, timedelta


class LineChart:

    def set_time(self, offset):
        return {
            'start_time': str(datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")),
            'end_time': str((datetime.now() + timedelta(hours=offset)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"))

        }

    def get_tile_model(self):
        return {
            'valid_time': self.set_time(1),
            'observed_time': self.set_time(1),
            'cache_scope': 'org',
            'data': []
        }

    def generate_tile(self, data, scale):
        self.mod = self.get_tile_model()
        self.mod.update({
            'default_scale': scale,
            'data': data
        })


class DonutChart:
    mod = {}
    data = []
    labels = [[], []]
    tile_data = []

    def set_time(self, offset):
        return {
            'start_time': str(datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")),
            'end_time': str((datetime.now() + timedelta(hours=offset)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"))

        }

    def label_lookup(self, label, outer=True):
        if outer:
            index = 0
        else:
            index = 1
        for l in range(len(self.labels[index])):
            if label == self.labels[index][l]:
                return l
        return None

    def get_tile_model(self):
        return {
            'valid_time': self.set_time(1),
            'observed_time': self.set_time(1),
            'cache_scope': 'org',
            'data': []
        }

    def create_tile(self):
        for d in self.data:
            outer_lookup = self.label_lookup(d['outer_ring_title'])
            if outer_lookup is None:
                self.labels[0].append(d['outer_ring_title'])
                outer_lookup = len(self.labels[0]) - 1
                self.tile_data.append({'key': outer_lookup, 'value': 0, 'segments': []})
            self.tile_data[outer_lookup]['value'] += d['value']
            inner_lookup = self.label_lookup(d['inner_ring_title'], False)
            if inner_lookup is None:
                self.labels[1].append(d['inner_ring_title'])
                inner_lookup = len(self.labels[1]) - 1
            segment = {'key': inner_lookup, 'value': d['value']}
            self.tile_data[outer_lookup]['segments'].append(segment)

    def generate_tile(self, data, inner_label, outer_label):
        self.mod = self.get_tile_model()
        self.data = data
        self.create_tile()
        self.mod.update({
            'data': self.tile_data,
            'labels': self.labels,
            'label_headers': [
                outer_label,
                inner_label
            ]
        })


class MarkdownTile:

    def set_time(self, offset):
        return {
            'start_time': str(datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")),
            'end_time': str((datetime.now() + timedelta(hours=offset)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"))

        }

    def get_tile_model(self):
        return {
            'valid_time': self.set_time(1),
            'observed_time': self.set_time(1),
            'cache_scope': 'org',
            'data': []
        }

    def generate_tile(self, data):
        self.mod = self.get_tile_model()
        self.mod['data'] = data


icon_types = [
    'device-type',
    'bulleted-list',
    'label-group',
    'static-nat',
    'information',
    'warning',
    'critical-stop',
    'object',
    'vpn',
    'user',
    'view-metadata',
    'umbrella',
    'block'
]


class MetricTile:

    def set_time(self, offset):
        return {
            'start_time': str(datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")),
            'end_time': str((datetime.now() + timedelta(hours=offset)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"))

        }

    def get_tile_model(self):
        return {
            'valid_time': self.set_time(1),
            'observed_time': self.set_time(1),
            'cache_scope': 'org',
            'data': []
        }

    def set_metric_tile_data(self, label, icon, link, value):
        if icon not in icon_types:
            icon = 'device-type'
        self.mod['data'].append({
            'value': value,
            'value-unit': 'integer',
            'icon': icon,
            'link_uri': link,
            'label': label
        })

    def generate_tile(self, metric_tile):
        self.mod = self.get_tile_model()
        for m in metric_tile:
            self.set_metric_tile_data(m['title'], m['icon'], m['link'], m['metric_value'])


class BarChart:

    def set_time(self, offset):
        return {
            'start_time': str(datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")),
            'end_time': str((datetime.now() + timedelta(hours=offset)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"))

        }

    def get_tile_model(self):
        return {
            'valid_time': self.set_time(1),
            'observed_time': self.set_time(1),
            'cache_scope': 'org',
            'data': []
        }

    def create_values(self, item):
        response = {'key': item['key'], 'value': item['value']}
        if 'link_uri' in item.keys():
            if item['link_uri'] != '':
                response.update({'link_uri': item['link_uri']})
        if 'tooltip' in item.keys():
            if item['tooltip'] != '':
                response.update({'tooltip': item['tooltip']})
        try:
            observe = json.loads(item['observables'])
            response.update({'observables': observe})
        except:
            pass
        return response

    def generate_tile(self, key_type, data, color_scale, x_unit):
        seen_keys = []
        keys = []
        labels = []
        items = []
        for d in data:
            values = self.create_values(d)
            if d['key'] not in seen_keys:
                seen_keys.append(d['key'])
                keys.append({
                    'key': d['key'],
                    'label': d['key'].capitalize()
                })
            if d['label'] not in labels:
                labels.append(d['label'])
                items.append({
                    'key': d['label'],
                    'label': d['label'].capitalize(),
                    'value': d['value'],
                    'values': [values]
                })
            else:
                for i in items:
                    if i['key'] == d['label']:
                        i['value'] += d['value']
                        i['values'].append(values)

        self.mod = self.get_tile_model()
        self.mod.update({
            'key_type': key_type,
            'keys': seen_keys,
            'data': items
        })
        if color_scale != 'Default':
            self.mod.update({'color_scale': color_scale})
        if x_unit != 'Default':
            self.mod.update({'x_unit': x_unit})
