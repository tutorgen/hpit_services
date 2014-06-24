import sure
import pytest
import httpretty
import requests
from unittest.mock import *

import logging
from client import Plugin
from client.settings import HPIT_URL_ROOT
from pymongo import MongoClient

from plugins import SkillManagementPlugin

test_subject = None

def setup_function(function):
    """ setup any state tied to the execution of the given method in a
    class.  setup_method is invoked for every test method of a class.
    """
    
    """
    global test_subject
    
    
    httpretty.enable()
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/connect/test_name",
                            body='{"entity_name":"skill_management_plugin","entity_id":"4"}',
                            )
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/test_name/subscribe/transaction",
                            body='',
                            )
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/test_name/subscribe/add_skill",
                            body='',
                            )
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/test_name/subscribe/remove_skill",
                            body='',
                            )
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/test_name/subscribe/get_skill",
                            body='',
                            )
    test_subject = SkillManagementPlugin("test_name",None)
    """
    pass
def teardown_function(function):
    """ teardown any state that was previously setup with a setup_method
    call.
    """
    #global test_subject
    
    #httpretty.disable()
    #httpretty.reset()
    #test_subject = None
    pass
def test_constructor():
    """
    SkillManagementPlugin.__init__() Test plan:
        -ensure name, logger set as parameters
        -ensure callbacks are set
    """
    #test_subject.name.should.equal("test_name")
    #test_subject.logger.should.equal(None)
    #test_subject.callbacks["add_skill"].should.equal(test_subject.test_plugin_callback)
    #test_subject.callbacks["remove_skill"].should.equal(test_subject.example_plugin_callback)
    #test_subject.callbacks["get_skill"].should.equal(test_subject.test_plugin_callback)
    pass
def test_add_skill_callback():
    """
    SkillManagementPlugin.add_skill_callback() Test plan:
        -Mock logger, ensure written to when called
    """
    #test_message = "This is a message"
    #calls = [call("ADD_SKILL"),call(test_message)]
    #mock=MagicMock()
    #test_subject.logger = mock
    #test_subject.add_skill_callback(test_message)
    #mock.debug.assert_has_calls(calls)
    pass
def test_remove_skill_callback():
    """
    SkillManagementPlugin.remove_skill_callback() Test plan:
        -Mock logger, ensure written to when called
    """
    #test_message = "This is a message"
    #calls = [call("REMOVE_SKILL"),call(test_message)]
    #mock=MagicMock()
    #test_subject.logger = mock
    #test_subject.add_skill_callback(test_message)
    #mock.debug.assert_has_calls(calls)
    pass
def test_get_skill_callback():
    """
    SkillManagementPlugin.get_skill_callback() Test plan:
        -Mock logger, ensure written to when called
    """
    #test_message = "This is a message"
    #calls = [call("GET_SKILL"),call(test_message)]
    #mock=MagicMock()
    #test_subject.logger = mock
    #test_subject.add_skill_callback(test_message)
    #mock.debug.assert_has_calls(calls)
    pass
