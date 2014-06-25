import sure
import pytest
import httpretty
import requests
from unittest.mock import *

import logging
from client import Tutor
from client.settings import HPIT_URL_ROOT
import random

from tutors import ExampleTutor

test_subject = None


def setup_function(function):
    """ setup any state tied to the execution of the given method in a
    class.  setup_method is invoked for every test method of a class.
    """
    global test_subject
    
    test_subject = ExampleTutor(1234,5678,None)
    
    httpretty.enable()
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/connect",
                            body='{"entity_name":"example_tutor","entity_id":"4"}',
                            )
    
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/disconnect",
                            body='OK',
                            )
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/message",
                            body='{"message_id":"4"}',
                            )


def teardown_function(function):
    """ teardown any state that was previously setup with a setup_method
    call.
    """
    global test_subject
    
    test_subject = None


def test_constructor():
    """
    ExampleTutor.__init__() Test plan:
        -Ensure event_names,run_once, logger set correctly
    """
    
    test_subject.logger.should.equal(None)
    test_subject.event_names.should.equal([
            'test', 'example', 'add_student', 
            'remove_student', 'trace'])
    test_subject.run_once.should.equal(None)

def test_setup():
    """
    ExampleTutor.setup() Test plan:
        -nothing here to test
    """
    pass

def test_shutdown():
    """
    ExampleTutor.shutdown() Test plan:
        -nothing here to test
    """
    pass

def test_main_callback():
    """
    ExampleTutor.main_callback() Test plan:
        -mock logger, ensure being written to
        -ensure that response is received on send
        -ensure that the response is logged
        -if run_once is false, returns false
        -if run_once is true, returns true
    """
    logger_mock = MagicMock()
    logger_calls = [call("Sending a random event: test"),call("RECV: {'message_id': '4'}")]
    
    logging.getLogger = MagicMock(return_value=logger_mock)
    
    random.choice = MagicMock(return_value="test")
    
    test_subject.main_callback().should.equal(True)
    
    logger_mock.debug.assert_has_calls(logger_calls)
    
    test_subject.run_once = True

    test_subject.main_callback().should.equal(False)
    
    
    

def test_run():
    """
    ExampleTutor.run() Test plan:
        -mock start, ensured called
        -ensure starts disconnected, finishes disconnected
    """
    mock = MagicMock()
    test_subject.start = mock
    test_subject.connected.should.equal(False)
    test_subject.run()
    test_subject.start.assert_any_call()
    test_subject.connected.should.equal(False)
    
    
    
