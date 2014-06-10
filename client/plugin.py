import time
from urllib.parse import urljoin

from .mixins import MessageSenderMixin
from .settings import HPIT_URL_ROOT
from .exceptions import PluginPollError

class Plugin(MessageSenderMixin):
    def __init__(self, name, wildcard_callback=None):
        super().__init__()

        self.name = name
        self.wildcard_callback = wildcard_callback
        self.callbacks = {}
        self.poll_wait = 5
        self.pre_poll = None
        self.post_poll = None
        self.pre_dispatch = None
        self.post_dispatch = None
        self.connected = False
        
        self.subscribe(
            transaction=self.transaction_callback
        )
    
    def transaction_callback(self,message):
        """
        This is the default callback to responding to transaction messages.  This
        can be overridden if a plugin is interested in transaction messages.
        """
        pass

    def connect(self):
        """
        Register a connection with the HPIT Server.

        This essentially sets up a session and logs that you are actively using
        the system. This is mostly used to track plugin use with the site.
        """
        connection = self._post_data(urljoin(HPIT_URL_ROOT, '/plugin/connect/' + self.name))

        if connection:
            self.connected = True
        else:
            self.connected = False

        return self.connected


    def disconnect(self):
        """
        Tells the HPIT Server that you are not currently going to poll
        the server for messages or responses. This also destroys the current session
        with the HPIT server.
        """
        self._post_data(urljoin(HPIT_URL_ROOT, '/plugin/disconnect'))
        self.connected = False

        return self.connected


    def list_subscriptions(self):
        """
        Polls the HPIT server for a list of event names we currently subscribing to.
        """
        list_url = urljoin(HPIT_URL_ROOT, '/plugin/' + self.name + '/subscriptions')
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
        Get a list of new messages from the server for events we are listening 
        to.
        """
        list_messages_url = urljoin(HPIT_URL_ROOT, 
            '/plugin/' + self.name + '/messages')

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

                time.sleep(self.poll_wait)

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
