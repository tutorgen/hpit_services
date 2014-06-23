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
        Polls the HPIT server for a list of event names we currently subscribing to.
        """
        list_url = urljoin(HPIT_URL_ROOT, '/plugin/subscriptions')
        subscriptions = self._get_data(list_url)['subscriptions']

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
            subscribe_url = urljoin(HPIT_URL_ROOT, '/plugin/subscribe')

            self._post_data(subscribe_url, {'message_name' : event_name})
            self.callbacks[event_name] = callback


    def unsubscribe(self, *event_names):
        """
        Unsubscribe from events. Pass each event name as a separate parameter.
        """
        for event_name in event_names:
            if event_name in self.callbacks:
                unsubscribe_url = urljoin(HPIT_URL_ROOT, '/plugin/unsubscribe')
                self._post_data(unsubscribe_url, {'message_name': event_name})
                del self.callbacks[event_name]


    def _poll(self):
        """
        Get a list of new messages from the server for events we are listening 
        to.
        """
        list_messages_url = urljoin(HPIT_URL_ROOT, '/plugin/messages')

        return self._get_data(list_messages_url)['messages']


    def _dispatch(self, event_data):
        """
        For each message recieved route it to the appropriate callback.
        """
        if not self._try_hook('pre_dispatch'):
            return False

        for event_item in event_data:
            event = event_item['event_name']
            payload = event_item['message']
            
            try:
                self.callbacks[event](payload)
            except KeyError:
                #No callback registered try the wildcard
                if self.wildcard_callback:
                    try:
                        self.wildcard_callback(payload)
                    except TypeError:
                        raise PluginPollError("Wildcard Callback is not a callable")
            except TypeError as e:
                #Callback isn't a function
                if self.callbacks[event] is None:
                    raise PluginPollError("No callback registered for event: <" + event + ">")
                else:
                    raise e

        if not self._try_hook('post_dispatch'):
            return False

        return True


    def start(self):
        """
        Start the plugin. Connect to the HPIT server. Then being polling and dispatching
        event callbacks based on messages we subscribe to.
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

                event_data = self._poll()

                if not self._try_hook('post_poll'):
                    break;

                if not self._dispatch(event_data):
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
        Sends a response to HPIT upon handling a specific event.

        Responses are handled differently than normal messages as they are destined
        for a only the original sender of the message_id to recieve the response.
        """
        response_url = urljoin(HPIT_URL_ROOT, 'response')

        self._post_data(response_url, {
            'message_id': message_id,
            'payload': payload
        })
