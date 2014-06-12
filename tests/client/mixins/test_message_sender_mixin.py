import sure
import httpretty
import json
import pytest

from client.mixins import RequestsMixin
from client.mixins import MessageSenderMixin
from client.exceptions import InvalidMessageNameException

@httpretty.activate
def test_send():
    """
    MessageSenderMixin._send() Test plan:
        -ensure events named transaction raise error
        -ensure callback is set on success
        -ensure that a response is received
    """
    
    test_payload = {"item":"shoe"}
    def test_callback():
        print("test callback")
    
    httpretty.register_uri(httpretty.POST,"http://localhost/message",
                            body='{"message_id":"4"}',
                            )
    
    subject = MessageSenderMixin()
    
    with pytest.raises(InvalidMessageNameException):
        subject.send("transaction",test_payload,None)
    
    subject.send("test_event",test_payload,test_callback)
    subject.response_callbacks["4"].should.equal("test_callback")
    
    
def test_send_transaction():
    """
    MessageSenderMixin._send_transaction() Test plan:
        -ensure callback is set on success
        -ensure that a response is received
    """
    pass

def test_poll_responses():
    """
    MessageSenderMixin._poll_responses() Test plan:
        -Ensure False returned if pre_poll_responses hook returns false
        -Ensure False returned if post_poll_responses hook returns false
        -Ensure a collection of responses returned on success
    """
    pass
    
def test_dispatch_responses():
    """
    MessageSenderMixin._dispatch_responses() Test plan:
        -Ensure False returned if pre_dispatch_responses hook returns false
        -Ensure False returned if post_dispatch_responses hook returns false
        -Catch invalid response from hpit on [message][id]
        -Catch invaled response from hpit on [response]
        -Catch no callback exception
        -Catch not callable error
        -Ensure true returned on completions
     """
    pass