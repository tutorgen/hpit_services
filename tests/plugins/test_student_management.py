import httpretty
import unittest
from unittest.mock import *

from hpitclient.settings import HpitClientSettings

HPIT_URL_ROOT = HpitClientSettings.settings().HPIT_URL_ROOT
from plugins import StudentManagementPlugin

class TestStudentManagementPlugin(unittest.TestCase):

    def setUp(self):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.test_subject = StudentManagementPlugin(123,456,None)
        
        httpretty.enable()
        httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/connect/test_name",
                                body='{"entity_name":"skill_management_plugin","entity_id":"4"}',
                                )

        httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/subscribe/",
                                body='',
                                )
        
       
    def tearDown(self):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        httpretty.disable()
        httpretty.reset()
        self.test_subject = None


    def test_constructor(self):
        """
        StudentManagementPlugin.__init__() Test plan:
            -ensure name, logger set as parameters
            -ensure that mongo is an instance of mongo client
        """
        self.test_subject.logger.should.equal(None)
        

    def test_add_student_callback(self):
        """
        StudentManagementPlugin.add_student_callback() Test plan:
            -Mock logger, ensure written to when called
        """
        test_message = "This is a message"
        calls = [call("ADD_STUDENT"),call(test_message)]
        mock=MagicMock()
        self.test_subject.logger = mock
        self.test_subject.add_student_callback(test_message)
        mock.debug.assert_has_calls(calls)
       

    def test_remove_student_callback(self):
        """
        StudentManagementPlugin.remove_student_callback() Test plan:
            -Mock logger, ensure written to when called
        """
        test_message = "This is a message"
        calls = [call("REMOVE_STUDENT"),call(test_message)]
        mock=MagicMock()
        self.test_subject.logger = mock
        self.test_subject.remove_student_callback(test_message)
        mock.debug.assert_has_calls(calls)

     
    def test_get_student_callback(self):
        """
        StudentManagementPlugin.get_skill_callback() Test plan:
            -Mock logger, ensure written to when called
        """
        test_message = "This is a message"
        calls = [call("GET_STUDENT"),call(test_message)]
        mock=MagicMock()
        self.test_subject.logger = mock
        self.test_subject.get_student_callback(test_message)
        mock.debug.assert_has_calls(calls)
