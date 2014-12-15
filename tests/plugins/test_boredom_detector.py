import unittest
from mock import *
from pymongo import MongoClient
from pymongo.collection import Collection
from bson.objectid import ObjectId

from hpit.plugins import BoredomDetectorPlugin

from hpit.management.settings_manager import SettingsManager
settings = SettingsManager.get_plugin_settings()

from datetime import datetime

class TestBoredomDetectorPlugin(unittest.TestCase):

    def setUp(self):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.test_subject = BoredomDetectorPlugin(123,456,None)
        self.test_subject.send_response = MagicMock()
        
    def tearDown(self):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        client = MongoClient()
        client.drop_database(settings.MONGO_DBNAME)
        
        self.test_subject = None
        
    def test_constructor(self):
        """
        BoredomDetectorPlugin.__init__() Test plan:
            - make sure logger set right
            - make sure self.mongo is a mongo client
            - make sure db is a collection
            -check full name
        """
        ds = BoredomDetectorPlugin(1234,5678,None)
        ds.logger.should.equal(None)
        isinstance(ds.mongo,MongoClient).should.equal(True)
        isinstance(ds.db,Collection).should.equal(True)
        ds.db.full_name.should.equal("hpit_unit_test_db.hpit_boredom_detection")
        
    def test_update_boredom_callback(self):
        """
        BoredomDetectorPlugin.update_boredom_callback() Test plan:
            - try without student_id, should return error
            - try without record, should be initted
            - try with a record, should be updated.
            - fake update total records, check if bored set to false on non- outlier
            - enter a largely variant time, should set bored to true.
        """
        time = datetime.now()
        
        #no args
        msg = {"message_id":"1","sender_entity_id":"2","time_created":time}
        self.test_subject.update_boredom_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "error":"update_boredom requires a 'student_id'",      
        })
        self.test_subject.send_response.reset_mock()
        
        #first try, no record
        msg["student_id"] = "123"
        self.test_subject.update_boredom_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "bored":False      
        })
        self.test_subject.send_response.reset_mock()
        
        self.test_subject.db.find_one({
            "student_id":"123",
            "last_reported_time": time,
            "average_time_difference": 0,
            "sum_of_variance": 0,
            "total_reports":0,
        }).should_not.equal(None)
        
        #second try, should change
        msg["time_created"] = time.replace(microsecond=time.microsecond + 10)
        import nose;nose.tools.set_trace()
        self.test_subject.update_boredom_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "bored":False   
        })
        self.test_subject.send_response.reset_mock()
        
        self.test_subject.db.find_one({
            "student_id":"123",
            "last_reported_time": msg["time_created"],
            "average_time_difference": 10,
            "sum_of_variance": 0,
            "total_reports":1,
        }).should_not.equal(None)
        self.test_subject.db.find({"student_id":"123"}).count.should.equal(1)
        
        #add some values, get bored set to true
        for xx in range(0,self.test_subject.RECORD_THRESHOLD):
            msg["time_created"] = time.replace(microsecond=time.microsecond + ((xx+2)*10))
            self.test_subject.update_boredom_callback(msg)
           
        msg["time_created"].replace(microsecond=time.microsecond + 2000)
        self.test_subject.update_boredom_callback(msg)  
        self.test_subject.send_response.assert_called_with("1",{
            "bored":True      
        })
        self.test_subject.send_response.reset_mock()
         
        
        
        
        
           
            
