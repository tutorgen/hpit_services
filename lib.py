#This contains the standard function with which to interact with HPIT
import json
import requests
from urllib.parse import urljoin
from settings import *
JSON_HTTP_HEADERS = {'content-type': 'application/json'}

class TutorConnectionError(Exception):
    pass

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
    def __init__(self, name, callback, **kwargs):
        self.name = name
        self.callback = callback

        for k, v in kwargs.items():
            setattr(self, k, v)

    def start(self):
        """
        Starts the tutor in event-driven mode.
        """
        self.connect()

        try:
            continue_execution = True
            while continue_execution:
                continue_execution = self.callback(self)
        except KeyboardInterrupt:
            self.disconnect()

        self.disconnect()

    def send(self, event_name, payload):
        tutor_url = urljoin(HPIT_URL_ROOT, 'transaction')
        data = {
            'name': event_name,
            'payload': payload
        }
        return requests.post(tutor_url, data=json.dumps(data), headers=JSON_HTTP_HEADERS)

    def connect(self):
        register_url = urljoin(HPIT_URL_ROOT, '/tutor/register', self.name)
        response = requests.post(register_url, data=json.dumps({}), headers=JSON_HTTP_HEADERS)

        if response.status_code == 200 and response.text == "OK":
            raise TutorConnectionError("Could not connect to HPIT Server.")

    def disconnect(self):
        unregister_url = urljoin(HPIT_URL_ROOT, '/tutor/unregister', self.name)
        return requests.post(register_url, data=json.dumps({}), headers=JSON_HTTP_HEADERS)
