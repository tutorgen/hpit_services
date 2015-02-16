import unittest
from mock import *
from pymongo import MongoClient
from pymongo.collection import Collection
from bson.objectid import ObjectId

import shlex
import json

from hpit.plugins import BoredomDetectorPlugin
from hpit.plugins import BoredomParameterException

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
    
    def test_simple_boredom_calculation(self):
        """
        BoredomDetectorPlugin._simple_boredom_calculation() Test plan:
            - without student_id, should throw param exception
            - try without record, should be initted
            - add records, check if bored set to false on non- outlier, true on high outlier
            - add records, check if bored set to false on non- outlier, true on low outlier
        """
        #invalid args
        time = datetime(2014,12,15,9,59)
        timestring = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
        msg =  {"message_id":"1","orig_sender_id":"2","time_created":timestring,"sender_entity_id":"999"}
        self.test_subject._simple_boredom_calculation.when.called_with(msg).should.throw(BoredomParameterException)
        
        #first go, no records
        msg = {"message_id":"1","student_id":"123","orig_sender_id":"2","time_created":timestring,"sender_entity_id":"999"}
        self.test_subject._simple_boredom_calculation(msg).should.equal(0.0)
        self.test_subject.db.find_one({
            "student_id":"123",
            "time": time,
        }).should_not.equal(None)
    
        #add some values, make sure still false
        for xx in range(0,5):
            time += timedelta(0,1)
            timestring = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
            
            msg["time_created"] = timestring
            self.test_subject._simple_boredom_calculation(msg).should.equal(0.0)
            
        #trip with a high value
        time += timedelta(0,5)
        timestring = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
        msg["time_created"]=timestring
        self.test_subject._simple_boredom_calculation(msg).should.equal(1.0)
        
        #reset, same thing but trip with low value
        self.test_subject.db.remove({})
        for xx in range(0,5):
            time += timedelta(0,5)
            timestring = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
            
            msg["time_created"] = timestring
            self.test_subject._simple_boredom_calculation(msg).should.equal(0.0)
        
        time += timedelta(0,1)
        timestring = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
        msg["time_created"] = timestring
        self.test_subject._simple_boredom_calculation(msg).should.equal(1.0)
    
    def test_complex_boredom_calculation(self):
        """
        BoredomDetectorPlugin._complex_boredom_calculation() Test plan:
            - make sure it returns 1, in the short term
        """
        msg={}
        self.test_subject._complex_boredom_calculation(msg).should.equal(1.0)
    
    def test_update_boredom_callback(self):
        """
        BoredomDetectorPlugin.update_boredom_callback() Test plan:
            - set bogus return_type, should send error response
            - mock boredom_calculation, throw BoredomParameterException, should return error
            - don't set return_type
                - mock boredom_calculation to return .7, threshold at .5, should return True
                - mock boredom_calculation to return .3, threshold at .5, should return False
                - mock boredom_calculation to return .5, threshold at .5, should return True
            - set return_type to "decimal"
                -mock boredom calculation to return .7, should return .7
        """
        time = datetime(2014,12,15,9,59)
        timestring = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        #setting bogus return_type
        msg = {"message_id":"1","student_id":"123","orig_sender_id":"2","time_created":timestring,"sender_entity_id":"999","return_type":"bogus"}
        self.test_subject.update_boredom_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error":"update_boredom 'return_type' must be 'bool' or 'decimal'",
        })
        self.test_subject.send_response.reset_mock()
        
        #mock boredom_calculation to throw exception
        del msg["return_type"]
        self.test_subject.boredom_calculation = MagicMock(side_effect = BoredomParameterException("Simple boredom model requires a 'student_id'"))
        self.test_subject.update_boredom_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error":"Simple boredom model requires a 'student_id'",
        })
        self.test_subject.send_response.reset_mock()
        
        #return type bool, boredom .7, threshold .5
        self.test_subject.threshold = 0.5
        self.test_subject.boredom_calculation = MagicMock(return_value=0.7)
        self.test_subject.update_boredom_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "bored":True,
        })
        self.test_subject.send_response.reset_mock()
        
        #return type bool, boredom .3, threshold .5
        self.test_subject.threshold = 0.5
        self.test_subject.boredom_calculation = MagicMock(return_value=0.3)
        self.test_subject.update_boredom_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "bored":False,
        })
        self.test_subject.send_response.reset_mock()
        
        #return type bool, boredom .5, threshold .5
        self.test_subject.threshold = 0.5
        self.test_subject.boredom_calculation = MagicMock(return_value=0.5)
        self.test_subject.update_boredom_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "bored":True,
        })
        self.test_subject.send_response.reset_mock()
        
        msg["return_type"] = "decimal"
        self.test_subject.update_boredom_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "bored":0.5,
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
        
        
    def test_set_boredom_threshold(self):
        """
        BoredomDetectorPlugin.set_boredom_threshold() Test plan:
            - send without threshold, should return with error
            - send with threshold below 0, should respond error
            - send with threshold above 1, should respond error
            - otherwise, response should be sent and threshold set
        """
        msg = {"message_id":"1","sender_entity_id":"888"}
        self.test_subject.set_boredom_threshold(msg)
        self.test_subject.send_response.assert_called_with("1",{
              "error":"set_boredom_threshold requires a 'threshold'",   
        })
        self.test_subject.send_response.reset_mock()
         
        msg["threshold"] = -1
        self.test_subject.set_boredom_threshold(msg)
        self.test_subject.send_response.assert_called_with("1",{
              "error":"threshold must be decimal value between 0 and 1.",   
        })
        self.test_subject.send_response.reset_mock()
         
        msg["threshold"] = 2
        self.test_subject.set_boredom_threshold(msg)
        self.test_subject.send_response.assert_called_with("1",{
             "error":"threshold must be decimal value between 0 and 1.",   
        })
        self.test_subject.send_response.reset_mock()
         
        msg["threshold"] = 1
        self.test_subject.set_boredom_threshold(msg)
        self.test_subject.send_response.assert_called_with("1",{
             "status":"OK",  
        })
        self.test_subject.send_response.reset_mock()
         
        msg["threshold"] = 0
        self.test_subject.set_boredom_threshold(msg)
        self.test_subject.send_response.assert_called_with("1",{
              "status":"OK",   
        })
        self.test_subject.send_response.reset_mock()
         
        self.test_subject.threshold.should.equal(0)
     
    def test_set_model_threshold(self):
        """
        BoredomDetectorPlugin.set_boredom_model() Test plan:
           - send without model, shoudl reply error
           - send bogus model, should reply with error
           - send valid model, ensure that status is ok and bodel was set
        """
        msg = {"message_id":"1","sender_entity_id":"888"}
        self.test_subject.set_boredom_model(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "error":"set_boredom_model requires a 'model_name'",          
        })
        self.test_subject.send_response.reset_mock()
        
        msg["model_name"] = "bogus"
        self.test_subject.set_boredom_model(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "error":"set_boredom_model unknown 'model_name'",          
        })
        self.test_subject.send_response.reset_mock()
        
        msg["model_name"] = "simple"
        self.test_subject.set_boredom_model(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "status":"OK",        
        })
        self.test_subject.send_response.reset_mock()
        
        self.test_subject.boredom_calculation.should.equal(self.test_subject._simple_boredom_calculation)
            
        
        
        
        
           
            
