import sure
import httpretty
import json
from urllib.parse import urljoin

from client.mixins import TransactionSenderMixin
from client.settings import HPIT_URL_ROOT

@httpretty.activate
def test__send():
	transaction_url = urljoin(HPIT_URL_ROOT, 'transaction')
	httpretty.register_uri(httpretty.POST, transaction_url,
                           body='{"name": "greeting", "payload": "hello"}',
                           adding_headers={'X-session-cookie': 'abcd1234'})
	subject = TransactionSenderMixin()
	#it should return event_name and payload if event_name and corresponding payload are sent
	subject.send("greeting", "hello").should.equal({"name": "greeting", "payload": "hello"})

@httpretty.activate
def test__send_transaction():
	transaction_url = urljoin(HPIT_URL_ROOT, 'transaction')
	httpretty.register_uri(httpretty.POST, transaction_url,
                           body='{"name": "transaction", "payload": "hello"}',
                           adding_headers={'X-session-cookie': 'abcd1234'})
	subject = TransactionSenderMixin()
	#it should return event_name and payload if event_name and corresponding payload are sent
	subject.send_transaction("hello").should.equal({"name": "transaction", "payload": "hello"})
	