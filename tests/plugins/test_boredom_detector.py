import unittest
from mock import *
from pymongo import MongoClient
from pymongo.collection import Collection
from bson.objectid import ObjectId

import shlex
import json

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
        
        args = {"transaction_management":"999"}
        args_string = shlex.quote(json.dumps(args))
        
        self.test_subject = BoredomDetectorPlugin(123,456,None,args_string)
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
        
        BoredomDetectorPlugin.when.called_with(1234,5678,None).should.throw(Exception)
        
        args = {"transaction_management":"999"}
        args_string = shlex.quote(json.dumps(args))
        
        ds = BoredomDetectorPlugin(1234,5678,None,args_string)
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
        time = datetime(2014,12,15,9,59)
        timestring = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        #no args
        msg = {"message_id":"1","orig_sender_id":"2","time_created":timestring,"sender_entity_id":"999"}
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
            time += timedelta(0,1)
            timestring = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
            
            msg["time_created"] = timestring
            self.test_subject.update_boredom_callback(msg)
            self.test_subject.send_response.assert_called_with("1",{
                "bored":False      
            })
        
        time += timedelta(0,5)
        timestring = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
        msg["time_created"]=timestring
        self.test_subject.update_boredom_callback(msg)  
        self.test_subject.send_response.assert_called_with("1",{
            "bored":True      
        })
        self.test_subject.send_response.reset_mock()
        
        #add some values, get bored set to true because of unusually low value
        self.test_subject.db.remove({})
        for xx in range(0,5):
            time += timedelta(0,5)
            timestring = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
            
            msg["time_created"] = timestring
            self.test_subject.update_boredom_callback(msg)
            self.test_subject.send_response.assert_called_with("1",{
                "bored":False      
            })
        
        time += timedelta(0,1)
        timestring = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
        msg["time_created"] = timestring
        self.test_subject.update_boredom_callback(msg)  
        self.test_subject.send_response.assert_called_with("1",{
            "bored":True      
        })
        self.test_subject.send_response.reset_mock()
         
    def test_transaction_callback_method(self):
        """
        BoredomDetectorPlugin.transaction_callback_method() Test plan:
            - this method is identical to update_boredom_callback, so no testing.
            - revisit when code is refactored
        """
        time = datetime(2014,12,15,9,59)
        timestring = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
        msg = {"message_id":"1","orig_sender_id":"2","time_created":timestring,"sender_entity_id":"888"}
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
                    "error" : "Access denied",
                    "responder":"boredom",
            })
        
        
        
            
        
        
        
        
           
            
