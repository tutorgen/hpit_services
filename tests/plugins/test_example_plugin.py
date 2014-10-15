import responses
import unittest
from urllib.parse import urljoin
from mock import *

from hpitclient.settings import HpitClientSettings

HPIT_URL_ROOT = HpitClientSettings.settings().HPIT_URL_ROOT

from plugins import ExamplePlugin


class TestExamplePlugin(unittest.TestCase):

    def setUp(self):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.test_subject = ExamplePlugin(1234,5678,5)

    def tearDown(self):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        self.test_subject = None

    def test_constructor(self):
        """
        ExamplePlugin.__init__() Test Plan:
            -ensure logger is set to param
            -ensure that callbacks are set
        """
        self.test_subject.logger.should.equal(5)


    @responses.activate
    def test_post_connect(self):
        """
        ExamplePlugin.post_connect() Test plan:
            -ensure callbacks are set for test and example
        """
        responses.add(responses.POST, urljoin(HPIT_URL_ROOT, '/plugin/subscribe'), body='OK')
        self.test_subject.post_connect()
        self.test_subject.callbacks["test"].should.equal(self.test_subject.test_plugin_callback)
        self.test_subject.callbacks["example"].should.equal(self.test_subject.example_plugin_callback)

    def test_plugin_callback(self):
        """
        ExamplePlugin.test_plugin_callback() Test plan:
            -Mock logger, ensure written to when called
        """
        test_message = "This is a message"
        calls = [call("TEST"),call(test_message)]
        
        self.test_subject.send_log_entry=MagicMock()
        
        self.test_subject.test_plugin_callback(test_message)
        
        self.test_subject.send_log_entry.assert_has_calls(calls)


    def example_plugin_callback(self):
        """
        ExamplePlugin.example_plugin_callback() Test plan:
            -Mock logger, ensure written to when called
        """
        test_message = "This is a message"
        calls = [call("EXAMPLE"),call(test_message)]
        
        self.test_subject.send_log_entry=MagicMock()
        
        self.test_subject.test_plugin_callback(test_message)
        
        self.test_subject.send_log_entry.assert_has_calls(calls)
