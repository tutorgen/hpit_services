import time
from urllib.parse import urljoin

from .mixins import MessageSenderMixin
from .settings import HPIT_URL_ROOT
from .exceptions import PluginPollError

class Plugin(MessageSenderMixin):
    def __init__(self, entity_id, api_key, wildcard_callback=None):
        super().__init__()

        self.entity_id = entity_id
        self.api_key = api_key
        self.wildcard_callback = wildcard_callback
        self.transaction_callback = lambda: 0
        self.callbacks = {}

        self.poll_wait = 500
        self.time_last_poll = time.time() * 1000

        self._add_hooks('pre_poll', 'post_poll', 'pre_dispatch', 'post_dispatch')
        self.connected = False
      
    def post_connect(self):
        """
        Run this hook after connecting to HPIT.
        """
        self.subscribe(
            transaction=self.transaction_callback
        )
    
    def register_transaction_callback(self,callback):
        """
        Set a callback for transactions.  This defaults to a pass method in the constructor.
        """
        self.transaction_callback = callback
        self.subscribe(
            transaction=self.transaction_callback
        )


    def list_subscriptions(self):
        """
        Polls the HPIT server for a list of message names we currently subscribing to.
        """
        list_url = urljoin(HPIT_URL_ROOT, '/plugin/subscription/list')
        subscriptions = self._get_data(list_url)['subscriptions']

        for sub in subscriptions:
            if sub not in self.callbacks:
                self.callbacks[sub] = None

        return self.callbacks


    def subscribe(self, **messages):
        """
        Subscribe to messages, each argument is exepcted as a key value pair where
        the key is the message's name and the value is the callback function.
        """
        for message_name, callback in messages.items():
            subscribe_url = urljoin(HPIT_URL_ROOT, '/plugin/subscribe')

            self._post_data(subscribe_url, {'message_name' : message_name})
            self.callbacks[message_name] = callback


    def unsubscribe(self, *message_names):
        """
        Unsubscribe from messages. Pass each message name as a separate parameter.
        """
        for message_name in message_names:
            if message_name in self.callbacks:
                unsubscribe_url = urljoin(HPIT_URL_ROOT, '/plugin/unsubscribe')
                self._post_data(unsubscribe_url, {'message_name': message_name})
                del self.callbacks[message_name]


    def _poll(self):
        """
        Get a list of new messages from the server for messages we are listening 
        to.
        """
        list_messages_url = urljoin(HPIT_URL_ROOT, '/plugin/message/list')

        return self._get_data(list_messages_url)['messages']


    def _dispatch(self, message_data):
        """
        For each message recieved route it to the appropriate callback.
        """
        if not self._try_hook('pre_dispatch'):
            return False

        for message_item in message_data:
            message = message_item['message_name']
            payload = message_item['message']
            
            try:
                self.callbacks[message](payload)
            except KeyError:
                #No callback registered try the wildcard
                if self.wildcard_callback:
                    try:
                        self.wildcard_callback(payload)
                    except TypeError:
                        raise PluginPollError("Wildcard Callback is not a callable")
            except TypeError as e:
                #Callback isn't a function
                if self.callbacks[message] is None:
                    raise PluginPollError("No callback registered for message: <" + message + ">")
                else:
                    raise e

        if not self._try_hook('post_dispatch'):
            return False

        return True


    def start(self):
        """
        Start the plugin. Connect to the HPIT server. Then being polling and dispatching
        message callbacks based on messages we subscribe to.
        """
        self.connect()
        self.list_subscriptions()

        try:
            while True:

                #A better timer
                cur_time = time.time() * 1000

                if cur_time - self.time_last_poll < self.poll_wait:
                    continue;

                self.time_last_poll = cur_time

                #Handle messages submitted by tutors
                if not self._try_hook('pre_poll'):
                    break;

                message_data = self._poll()

                if not self._try_hook('post_poll'):
                    break;

                if not self._dispatch(message_data):
                    return False

                #Handle responses from other plugins
                if not self._try_hook('pre_poll_responses'):
                    break;

                responses = self._poll_responses()

                if not self._try_hook('post_poll_responses'):
                    break;

                if not self._dispatch_responses(responses):
                    break;

        except KeyboardInterrupt:
            self.disconnect()

        self.disconnect()


    def send_response(self, message_id, payload):
        """
        Sends a response to HPIT upon handling a specific message.

        Responses are handled differently than normal messages as they are destined
        for a only the original sender of the message_id to recieve the response.
        """
        response_url = urljoin(HPIT_URL_ROOT, 'response')

        self._post_data(response_url, {
            'message_id': message_id,
            'payload': payload
        })
