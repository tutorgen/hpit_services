import sure
import unittest
import responses
from mock import *

import logging
<<<<<<< HEAD
=======
from hpitclient.settings import HpitClientSettings

from environment.settings_manager import SettingsManager
settings = SettingsManager.get_plugin_settings()
HPIT_URL_ROOT = settings.HPIT_URL_ROOT
>>>>>>> message lockdown and resource auth
import random

from hpit.tutors import ExampleTutor

class TestExampleTutor(unittest.TestCase):

    def setUp(self):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.test_subject = ExampleTutor(1234,5678,None)

    def tearDown(self):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        self.test_subject = None


    def test_constructor(self):
        """
        ExampleTutor.__init__() Test plan:
            -Ensure event_names,run_once, logger set correctly
        """
        
        self.test_subject.logger.should.equal(None)
        self.test_subject.event_names.should.equal([
                'tutorgen.test', 'tutorgen.example', 'tutorgen.add_student', 
                'tutorgen.remove_student', 'tutorgen.trace'])
        self.test_subject.run_once.should.equal(None)

    def test_setup(self):
        """
        ExampleTutor.setup() Test plan:
            -nothing here to test
        """
        pass

    def test_shutdown(self):
        """
        ExampleTutor.shutdown() Test plan:
            -nothing here to test
        """
        pass

    @responses.activate
    def test_main_callback(self):
        """
        ExampleTutor.main_callback() Test plan:
            -mock logger, ensure being written to
            -ensure that response is received on send
            -ensure that the response is logged
            -if run_once is false, returns false
            -if run_once is true, returns true
        """
<<<<<<< HEAD

=======
        """
        responses.add(responses.POST,HPIT_URL_ROOT+"/connect",
                                body='{"entity_name":"example_tutor","entity_id":"4"}',
                                )
        
        responses.add(responses.POST,HPIT_URL_ROOT+"/disconnect",
                                body='OK',
                                )
        responses.add(responses.POST,HPIT_URL_ROOT+"/message",
                                body='{"message_id":"4"}',
                                )
        
        logger_mock = MagicMock()
>>>>>>> message lockdown and resource auth
        logger_calls = [call("Sending a random event: test"),call("RECV: {'message_id': '4'}")]
        self.test_subject.send_log_entry = MagicMock()
        self.test_subject.send = MagicMock(return_value={"message_id":"4"})
        random.choice = MagicMock(return_value="test")
        
        self.test_subject.main_callback().should.equal(True)
        self.test_subject.send_log_entry.assert_has_calls(logger_calls)
        self.test_subject.run_once = True
        self.test_subject.main_callback().should.equal(False)
        """
        
