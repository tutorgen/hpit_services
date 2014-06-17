import sure
import pytest
import httpretty
import requests
from unittest.mock import *

from client import Plugin
from client.settings import HPIT_URL_ROOT

from plugins import ExamplePlugin


test_subject = None

def setup_function(function):
    """ setup any state tied to the execution of the given method in a
    class.  setup_method is invoked for every test method of a class.
    """
    global test_subject
    
    httpretty.enable()
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/connect/test_name",
                            body='{"entity_name":"example_plugin","entity_id":"4"}',
                            )
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/test_name/subscribe/transaction",
                            body='',
                            )
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/test_name/subscribe/test",
                            body='',
                            )
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/test_name/subscribe/example",
                            body='',
                            )
    
    test_subject = ExamplePlugin("test_name",None)

def teardown_function(function):
    """ teardown any state that was previously setup with a setup_method
    call.
    """
    httpretty.disable()
    httpretty.reset()


def test_constructor():
    """
    ExamplePlugin.__init__() Test Plan:
        -ensure logger is set to param
        -ensure that callbacks are set
    """
    test_subject.name.should.equal("test_name")
    test_subject.logger.should.equal(None)
    test_subject.callbacks["test"].should.equal(test_subject.test_plugin_callback)
    test_subject.callbacks["example"].should.equal(test_subject.example_plugin_callback)

def test_plugin_callback():
    """
    ExamplePlugin.test_plugin_callback() Test plan:
        -Mock logger, ensure written to when called
    """
    test_message = "This is a message"
    calls = [call("TEST"),call(test_message)]
    
    mock=MagicMock()
    test_subject.logger = mock
    
    test_subject.test_plugin_callback(test_message)
    
    mock.debug.assert_has_calls(calls)


def example_plugin_callback():
    """
    ExamplePlugin.example_plugin_callback() Test plan:
        -Mock logger, ensure written to when called
    """
    test_message = "This is a message"
    calls = [call("EXAMPLE"),call(test_message)]
    
    mock=MagicMock()
    test_subject.logger = mock
    
    test_subject.test_plugin_callback(test_message)
    
    mock.debug.assert_has_calls(calls)
