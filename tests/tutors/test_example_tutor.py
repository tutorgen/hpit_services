import sure
import unittest
import responses
from unittest.mock import *

import logging
from hpitclient.settings import HpitClientSettings

HPIT_URL_ROOT = HpitClientSettings.settings().HPIT_URL_ROOT
import random

from tutors import ExampleTutor

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
                'test', 'example', 'add_student', 
                'remove_student', 'trace'])
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
        logger_calls = [call("Sending a random event: test"),call("RECV: {'message_id': '4'}")]
        
        logging.getLogger = MagicMock(return_value=logger_mock)
        
        random.choice = MagicMock(return_value="test")
        
        self.test_subject.main_callback().should.equal(True)
        
        logger_mock.debug.assert_has_calls(logger_calls)
        
        self.test_subject.run_once = True

        self.test_subject.main_callback().should.equal(False)
