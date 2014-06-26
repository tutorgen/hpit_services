import time
from urllib.parse import urljoin

from .mixins import MessageSenderMixin
from .settings import HPIT_URL_ROOT
from .exceptions import ResponseDispatchError

class Tutor(MessageSenderMixin):
    def __init__(self, entity_id, api_key, callback, **kwargs):
        super().__init__()

        self.entity_id = str(entity_id)
        self.api_key = str(api_key)
        self.callback = callback

        self.poll_wait = 500
        self.time_last_poll = time.time() * 1000

        for k, v in kwargs.items():
            setattr(self, k, v)

    def start(self):
        """
        Starts the tutor in event-driven mode.
        """
        self.connect()
        
        try:
            while True:
                if not self.callback():
                    break;

                #A better timer
                cur_time = time.time() * 1000

                if cur_time - self.time_last_poll < self.poll_wait:
                    continue;

                self.time_last_poll = cur_time

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
