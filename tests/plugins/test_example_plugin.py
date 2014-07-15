import httpretty
from unittest.mock import *

from hpitclient.settings import HpitClientSettings

HPIT_URL_ROOT = HpitClientSettings.settings().HPIT_URL_ROOT

from plugins import ExamplePlugin


test_subject = None

def setup_function(function):
    """ setup any state tied to the execution of the given method in a
    class.  setup_method is invoked for every test method of a class.
    """
    global test_subject
    
    httpretty.enable()
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/connect",
                            body='{"entity_name":"example_plugin","entity_id":"4"}',
                            )
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/subscribe",
                            body='',
                            )
    
    test_subject = ExamplePlugin(1234,5678,5)

def teardown_function(function):
    """ teardown any state that was previously setup with a setup_method
    call.
    """
    global test_subject
    
    httpretty.disable()
    httpretty.reset()
    test_subject = None

def test_constructor():
    """
    ExamplePlugin.__init__() Test Plan:
        -ensure logger is set to param
        -ensure that callbacks are set
    """
    test_subject.logger.should.equal(5)


def test_post_connect():
    """
    ExamplePlugin.post_connect() Test plan:
        -ensure callbacks are set for test and example
    """
    test_subject.post_connect()
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
