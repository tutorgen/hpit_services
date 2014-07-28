import sure
import responses
import unittest
from unittest.mock import *

from hpitclient.settings import HpitClientSettings

HPIT_URL_ROOT = HpitClientSettings.settings().HPIT_URL_ROOT

from plugins import SkillManagementPlugin

class TestSkillManagementPlugin(unittest.TestCase):

    def setUp(self):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.test_subject = SkillManagementPlugin(123,456,None)
       
    def tearDown(self):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        self.test_subject = None


    def test_constructor(self):
        """
        SkillManagementPlugin.__init__() Test plan:
            -ensure name, logger set as parameters
            -ensure that mongo is an instance of mongo client
        """
        self.test_subject.logger.should.equal(None)


    def test_add_skill_callback(self):
        """
        SkillManagementPlugin.add_skill_callback() Test plan:
            -Mock logger, ensure written to when called
        """
        test_message = "This is a message"
        calls = [call("ADD_SKILL"),call(test_message)]
        mock=MagicMock()
        self.test_subject.logger = mock
        self.test_subject.add_skill_callback(test_message)
        mock.debug.assert_has_calls(calls)
       

    def test_remove_skill_callback(self):
        """
        SkillManagementPlugin.remove_skill_callback() Test plan:
            -Mock logger, ensure written to when called
        """
        test_message = "This is a message"
        calls = [call("REMOVE_SKILL"),call(test_message)]
        mock=MagicMock()
        self.test_subject.logger = mock
        self.test_subject.remove_skill_callback(test_message)
        mock.debug.assert_has_calls(calls)

     
    def test_get_skill_callback(self):
        """
        SkillManagementPlugin.get_skill_callback() Test plan:
            -Mock logger, ensure written to when called
        """
        test_message = "This is a message"
        calls = [call("GET_SKILL"),call(test_message)]
        mock=MagicMock()
        self.test_subject.logger = mock
        self.test_subject.get_skill_callback(test_message)
        mock.debug.assert_has_calls(calls)
