import sure
import httpretty
import json
import pytest

from client.mixins import MessageSenderMixin
from client.exceptions import InvalidMessageNameException
from client.exceptions import ResponseDispatchError
from client.settings import HPIT_URL_ROOT

def send_callback():
    print("test callback")

@httpretty.activate
def test_send():
    """
    MessageSenderMixin._send() Test plan:
        -ensure events named transaction raise error
        -ensure callback is set on success
        -ensure that a response is received
    """
    
    test_payload = {"item":"shoe"}
    
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/message",
                            body='{"message_id":"4"}',
                            )
    
    subject = MessageSenderMixin()
    
    subject.send.when.called_with("transaction",test_payload,None).should.throw(InvalidMessageNameException)
    
    response = subject.send("test_event",test_payload,send_callback)
    subject.response_callbacks["4"].should.equal(globals()["send_callback"])
    
    response.should.equal({"message_id":"4"})
    
@httpretty.activate
def test_send_transaction():
    """
    MessageSenderMixin._send_transaction() Test plan:
        -ensure callback is set on success
        -ensure that a response is received
    """
    
    test_payload = {"item":"shoe"}
    
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/message",
                            body='{"message_id":"4"}',
                            )
    
    subject = MessageSenderMixin()
    
    response = subject.send("test_event",test_payload,send_callback)
    subject.response_callbacks["4"].should.equal(globals()["send_callback"])
    
    response.should.equal({"message_id":"4"})
    
@httpretty.activate
def test_poll_responses():
    """
    MessageSenderMixin._poll_responses() Test plan:
        -Ensure False returned if pre_poll_responses hook returns false
        -Ensure False returned if post_poll_responses hook returns false
        -Ensure a collection of responses returned on success
    """
    
    httpretty.register_uri(httpretty.GET,HPIT_URL_ROOT+"/response/list",
                            body='{"responses":"4"}',
                            )
    
    
    def returnFalse():
        return False
    def returnTrue():
        return True
    
    test_message_sender_mixin = MessageSenderMixin()
    
    setattr(test_message_sender_mixin,"pre_poll_responses",returnFalse)
    setattr(test_message_sender_mixin,"post_poll_responses",returnTrue)
    test_message_sender_mixin._poll_responses().should.equal(False)
    
    setattr(test_message_sender_mixin,"pre_poll_responses",returnTrue)
    setattr(test_message_sender_mixin,"post_poll_responses",returnFalse)
    test_message_sender_mixin._poll_responses().should.equal(False)
    
    setattr(test_message_sender_mixin,"pre_poll_responses",returnTrue)
    setattr(test_message_sender_mixin,"post_poll_responses",returnTrue)
    test_message_sender_mixin._poll_responses().should.equal("4")

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
    bad_response = [{"bad_response": "boo"}]
    bad_response2 = [{"message":{"id":"4"}}]
    good_response = [{"message": {"id":"4"},"response":"2"}]

    
    def returnFalse():
        return False
    def returnTrue():
        return True
    def callback1(payload):
        return True
    
    test_message_sender_mixin = MessageSenderMixin()
    
    test_message_sender_mixin.response_callbacks["4"] = callback1
    setattr(test_message_sender_mixin,"pre_dispatch_responses",returnFalse)
    setattr(test_message_sender_mixin,"post_dispatch_responses",returnTrue)
    test_message_sender_mixin._dispatch_responses(good_response).should.equal(False)
    
    setattr(test_message_sender_mixin,"pre_dispatch_responses",returnTrue)
    setattr(test_message_sender_mixin,"post_dispatch_responses",returnFalse)
    test_message_sender_mixin._dispatch_responses(good_response).should.equal(False)
    
    setattr(test_message_sender_mixin,"pre_dispatch_responses",returnTrue)
    setattr(test_message_sender_mixin,"post_dispatch_responses",returnTrue)
    
    test_message_sender_mixin._dispatch_responses.when.called_with(bad_response).should.throw(ResponseDispatchError)
    test_message_sender_mixin._dispatch_responses.when.called_with(bad_response2).should.throw(ResponseDispatchError)
    
    del test_message_sender_mixin.response_callbacks["4"]
    test_message_sender_mixin._dispatch_responses.when.called_with(good_response).should.throw(ResponseDispatchError)
    test_message_sender_mixin.response_callbacks["4"] = 5
    test_message_sender_mixin._dispatch_responses.when.called_with(good_response).should.throw(ResponseDispatchError)
    
    test_message_sender_mixin.response_callbacks["4"] = callback1
    test_message_sender_mixin._dispatch_responses(good_response).should.equal(True)
    
    

