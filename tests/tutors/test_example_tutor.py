import sure
import pytest
import httpretty
import requests
from unittest.mock import *

from client import Tutor
from client.settings import HPIT_URL_ROOT

from tutors import ExampleTutor

test_subject = None


def setup_function(function):
    """ setup any state tied to the execution of the given method in a
    class.  setup_method is invoked for every test method of a class.
    """
    global test_subject
    
    test_subject = ExampleTutor("test_name",None)
    
    httpretty.enable()
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/tutor/connect/test_name",
                            body='{"entity_name":"example_tutor","entity_id":"4"}',
                            )
    
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/tutor/disconnect",
                            body='OK',
                            )


def teardown_function(function):
    """ teardown any state that was previously setup with a setup_method
    call.
    """
    pass


def test_constructor():
    """
    ExampleTutor.__init__() Test plan:
        -Ensure name, logger set correctly
        -Ensure event_names set correctly
    """
    
    test_subject.name.should.equal("test_name")
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
    pass

def test_run():
    """
    ExampleTutor.run() Test plan:
        -mock start, ensured called
        -ensure starts disconnected, finishes connected
    """
    mock = MagicMock()
    test_subject.start = mock
    test_subject.run()
    test_subject.start.assert_any_call()
    
    
    
