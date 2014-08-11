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
