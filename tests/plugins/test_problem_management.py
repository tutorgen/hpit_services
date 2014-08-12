import unittest
from mock import *
from pymongo import MongoClient
from pymongo.collection import Collection
from bson.objectid import ObjectId

from plugins import ProblemManagementPlugin

class TestProblemManagementPlugin(unittest.TestCase):

    def setUp(self):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.test_subject = ProblemManagementPlugin(123,456,None)
        self.test_subject.db = self.test_subject.mongo.test_hpit.hpit_problems
        
    def tearDown(self):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        client = MongoClient()
        client.drop_database("test_hpit")
        
        self.test_subject = None
        
    def test_add_problem_callback(self):
        """
        ProblemManagementPlugin.add_problem_callback() Test plan:
            - 
        """
        
    def test_remove_problem_callback(self):
        """
        ProblemManagementPlugin.remove_problem_callback() Test plan:
            -
        """
       
    def test_get_problem_callback(self):
        """
        ProblemManagementPlugin.get_problem_callback() Test plan:
            -
        """
        
    def test_edit_problem_callback(self):
        """
        ProblemManagementPlugin.edit_problem_callback() Test plan:
            -
        """
        
    def test_list_problems_callback(self):
        """
        ProblemManagementPlugin.list_problems_callback() Test plan:
            -
        """
        
    def test_clone_problem_callback(self):
        """
        ProblemManagementPlugin.clone_problem_callback() Test plan:
            -
        """
        
    def test_add_step_callback(self):
        """
        ProblemManagementPlugin.add_step_callback() Test plan:
            -
        """
        
    def test_remove_step_callback(self):
        """
        ProblemManagmentPlugin.remove_step_callback() Test plan:
            -
        """
        
    def test_get_step_callback(self):
        """
        ProblemManagementPlugin.get_step_callback() Test plan:
            -
        """
        
    def test_get_problem_steps_callback(self):
        """
        ProblemManagementPlugin.get_problem_steps_callback() Test plan:
            -
        """
    
        
