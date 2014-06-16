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
    
    test_subject = ExampleTutor("test_name",None)

def teardown_function(function):
    """ teardown any state that was previously setup with a setup_method
    call.
    """
    pass


def test_constructor():
    """
    ExampleTutor.__init__() Test plan:
    """
    pass

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
    pass
