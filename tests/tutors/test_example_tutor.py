import sure
import unittest
import responses
from mock import *

import logging
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

        logger_calls = [call("Sending a random event: test"),call("RECV: {'message_id': '4'}")]
        self.test_subject.send_log_entry = MagicMock()
        self.test_subject.send = MagicMock(return_value={"message_id":"4"})
        random.choice = MagicMock(return_value="test")
        
        self.test_subject.main_callback().should.equal(True)
        self.test_subject.send_log_entry.assert_has_calls(logger_calls)
        self.test_subject.run_once = True
        self.test_subject.main_callback().should.equal(False)
