import time
from urllib.parse import urljoin

from .mixins import MessageSenderMixin
from .settings import HPIT_URL_ROOT
from .exceptions import PluginPollError, BadCallbackException

class Plugin(MessageSenderMixin):
    def __init__(self, entity_id, api_key, wildcard_callback=None):
        super().__init__()

        self.entity_id = str(entity_id)
        self.api_key = str(api_key)
        self.wildcard_callback = wildcard_callback
        self.transaction_callback = None
        self.callbacks = {}

        self.poll_wait = 500
        self.time_last_poll = time.time() * 1000

        self._add_hooks(
            'pre_poll_messages', 'post_poll_messages', 
            'pre_dispatch_messages', 'post_dispatch_messages', 
            'pre_handle_transactions', 'post_handle_transcations')


    def post_connect(self):
        pass


    def register_transaction_callback(self,callback):
        """
        Set a callback for transactions and start listening for them.
        """
        if not hasattr(callback,"__call__"):
            raise BadCallbackException("The callback submitted is not callable.")
        subscribe_url = urljoin(HPIT_URL_ROOT, '/plugin/subscribe')
        self._post_data(subscribe_url, {'message_name' : "transaction"})
        self.transaction_callback = callback
        
        
    def clear_transaction_callback(self):
        """
        Clear the callback for transactions and stop listening for them.
        """
        unsubscribe_url = urljoin(HPIT_URL_ROOT, '/plugin/unsubscribe')
        self._post_data(unsubscribe_url, {'message_name': "transaction"})
        self.transaction_callback = None
        

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

    def _handle_transactions(self):
        """
        Get a list of datashop transactions from the server. 
        """

        list_transaction_url = urljoin(HPIT_URL_ROOT, '/plugin/transaction/list')

        transaction_data = self._get_data(list_transaction_url)['transactions']

        for item in transaction_data:
            if self.transaction_callback:
                if not self.transaction_callback(item):
                    return False

        return True


    def _dispatch(self, message_data):
        """
        For each message recieved route it to the appropriate callback.
        """
        if not self._try_hook('pre_dispatch_messages'):
            return False

        for message_item in message_data:
            message = message_item['message_name']
            payload = message_item['message']

            #Inject the message_id into the payload
            payload['message_id'] = message_item['message_id']
            payload['sender_entity_id'] = message_item['sender_entity_id']

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

        if not self._try_hook('post_dispatch_messages'):
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
                if not self._try_hook('pre_poll_messages'):
                    break;

                message_data = self._poll()

                if not self._try_hook('post_poll_messages'):
                    break;

                if not self._dispatch(message_data):
                    return False

                if not self._try_hook('pre_handle_transactions'):
                    break;

                if not self._handle_transactions():
                    return False

                if not self._try_hook('post_handle_transactions'):
                    break;

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
