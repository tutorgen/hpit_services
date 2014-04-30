#This contains the standard function with which to interact with HPIT
import os
import time
import json
import requests
from urllib.parse import urljoin
from settings import *
JSON_HTTP_HEADERS = {'content-type': 'application/json'}

class ConnectionError(Exception):
    pass

class PluginRegistrationError(Exception):
    pass

class PluginPollError(Exception):
    pass

class RequestsMixin:
    def _post_data(self, url, data=None):
        if data:
            response = requests.post(url, data=json.dumps(data), headers=JSON_HTTP_HEADERS)
        else:
            response = requests.post(url)

        if response.status_code != 200:
            raise ConnectionError("Could not POST Data to HPIT Server.")

        return response

    def _get_data(self, url):
        response = requests.get(url)

        if response.status_code != 200:
            raise ConnectionError("Could not GET Data from HPIT Server.")

        return response.json()


class TransactionSenderMixin(RequestsMixin):
    def send(self, event_name, payload):
        transaction_url = urljoin(HPIT_URL_ROOT, 'transaction')

        return self._post_data(transaction_url, {
            'name': event_name,
            'payload': payload
        })

class Plugin(TransactionSenderMixin):
    def __init__(self, name, wildcard_callback=None):
        self.name = name
        self.wildcard_callback = wildcard_callback
        self.callbacks = {}
        self.poll_wait = 5
        self.pre_poll = None
        self.post_poll = None
        self.pre_dispatch = None
        self.post_dispatch = None
        self.connected = False

    def connect(self):
        connection = self._post_data(urljoin(HPIT_URL_ROOT, '/plugin/connect/' + self.name))

        if connection:
            self.connected = True
        else:
            self.connected = False

        return self.connected

    def disconnect(self):
        self._post_data(urljoin(HPIT_URL_ROOT, '/plugin/disconnect/' + self.name))
        self.connected = False

        return self.connected

    def list_subscriptions(self):
        list_url = urljoin(HPIT_URL_ROOT, '/plugin/' + self.name + '/subscriptions')
        subscriptions = requests.get(list_url).json()['subscriptions']

        for sub in subscriptions:
            if sub not in self.callbacks:
                self.callbacks[sub] = None

        return self.callbacks

    def subscribe(self, **events):
        """
        Subscribe to events, each argument is exepcted as a key value pair where
        the key is the event's name and the value is the callback function.
        """
        for event_name, callback in events.items():
            subscribe_url = urljoin(HPIT_URL_ROOT, 
                '/plugin/' + self.name + '/subscribe/' + event_name)

            self._post_data(subscribe_url)
            self.callbacks[event_name] = callback

    def unsubscribe(self, *event_names):
        """
        Unsubscribe from events. Pass each event name as a separate parameter.
        """
        for event_name in event_names:
            if event_name in self.callbacks:
                unsubscribe_url = urljoin(HPIT_URL_ROOT, 
                    'plugin', self.name, 'unsubscribe', event_name)

                self._post_data(unsubscribe_url)
                del self.callbacks[event_name]

    def _poll(self):
        """
        Get a list of new transactions from the server for events we are listening 
        to.
        """
        list_transactions_url = urljoin(HPIT_URL_ROOT, 
            '/plugin/' + self.name + '/transactions')

        return self._get_data(list_transactions_url)['transactions']

    def _try_hook(self, hook_name):
        """
        Try's to call a signal hook. Hooks take in no parameters and return a boolean result.
        True will cause the plugin to continue execution.
        False will cause the plugon to stop execution.
        """
        hook = getattr(self, hook_name, None)

        if hook:
            return hook()
        else:
            return True

    def _dispatch(self, event_data):
        """
        For each transaction recieved route it to the appropriate callback.
        """
        if not self._try_hook('pre_dispatch'):
            return False

        for event_item in event_data:
            event = event_item['event_name']
            payload = event_item['transaction']
            
            try:
                self.callbacks[event](payload)
            except KeyError:
                #No callback registered try the wildcard
                if self.wildcard_callback:
                    try:
                        self.wildcard_callback(payload)
                    except TypeError:
                        raise PluginPollError("Wildcard Callback is not a callable")
            except TypeError:
                #Callback isn't a function
                if self.callbacks[event] is None:
                    raise PluginPollError("No callback registered for event: <" + event + ">")
                else:
                    raise PluginPollError("Registered callback for event: <" + event + "> is not a callable")

        if not self._try_hook('post_dispatch'):
            return False

        return True

    def start(self):
        """
        Start the plugin. Connect to the HPIT server. Then being polling and dispatching
        event callbacks based on transactions we subscribe to.
        """
        self.connect()
        self.list_subscriptions()

        try:
            continue_execution = True

            while continue_execution:
                if not self._try_hook('pre_poll'):
                    return False

                event_data = self._poll()

                if not self._try_hook('post_poll'):
                    return False

                continue_execution = self._dispatch(event_data)
                time.sleep(self.poll_wait)

        except KeyboardInterrupt:
            self.disconnect()

        self.disconnect()

class Tutor(TransactionSenderMixin):
    def __init__(self, name, callback, **kwargs):
        self.name = name
        self.callback = callback
        self.connected = False

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

    def connect(self):
        connection = self._post_data(urljoin(HPIT_URL_ROOT, '/tutor/connect/' + self.name))
        if connection:
            self.connected = True
        else:
            self.connected = False

        return self.connected

    def disconnect(self):
        self._post_data(urljoin(HPIT_URL_ROOT, '/tutor/disconnect/' + self.name))
        self.connected = False

        return self.connected

