import unittest
from mock import *
from pymongo import MongoClient
from pymongo.collection import Collection
from bson.objectid import ObjectId

from hpit.plugins import BoredomDetectorPlugin

from hpit.management.settings_manager import SettingsManager
settings = SettingsManager.get_plugin_settings()

from datetime import datetime
from datetime import timedelta

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
            - add records, check if bored set to false on non- outlier, true on high outlier
            - add records, check if bored set to false on non- outlier, true on high outlier
            ** this test also tests update_moredom_callback
        """
        time = datetime.now()
        time = datetime(2014,12,15,9,59)
        
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
            "time": time,
        }).should_not.equal(None)
        
        
        #add some values, get bored set to true because of unusually high value
        for xx in range(0,5):
            msg["time_created"] += timedelta(0,1)
            self.test_subject.update_boredom_callback(msg)
            self.test_subject.send_response.assert_called_with("1",{
                "bored":False      
            })
           
        msg["time_created"]+= timedelta(0,5)
        self.test_subject.update_boredom_callback(msg)  
        self.test_subject.send_response.assert_called_with("1",{
            "bored":True      
        })
        self.test_subject.send_response.reset_mock()
        
        #add some values, get bored set to true because of unusually low value
        self.test_subject.db.remove({})
        for xx in range(0,5):
            msg["time_created"] += timedelta(0,5)
            self.test_subject.update_boredom_callback(msg)
            self.test_subject.send_response.assert_called_with("1",{
                "bored":False      
            })
            
        msg["time_created"]+= timedelta(0,1)
        self.test_subject.update_boredom_callback(msg)  
        self.test_subject.send_response.assert_called_with("1",{
            "bored":True      
        })
        self.test_subject.send_response.reset_mock()
         
    def test_transaction_callback_method(self):
        """
        BoredomDetectorPlugin.transaction_callback_method() Test plan:
            - try without student_id, bored_message should be set
            - mock boredom_calculation to return false, should show in response 
            - mock boredom_calculation to return true, should show in response
        """
        def mock_send(message_name,payload,callback):
            callback({"responder":["downstream"]})
            
        self.test_subject.send_response = MagicMock()
        self.test_subject.boredom_calculation = MagicMock(return_value=False)
        self.test_subject.send = MagicMock(side_effect=mock_send)
        
        time = datetime.now()
        msg = {"message_id":"1","sender_entity_id":"2","time_created":time}
        
        #no student
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "bored":False,
            "boredom_detector_message":"error: boredom detector requires a 'student_id'",
            "responder":["boredom_detector","downstream"]
        })
        self.test_subject.send_response.reset_mock()
        
        #student here
        msg["student_id"] = "123"
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "bored":False,
            "boredom_detector_message":"",
            "responder":["boredom_detector","downstream"]
        })
        self.test_subject.send_response.reset_mock()
        
        
        #boredom_calculation returns true
        self.test_subject.boredom_calculation = MagicMock(return_value=True)
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "bored":True,
            "boredom_detector_message":"",
            "responder":["boredom_detector","downstream"]
        })
        self.test_subject.send_response.reset_mock()
        
        
            
        
        
        
        
           
            
