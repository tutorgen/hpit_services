import sure
import responses
import unittest
from mock import *

from pymongo import MongoClient
from pymongo import Collection

from plugins import SkillManagementPlugin

class TestSkillManagementPlugin(unittest.TestCase):

    def setUp(self):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.test_subject = SkillManagementPlugin(123,456,None)
        self.test_subject.db = self.test_subject.mongo.test_hpit.hpit_skills
       
    def tearDown(self):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        c = Collection()
        c.drop_database("test_hpit")
        
        self.test_subject = None


    def test_constructor(self):
        """
        SkillManagementPlugin.__init__() Test plan:
            -ensure name, logger set as parameters
            -ensure that mongo is an instance of mongo client
            -ensure that a cache db is set up
        """
        test_subject = SkillManagementPlugin(123,456,None)
        test_subject.logger.should.equal(None)
        
        isinstance(


    def test_get_skill_name_callback(self):
        """
        SkillManagementPlugin.get_skill_name_callback() Test plan:
            - pass in message without id, should respond with error
            - pass in message with bogus id, should respond with error
            - pass in message with good id, should respond with name
        """
        pass
    
    def test_get_skill_id_callback(self):
        """
        SkillManagementPlugin.get_skill_id_callback() Test plan:
            - pass in message without name, should respond with error
            - pass in message with name for non existent, should create one
            - pass in message with existing name, should return proper id
        """
        pass
        
