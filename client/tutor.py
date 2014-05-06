from urllib.parse import urljoin

from .mixins import TransactionSenderMixin
from .settings import HPIT_URL_ROOT
from .exceptions import ResponseDispatchError

class Tutor(TransactionSenderMixin):
    def __init__(self, name, callback, **kwargs):
        super().__init__()

        self.name = name
        self.callback = callback
        self.connected = False

        for k, v in kwargs.items():
            setattr(self, k, v)

    def start(self):
        """
        Starts the tutor in event-driven mode.
        """
        try:
            while True:
                if not self.callback():
                    break;

                if not self._try_hook('pre_poll_responses'):
                    break;

                responses = self._poll_responses()

                if not self._try_hook('post_poll_responses'):
                    break;

                try:
                    if not self._dispatch_responses(responses):
                        break;
                except ResponseDispatchError as e:
                    print(str(e))

        except KeyboardInterrupt:
            self.disconnect()

    def connect(self):
        connection = self._post_data(urljoin(HPIT_URL_ROOT, '/tutor/connect/' + self.name))
        if connection:
            self.connected = True
        else:
            self.connected = False

        return self.connected

    def disconnect(self):
        self._post_data(urljoin(HPIT_URL_ROOT, '/tutor/disconnect'))
        self.connected = False

        return self.connected
