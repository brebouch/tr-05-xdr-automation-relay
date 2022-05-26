import base64
import api.rest as rest
import requests


class SecureX:

    headers = {}

    def get_token(self, i, s):
        url = 'https://visibility.amp.cisco.com/iroh/oauth2/token'
        b64 = base64.b64encode((i + ':' + s).encode()).decode()
        header = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': 'Basic ' + b64
        }
        payload = 'grant_type=client_credentials'
        response = rest.post(url, header, payload)
        if response:
            return response['access_token']

    def get_module_types(self):
        url = 'https://visibility.amp.cisco.com/iroh/iroh-int/module-type/'
        return rest.get(url, self.headers)


    def delete_module_type(self, mod):
        url = 'https://visibility.amp.cisco.com/iroh/iroh-int/module-type/' + mod
        return rest.delete(url, self.headers)
    
    def get_module_type(self, mod):
        url = 'https://visibility.amp.cisco.com/iroh/iroh-int/module-type/' + mod
        return rest.get(url, self.headers)

    def update_module_type(self, mod_id, mod):
        url = 'https://visibility.amp.cisco.com/iroh/iroh-int/module-type/' + mod_id
        return rest.patch(url, headers=self.headers, body=mod)
    
    def create_module_type(self, mod):
        url = 'https://visibility.amp.cisco.com/iroh/iroh-int/module-type/'
        return rest.post(url, headers=self.headers, body=mod)

    def create_module_instance(self, mod):
        url = 'https://visibility.amp.cisco.com/iroh/iroh-int/module-instance/'
        return rest.post(url, headers=self.headers, body=mod)

    def update_module_instance(self, mod_id, mod):
        url = 'https://visibility.amp.cisco.com/iroh/iroh-int/module-instance/' + mod_id
        return rest.patch(url, headers=self.headers, body=mod)
    
    def get_module_instance(self, mod_id):
        url = 'https://visibility.amp.cisco.com/iroh/iroh-int/module-instance/' + mod_id
        return rest.get(url, headers=self.headers)

    def get_module_instances(self):
        url = 'https://visibility.amp.cisco.com/iroh/iroh-int/module-instance/'
        return rest.get(url, headers=self.headers)
    
    def encode_img(self, url):
        item = requests.get(url)
        encoded = base64.b64encode(item.content).decode('utf8')
        return 'data:image/png;base64,' + encoded

    def get_headers(self):
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.token
        }

    def __init__(self, client_id, client_secret):
        self.token = self.get_token(client_id, client_secret)
        self.get_headers()


if __name__ == '__main__':
    import sys
    sec = SecureX(sys.argv[1], sys.argv[2])
    print('hi')