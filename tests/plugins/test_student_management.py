import sure
import pytest
import httpretty
import requests
from unittest.mock import *

import logging
from client import Plugin
from client.settings import HPIT_URL_ROOT
from pymongo import MongoClient

from plugins import StudentManagementPlugin

test_subject = None

def setup_function(function):
    """ setup any state tied to the execution of the given method in a
    class.  setup_method is invoked for every test method of a class.
    """
    
    
    global test_subject
    
    test_subject = StudentManagementPlugin(123,456,None)
    
    httpretty.enable()
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/connect/test_name",
                            body='{"entity_name":"skill_management_plugin","entity_id":"4"}',
                            )

    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/subscribe/",
                            body='',
                            )
    
   
def teardown_function(function):
    """ teardown any state that was previously setup with a setup_method
    call.
    """
    global test_subject
    
    httpretty.disable()
    httpretty.reset()
    test_subject = None
    pass
def test_constructor():
    """
    StudentManagementPlugin.__init__() Test plan:
        -ensure name, logger set as parameters
        -ensure that mongo is an instance of mongo client
    """
    test_subject.logger.should.equal(None)
    isinstance(test_subject.mongo,MongoClient).should.equal(True)
    
    pass
def test_add_student_callback():
    """
    StudentManagementPlugin.add_student_callback() Test plan:
        -Mock logger, ensure written to when called
    """
    test_message = "This is a message"
    calls = [call("ADD_STUDENT"),call(test_message)]
    mock=MagicMock()
    test_subject.logger = mock
    test_subject.add_student_callback(test_message)
    mock.debug.assert_has_calls(calls)
    
def test_remove_student_callback():
    """
    StudentManagementPlugin.remove_student_callback() Test plan:
        -Mock logger, ensure written to when called
    """
    test_message = "This is a message"
    calls = [call("REMOVE_STUDENT"),call(test_message)]
    mock=MagicMock()
    test_subject.logger = mock
    test_subject.remove_student_callback(test_message)
    mock.debug.assert_has_calls(calls)
 
def test_get_student_callback():
    """
    StudentManagementPlugin.get_skill_callback() Test plan:
        -Mock logger, ensure written to when called
    """
    test_message = "This is a message"
    calls = [call("GET_STUDENT"),call(test_message)]
    mock=MagicMock()
    test_subject.logger = mock
    test_subject.get_student_callback(test_message)
    mock.debug.assert_has_calls(calls)
    pass
