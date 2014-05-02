from urllib.parse import urljoin

from .requests_mixin import RequestsMixin
from exceptions import ResponseDispatchError
from settings import HPIT_URL_ROOT

class TransactionSenderMixin(RequestsMixin):
    def __init__(self):
        super().__init__()
        self.response_callbacks = []
        self.pre_poll_responses = None
        self.post_poll_responses = None
        self.pre_dispatch_responses = None
        self.post_dispatch_responses = None

    def send(self, event_name, payload, callback=None):
        transaction_url = urljoin(HPIT_URL_ROOT, 'transaction')

        response = self._post_data(transaction_url, {
            'name': event_name,
            'payload': payload
        }).json()

        if callback:
            self.response_callbacks[response['transaction_id']] = callback

        return response


    def _poll_responses(self):
        response_list_url = urljoin(HPIT_URL_ROOT, 'responses')

        if not self._try_hook('pre_poll_responses'):
            return False

        responses = self._get_data(response_list_url)['responses']

        if not self._try_hook('post_poll_responses'):
            return False

        return responses


    def _dispatch_responses(self, responses):

        if not self._try_hook('pre_dispatch_responses'):
            return False

        for res in responses:
            try:
                transaction_id = res['transaction']['id']
            except KeyError:
                raise ResponseDispatchError('Invalid response from HPIT. No transaction id supplied in response.')

            try:
                response_payload = res['response']
            except KeyError:
                raise ResponseDispatchError('Invalid response from HPIT. No response payload supplied.')

            try:
                self.response_callbacks[transaction_id](response_payload)
            except KeyError:
                raise ResponseDispatchError('No callback registered for transaction id: ' + transaction_id)
            except TypeError:
                raise ResponseDispatchError("Callback registered for transcation id: " + transaction_id + " is not a callable.")

        if not self._try_hook('post_dispatch_responses'):
            return False

        return True
