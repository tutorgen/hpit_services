import json
import requests

from exceptions import ConnectionError

JSON_HTTP_HEADERS = {'content-type': 'application/json'}

class RequestsMixin:
    def __init__(self):
        self.session = requests.Session()

    def _post_data(self, url, data=None):
        if data:
            response = self.session.post(url, data=json.dumps(data), headers=JSON_HTTP_HEADERS)
        else:
            response = self.session.post(url)

        if response.status_code != 200:
            raise ConnectionError("Could not POST Data to HPIT Server.")

        return response

    def _get_data(self, url):
        response = self.session.get(url)

        if response.status_code != 200:
            raise ConnectionError("Could not GET Data from HPIT Server.")

        return response.json()

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

