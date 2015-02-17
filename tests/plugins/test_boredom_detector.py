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
    
        isinstance(ds.config_db,Collection).should.equal(True)
        ds.config_db.full_name.should.equal("hpit_unit_test_db.hpit_boredom_config")
    
    def test_ensure_config_init(self):
        """
        BoredomDetectorPlugin.ensure_config_init() Test plan:
            - with nothing in the db, should insert defaults and return return_config
            - with only threshold in DB, should add default model
            - with only model in db, should add default threshold
            - should always return full config
        """
        
        #nothing in db
        config = self.test_subject.ensure_config_init("123","456")
        config["threshold"].should.equal(self.test_subject.DEFAULT_THRESHOLD)
        config["model_name"].should.equal(self.test_subject.DEFAULT_MODEL)
        config["student_id"].should.equal("123")
        config["entity_id"].should.equal("456")
        self.test_subject.config_db.find_one({"student_id":"123","entity_id":"456","threshold":self.test_subject.DEFAULT_THRESHOLD,"model_name":self.test_subject.DEFAULT_MODEL}).should_not.equal(None)
        
        self.test_subject.config_db.remove({})
        
        #only threshold in db
        self.test_subject.config_db.insert({"student_id":"123","entity_id":"456","threshold":.2})
        config = self.test_subject.ensure_config_init("123","456")
        config["threshold"].should.equal(.2)
        config["model_name"].should.equal(self.test_subject.DEFAULT_MODEL)
        config["student_id"].should.equal("123")
        config["entity_id"].should.equal("456")
        self.test_subject.config_db.find({"student_id":"123","entity_id":"456","threshold":.2,"model_name":self.test_subject.DEFAULT_MODEL}).count().should.equal(1)
        
        self.test_subject.config_db.remove({})
        
        #only model in db
        self.test_subject.config_db.insert({"student_id":"123","entity_id":"456","model_name":"woohoo"})
        config = self.test_subject.ensure_config_init("123","456")
        config["threshold"].should.equal(self.test_subject.DEFAULT_THRESHOLD)
        config["model_name"].should.equal("woohoo")
        config["student_id"].should.equal("123")
        config["entity_id"].should.equal("456")
        self.test_subject.config_db.find({"student_id":"123","entity_id":"456","threshold":self.test_subject.DEFAULT_THRESHOLD,"model_name":"woohoo"}).count().should.equal(1)
        
        self.test_subject.config_db.remove({})
        
        #both in db
        self.test_subject.config_db.insert({"student_id":"123","entity_id":"456","model_name":"woohoo","threshold":.2})
        config = self.test_subject.ensure_config_init("123","456")
        config["threshold"].should.equal(.2)
        config["model_name"].should.equal("woohoo")
        config["student_id"].should.equal("123")
        config["entity_id"].should.equal("456")
        self.test_subject.config_db.find({"student_id":"123","entity_id":"456","threshold":.2,"model_name":"woohoo"}).count().should.equal(1)
    

    def test_simple_boredom_calculation(self):
        """
        BoredomDetectorPlugin._simple_boredom_calculation() Test plan:
            - try without record, should be initted
            - add records, check if bored set to false on non- outlier, true on high outlier
            - add records, check if bored set to false on non- outlier, true on low outlier
        """
        time = datetime(2014,12,15,9,59)
        timestring = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
        
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
            - send without student_id, should send error response
            - mock boredom_calculation, throw BoredomParameterException, should return error.
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
        msg = {"message_id":"1","time_created":timestring,"sender_entity_id":"999","return_type":"bogus"}
        self.test_subject.update_boredom_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error":"update_boredom 'return_type' must be 'bool' or 'decimal'",
        })
        self.test_subject.send_response.reset_mock()
        
        #without student_id
        del msg["return_type"]
        self.test_subject.update_boredom_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error":"update boredom requires 'student_id'",
        })
        self.test_subject.send_response.reset_mock()
        
        #mock boredom_calculation to throw exception
        msg["student_id"] = "2"
        self.test_subject.boredom_models["simple"] = MagicMock(side_effect = BoredomParameterException("Simple boredom model requires a 'student_id'"))
        self.test_subject.update_boredom_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error":"Simple boredom model requires a 'student_id'",
        })
        self.test_subject.send_response.reset_mock()
                
        #return type bool, boredom .7, threshold .5
        self.test_subject.config_db.update({"student_id":"2"},{"$set":{"threshold":.5}})
        self.test_subject.boredom_models["simple"] = MagicMock(return_value=0.7)
        self.test_subject.update_boredom_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "bored":True,
        })
        self.test_subject.send_response.reset_mock()
        
        #return type bool, boredom .3, threshold .5
        self.test_subject.boredom_models["simple"] = MagicMock(return_value=0.3)
        self.test_subject.update_boredom_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "bored":False,
        })
        self.test_subject.send_response.reset_mock()
        
        #return type bool, boredom .5, threshold .5
        self.test_subject.boredom_models["simple"]= MagicMock(return_value=0.5)
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
               
    def test_set_boredom_threshold(self):
        """
        BoredomDetectorPlugin.set_boredom_threshold() Test plan:
            - send without threshold, should return with error
            - send with threshold below 0, should respond error
            - send with threshold above 1, should respond error
            - otherwise, response should be sent and threshold set
        """
        
        #no threshold
        msg = {"message_id":"1","sender_entity_id":"888"}
        self.test_subject.set_boredom_threshold(msg)
        self.test_subject.send_response.assert_called_with("1",{
              "error":"set_boredom_threshold requires a 'threshold' and 'student_id'",   
        })
        self.test_subject.send_response.reset_mock()
        
        #no student ID
        msg["threshold"] = -1
        self.test_subject.set_boredom_threshold(msg)
        self.test_subject.send_response.assert_called_with("1",{
              "error":"set_boredom_threshold requires a 'threshold' and 'student_id'",   
        })
        self.test_subject.send_response.reset_mock()
         
        #threshold under 0
        msg["student_id"] = "2"
        self.test_subject.set_boredom_threshold(msg)
        self.test_subject.send_response.assert_called_with("1",{
              "error":"threshold must be decimal value between 0 and 1.",   
        })
        self.test_subject.send_response.reset_mock()
        
        #threshold over 1
        msg["threshold"] = 2
        self.test_subject.set_boredom_threshold(msg)
        self.test_subject.send_response.assert_called_with("1",{
             "error":"threshold must be decimal value between 0 and 1.",   
        })
        self.test_subject.send_response.reset_mock()
        
        #threshold at 1
        msg["threshold"] = 1
        self.test_subject.set_boredom_threshold(msg)
        self.test_subject.send_response.assert_called_with("1",{
             "status":"OK",  
        })
        self.test_subject.send_response.reset_mock()
        
        #threshold at 0
        msg["threshold"] = 0
        self.test_subject.set_boredom_threshold(msg)
        self.test_subject.send_response.assert_called_with("1",{
              "status":"OK",   
        })
        self.test_subject.send_response.reset_mock()
         
        self.test_subject.config_db.find_one({"student_id":"2","entity_id":"888","threshold":0}).should_not.equal(None)
     
    def test_set_boredom_model(self):
        """
        BoredomDetectorPlugin.set_boredom_model() Test plan:
           - send without model, shoudl reply error
           - send bogus model, should reply with error
           - send valid model, ensure that status is ok and bodel was set
           - make sure db set correctly
        """
        msg = {"message_id":"1","sender_entity_id":"888"}
        self.test_subject.set_boredom_model(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "error":"set_boredom_model requires a 'model_name' and 'student_id'",          
        })
        self.test_subject.send_response.reset_mock()
        
        msg["student_id"] = "2"
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
                    
        self.test_subject.config_db.find_one({"student_id":"2","entity_id":"888","model_name":"simple"}).should_not.equal(None)
    

    def test_transaction_callback_method(self):
        """
        BoredomDetectorPlugin.transaction_callback_method() Test plan:
            - check for access denied
            - if student ID not supplied, should raise error
            - mock boredom_models["simple"] to return .5, make sure called
        """
        time = datetime(2014,12,15,9,59)
        timestring = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
        msg = {"message_id":"1","orig_sender_id":"2","time_created":timestring,"sender_entity_id":"888"}
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
                    "error" : "Access denied",
                    "responder":"boredom",
            })
        self.test_subject.send_response.reset_mock()
        
        msg["sender_entity_id"] = "999"
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error":"boredom detector requires a 'student_id'",
                "responder":"boredom"
            })
        self.test_subject.send_response.reset_mock()
        
        msg["student_id"] = "3"
        self.test_subject.boredom_models["simple"] = MagicMock(return_value=.5)
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "bored":.5,
                "threshold":.75,
                "responder":"boredom",
            })
        self.test_subject.send_response.reset_mock()
        
        
        
           
            
