#This contains the standard function with which to interact with HPIT
import json
import requests
from urllib.parse import urljoin
from settings import *

class Plugin:
    def register(plugin_name):
        pass

    def unregister(plugin_name):
        pass

    def subscribe(event_name):
        pass

    def unsubscribe(event_name):
        pass

class Tutor:
    def register(plugin_name):
        pass

    def unregister(plugin_name):
        pass
        
    def send_transaction(event_name, payload):
        tutor_url = urljoin(HPIT_URL_ROOT, 'transaction')
        headers = {'content-type': 'application/json'}
        data = {
            'name': event_name,
            'payload': payload
        }
        return request.post(tutor_url, data=json.dumps(data), headers=headers)
