import unittest
from mock import *
from pymongo import MongoClient
from pymongo.collection import Collection
from bson.objectid import ObjectId

from threading import Timer

from couchbase import Couchbase
import couchbase

import requests

from hpit.plugins import StudentManagementPlugin

from hpit.management.settings_manager import SettingsManager
settings = SettingsManager.get_plugin_settings()

class TestStudentManagementPlugin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        options = {
                "authType":"sasl",
                "saslPassword":"",
                "bucketType":"memcached",
                "flushEnabled":1,
                "name":"test_student_model_cache",
                "ramQuotaMB":100,
            }
        req = requests.post(settings.COUCHBASE_BUCKET_URI,auth=settings.COUCHBASE_AUTH, data = options)
        """
        
    @classmethod
    def tearDownClass(cls):
        """
        res = requests.delete(settings.COUCHBASE_BUCKET_URI + "/test_student_model_cache",auth=settings.COUCHBASE_AUTH)
        if res.status_code != 200 and res.status_code != 404:
            if '_' not in res.json() or res.json()['_'] != 'Bucket deletion not yet complete, but will continue.\r\n':
                raise Exception("Failure to delete bucket")
        """
        
    def setUp(self):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """

        self.test_subject = StudentManagementPlugin(123,456,None)
        
        #self.test_subject.cache = Couchbase.connect(bucket = "test_student_model_cache", host = settings.COUCHBASE_HOSTNAME)
        self.test_subject.logger = MagicMock()
        self.test_subject.send_log_entry = MagicMock()
        
    def tearDown(self):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
       
        client = MongoClient()
        client.drop_database(settings.MONGO_DBNAME)
        
        self.test_subject = None

    def test_constructor(self):
        """
        StudentManagementPlugin.__init__() Test plan:
            -ensure name, logger set as parameters
            -ensure that mongo is an instance of MongoClient
            -ensure that db is an instance of Collection
            -ensure that the full name is hpit.hpit_students
        """
        smp = StudentManagementPlugin(123,456,None)
        isinstance(smp.mongo,MongoClient).should.equal(True)
        isinstance(smp.db,Collection).should.equal(True)
        smp.db.full_name.should.equal("hpit_unit_test_db.hpit_students")
        
    def test_add_student_callback(self):
        """
        StudentManagementPlugin.add_student_callback() Test plan:
            -Mock logger, ensure written to when called
            -Send message without attributes, attributes should be empty in db
            -Send in attributes, should be present in database
            -Should be two distinc messages now
            -mock response, should have a call with the message id and student id
        """

        test_message = {"message_id":"2","sender_entity_id":"3"}
        calls = [call("ADD_STUDENT"),call(test_message)]
        self.test_subject.send_response = MagicMock()
        self.test_subject._post_data = MagicMock(return_value=requests.Response())
        requests.Response.json = MagicMock(return_value={"resource_id":"456"})
        
        self.test_subject.add_student_callback(test_message)
        self.test_subject.send_log_entry.assert_has_calls(calls)
        
        client = MongoClient()
        result = client[settings.MONGO_DBNAME].hpit_students.find({})
        result.count().should.equal(1)
        result[0]["attributes"].should.equal({})  
        
        session = client[settings.MONGO_DBNAME].hpit_sessions.find_one({"student_id":str(result[0]["_id"])})
        
        self.test_subject.send_response.assert_called_with("2",{"student_id":str(result[0]["_id"]),"attributes":{},"resource_id":"456","session_id":str(session["_id"])})
        self.test_subject.send_response.reset_mock()
        
        test_message = {"message_id":"2","attributes":{"attr":"value"},"sender_entity_id":"3"}
        self.test_subject.add_student_callback(test_message)
        result = client[settings.MONGO_DBNAME].hpit_students.find({})
        result.count().should.equal(2)
        result[1]["attributes"].should.equal({"attr":"value"})
        
        session = client[settings.MONGO_DBNAME].hpit_sessions.find_one({"student_id":str(result[1]["_id"])})
        
        self.test_subject.send_response.assert_called_with("2",{"student_id":str(result[1]["_id"]),"attributes":{"attr":"value"},"resource_id":"456","session_id":str(session["_id"])})
        
    def test_get_student_callback(self):
        """
        StudentManagementPlugin.get_student_callback() Test plan:
            - Mock logger, ensure written to when called
            - mock response
            - send message without student id, response should contain error
            - with no student, should return an error
            - add a student
            - response should have call with student_id, and attributes
        """
        test_message = {"message_id":"2","sender_entity_id":"123"}
        calls = [call("GET_STUDENT"),call(test_message)]
        self.test_subject.send_response = MagicMock()
        
        self.test_subject.get_student_callback(test_message)
        self.test_subject.send_log_entry.assert_has_calls(calls)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"Must provide a valid 'student_id' to get a student"})
        self.test_subject.send_response.reset_mock()
        
        #get non existing student
        bogus_id = ObjectId()
        test_message = {"message_id":"2","student_id":str(bogus_id),"sender_entity_id":"123"}
        self.test_subject.get_student_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"Student with id "+str(bogus_id)+" not found."})
        self.test_subject.send_response.reset_mock()
        
        #try with a good student
        sid = self.test_subject.db.insert({"attributes":{"key":"value"},"owner_id":"123","resource_id":"4"})
        test_message = {"message_id":"2","student_id":sid,"sender_entity_id":"123"}
        self.test_subject.get_student_callback(test_message)
        
        session = self.test_subject.session_db.find_one({"student_id":str(sid)})
        
        self.test_subject.send_response.assert_called_once_with("2",{"student_id":str(sid),"resource_id":"4","attributes":{"key":"value"},"session_id":str(session["_id"])})
        self.test_subject.send_response.reset_mock()
        
        #try without owner
        test_message = {"message_id":"2","student_id":sid,"sender_entity_id":"456"}
        self.test_subject.get_student_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"Student with id "+str(sid)+" not found."})
        self.test_subject.send_response.reset_mock()
        
        
    def test_set_attribute_callback(self):
        """
        StudentManagementPlugin.set_attribute_callback() Test plan:
            - Mock logger, ensure written to when called
            - Try lacking id, name, and value; response should have an error
            - Get an attribute with a bum ID; should send back error
            - Send in a real OID, should have real response.  Attribute should be changed in response and in db
        """
        test_message = {"message_id":"2","sender_entity_id":"123"}
        calls = [call("SET_ATTRIBUTE"),call(test_message)]
        self.test_subject.send_response = MagicMock()
        
        #no id
        self.test_subject.set_attribute_callback(test_message)
        self.test_subject.send_log_entry.assert_has_calls(calls)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"Must provide a 'student_id', 'attribute_name' and 'attribute_value'"})
        self.test_subject.send_response.reset_mock()
        
        #no attr
        test_message = {"message_id":"2","student_id":ObjectId(),"sender_entity_id":"123"}
        self.test_subject.set_attribute_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"Must provide a 'student_id', 'attribute_name' and 'attribute_value'"})
        self.test_subject.send_response.reset_mock()
        
        #no val
        test_message = {"message_id":"2","student_id":ObjectId(),"attribute_name":"attr","sender_entity_id":"123"}
        self.test_subject.set_attribute_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"Must provide a 'student_id', 'attribute_name' and 'attribute_value'"})
        self.test_subject.send_response.reset_mock()
        
        #bogus id
        bogus_id = ObjectId()
        test_message = {"message_id":"2","student_id":str(bogus_id),"attribute_name":"attr","attribute_value":"val","sender_entity_id":"123"}
        self.test_subject.set_attribute_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"Student with id "+str(bogus_id)+" not found."})
        self.test_subject.send_response.reset_mock()
        
        #good id
        sid = self.test_subject.db.insert({"attributes":{"key":"value"},"owner_id":"123"})
        test_message = {"message_id":"2","student_id":sid,"attribute_name":"key","attribute_value":"new_value","sender_entity_id":"123"} #override previous val
        self.test_subject.set_attribute_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"student_id":str(sid),"attributes":{"key":"new_value"}})
        self.test_subject.db.find_one({"_id":sid})["attributes"]["key"].should.equal("new_value")
        self.test_subject.send_response.reset_mock()
        
        #not owner
        test_message["sender_entity_id"]="456"
        self.test_subject.set_attribute_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"Student with id "+str(sid)+" not found."})
        
    def test_get_attribute_callback(self):
        """
        StudentManagementPlugin.get_attribute_callback() Test plan:
            - Mock logger, ensure written to when called
            - Try missing id and attribute name, should respond with error
            - Try with bogus student, should show error
            - Try with valid attribute, should respond with value
            - Try with bogus attribute, should reply empty
        """
        test_message = {"message_id":"2","sender_entity_id":"123"}
        calls = [call("GET_ATTRIBUTE"),call(test_message)]
        self.test_subject.send_response = MagicMock()
        
        #no student id
        self.test_subject.get_attribute_callback(test_message)
        self.test_subject.send_log_entry.assert_has_calls(calls)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"Must provide a 'student_id' and 'attribute_name'"})
        self.test_subject.send_response.reset_mock()
        
        #no attribute name
        test_message = {"message_id":"2","student_id":ObjectId(),"sender_entity_id":"123"}
        self.test_subject.get_attribute_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"Must provide a 'student_id' and 'attribute_name'"})
        self.test_subject.send_response.reset_mock()
        
        #bogus student id
        bogus_id = ObjectId()
        test_message = {"message_id":"2","student_id":str(bogus_id),"attribute_name":"attr","sender_entity_id":"123"}
        self.test_subject.get_attribute_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"Student with id "+str(bogus_id)+" not found."})
        self.test_subject.send_response.reset_mock()
        
        #get good key
        sid = self.test_subject.db.insert({"attributes":{"key":"value"},"owner_id":"123","resource_id":"456"})
        test_message = {"message_id":"2","student_id":sid,"attribute_name":"key","sender_entity_id":"123"}
        self.test_subject.get_attribute_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"student_id":str(sid),"key":"value","resource_id":"456"})
        self.test_subject.send_response.reset_mock()
        
        #get bogus key
        test_message = {"message_id":"2","student_id":sid,"attribute_name":"bogus_key","sender_entity_id":"123"}
        self.test_subject.get_attribute_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"student_id":str(sid),"bogus_key":"","resource_id":"456"})
        self.test_subject.send_response.reset_mock()
        
        #not owner
        test_message["sender_entity_id"] = "890"
        self.test_subject.get_attribute_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"Student with id "+str(sid)+" not found."})
        
    def test_get_student_model_callback(self):
        """
        StudentManagementPlugin.get_student_model_callback() Test plan:
            - pass it something without a student id, should respond with error
            - student_models, timeout_threads should be set
            - mock out Timer.start, ensure called
            - mock send, ensure sent with proper parameters
        """
        self.test_subject.send_response = MagicMock()
        
        #no id
        msg = {"message_id":"1","sender_entity_id":"123"}
        self.test_subject.get_student_model_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
             "error":"get_student_model requires a 'student_id'",     
        })
        self.test_subject.send_response.reset_mock()
        
        #bogus id
        bogus = ObjectId()
        msg["student_id"] = bogus
        self.test_subject.get_student_model_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
             "error":"student with id " + str(bogus) + " does not exist.",     
        })
        
        #this should work
        sid = self.test_subject.db.insert({"attributes":{"key":"value"},"owner_id":"123","resource_id":"456"})
        msg["student_id"] = sid
        msg["sender_entity_id"]="123"
        setattr(Timer,"start",MagicMock())
        self.test_subject.send = MagicMock()
        self.test_subject.get_populate_student_model_callback_function = MagicMock(return_value="3")
        self.test_subject.get_student_model_callback(msg)
        self.test_subject.student_models["1"].should.equal({})
        self.test_subject.timeout_threads["1"].start.assert_called_with()
        self.test_subject.send.assert_called_with("get_student_model_fragment",{
            "student_id":str(sid),
            'update': False
        },"3")
    
    def test_get_student_model_callback_cached(self):
        """
        StudentManagementPlugin.get_student_model_callback() Cached Test plan:
            - put a student model in the cache
            - run get_student_model_callback with no update, and update false, should proceed as planned
            - run with update = true, should reply with what is in the cache.
        """
        pass
        """
        setattr(Timer,"start",MagicMock())
        self.test_subject.send = MagicMock()
        self.test_subject.send_response = MagicMock()
        self.test_subject.get_populate_student_model_callback_function = MagicMock(return_value="3")

        #no update, should send message get_student_model_fragment
        sid = self.test_subject.db.insert({"attributes":{"key":"value"},"owner_id":"456","resource_id":"789"})
        msg = {"message_id":"1","student_id":sid,"sender_entity_id":"456"}

        self.test_subject.get_student_model_callback(msg)

        self.test_subject.send.assert_called_with("get_student_model_fragment",{
            "student_id":str(sid),
            "update": False
        },"3")
        
        #update set to true, same thing
        msg["update"]=True
        
        self.test_subject.get_student_model_callback(msg)

        self.test_subject.send.assert_called_with("get_student_model_fragment",{
            "update": True,
            "student_id":str(sid),
        },"3")
        
        #update set to false, nothing exists, should do same thing
        msg["update"]=False
        
        self.test_subject.get_student_model_callback(msg)

        self.test_subject.send.assert_called_with("get_student_model_fragment",{
            "student_id":str(sid),
            "update": False
        },"3")
        
        #update false, thing in cache, should return student model
        self.test_subject.cache.set(str(sid),{"knowledge_tracing":["1","2"]})
        self.test_subject.get_student_model_callback(msg)

        self.test_subject.send_response.assert_called_with("1",{
            "student_id": str(sid),
            "student_model" : {"knowledge_tracing":["1","2"]},
            "cached": True,
            "resource_id":"789"
        })
        """
       
        
        
    
    def test_get_populate_student_model_callback_function(self):
        """
        StudentManagementPlugin.get_populate_student_model_callback() Test plan:
            - call the method, get the function
            - call said function without response[name], message[student_id] and response[fragment], should exit cleanly, send_response not called
            - set some student_model_fragments to None, should break out, send_response not called
            - set some bogus fragments, raising key error, should break out, send_response not called
            - with empty self.timeout_threads, should not call send response
            - with self.timeout_threads[student_id], should call send response, cancel threads (mock out) and remove threads
        """
        #init stuff
        self.test_subject.send_response = MagicMock()
        #self.test_subject.cache.set = MagicMock()
        msg = {"message_id":"1"}        
        self.test_subject.timeout_threads["1"] = Timer(15,self.test_subject.kill_timeout,[msg, "123"])
        self.test_subject.student_model_fragment_names = ["knowledge_tracing"]
        
        #missing student_id
        func = self.test_subject.get_populate_student_model_callback_function("123", msg)
        func({"name":"knowledge_tracing","fragment":"some data"})
        self.test_subject.send_response.call_count.should.equal(0)
        
        #missing name
        msg = {"message_id":"1","student_id":"123"}
        func = self.test_subject.get_populate_student_model_callback_function("123", msg)
        func({"fragment":"some data"})
        self.test_subject.send_response.call_count.should.equal(0)
        
        #missing fragment
        msg = {"message_id":"1","student_id":"123"}
        func = self.test_subject.get_populate_student_model_callback_function("123", msg)
        func({"name":"knowledge_tracing"})
        self.test_subject.send_response.call_count.should.equal(0)
               
        #will still not be called, key error until 123 added to student models
        msg = {"message_id":"1","student_id":"123"}
        func = self.test_subject.get_populate_student_model_callback_function("123", msg)
        func({"name":"knowledge_tracing","fragment":"some_data"})
        self.test_subject.send_response.call_count.should.equal(0)
        
        self.test_subject.student_models["1"] = {}
        
        #bogus name should break for loop
        msg = {"message_id":"1","student_id":"123"}
        func = self.test_subject.get_populate_student_model_callback_function("123", msg)
        func({"name":"bogus_name","fragment":"some_data"})
        self.test_subject.send_response.call_count.should.equal(0)
        
        #this should work
        sid = self.test_subject.db.insert({"attributes":{"key":"value"},"owner_id":"123","resource_id":"456"})
        msg = {"message_id":"1","student_id":sid,"sender_entity_id":"123"}
        func = self.test_subject.get_populate_student_model_callback_function(str(sid),msg)
        func({"name":"knowledge_tracing","fragment":"some_data"})
        self.test_subject.send_response.assert_called_with("1",{
            "student_id": str(sid),
            "student_model":{"knowledge_tracing":"some_data"},
            "cached":False,
            "resource_id":"456",
            "message_id":"1",
        })
        self.test_subject.timeout_threads.should_not.contain("1")
        self.test_subject.student_models.should_not.contain("1")
        self.test_subject.send_response.reset_mock()
        
        #self.test_subject.cache.set.assert_called_with(str(sid),{"knowledge_tracing":"some_data"})
        #self.test_subject.cache.set.reset_mock()
        
        #simulate timeout (timeout_thread["1"] will be deleted in above test)
        msg = {"message_id":"1","student_id":sid,"sender_entity_id":"123"}
        func = self.test_subject.get_populate_student_model_callback_function(str(sid),msg)
        func({"name":"knowledge_tracing","fragment":"some_data","cached":False})
        self.test_subject.send_response.call_count.should.equal(0)
        #self.test_subject.cache.set.call_count.should.equal(0)
        
        
    def test_kill_timeout(self):
        """
        StudentManagementPlugin.kill_timeout() Test plan:
            - with nothing in threads or student_models, should exit cleanly, calling response
            - put something in student_models[student_id] and timeout_threads[student_id]
            - mock out send_response, ensured called with proper parameters
            - make sure keys get deleted in student_models and timeout_threads 
        """
        self.test_subject.send_response = MagicMock()
        
        sid = self.test_subject.db.insert({"attributes":{"key":"value"},"owner_id":"123","resource_id":"456"})
        
        msg = {"message_id":"1","student_id":str(sid),"sender_entity_id":"123"}
        self.test_subject.kill_timeout(msg,str(sid))
        self.test_subject.send_response.assert_called_with("1",{
            "error":"Get student model timed out. Here is a partial student model.",
            "student_model":{},
            "student_id": str(sid),
            "resource_id":"456",
            "message_id":"1",
            })
        self.test_subject.send_response.reset_mock()
        
        
        self.test_subject.student_models = {"1":"value"}
        self.test_subject.timeout_threads = {"1":"value"}
        
        
        self.test_subject.kill_timeout(msg, str(sid))
        self.test_subject.send_response.assert_called_with("1",{
            "error":"Get student model timed out. Here is a partial student model.",
            "student_model":"value",
            "student_id": str(sid),
            "resource_id":"456",
            "message_id":"1",
            })
        ("1" in self.test_subject.student_models).should.equal(False)
        ("1" in self.test_subject.timeout_threads).should.equal(False)
        
        self.test_subject.send_response.reset_mock()
        
    def test_transaction_callback_method(self):
        """
        StudentManagementPlugin.transaction_callback_method() Test plan:
            - call without student and session id, should reply with error
            - call with invalid session_id, should reply with error
            - call with completely bogus student, should reply with error
            - call with ID in attributes with valid session, should call send, calls callback
            - callback should call send_response, which should contain all the responses
            - use random session, should send error.
        """
        def mock_send(message_name,payload,callback):
            callback({"responder":["downstream"]})
                
        self.test_subject.send = MagicMock(side_effect = mock_send)
        self.test_subject.send_response = MagicMock()
        
        #no args
        msg = {"message_id":"1","sender_entity_id":"2"}
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
              "error":"transaction for Student Manager requires a 'student_id' and 'session_id'",
              "responder":["student_manager"]
        })
        self.test_subject.send_response.reset_mock()
        
        #one arg
        msg["student_id"]="123"
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
              "error":"transaction for Student Manager requires a 'student_id' and 'session_id'",
              "responder":["student_manager"]
        })
        self.test_subject.send_response.reset_mock()
        
        #bad session id
        msg["session_id"] = "456"
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
                    "error" : "The supplied 'session_id' is not a valid ObjectId.",
                    "responder":["student_manager"],
                    "success":False
            })
        self.test_subject.send_response.reset_mock()
        
        #student does not exist
        msg["session_id"] = ObjectId()
        bogus = ObjectId()
        msg["student_id"] = bogus
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{"error":"transaction failed; could not find student with id " + str(bogus) + ". Try using add_student first.","responder": ["student_manager"]})
        self.test_subject.send_response.reset_mock()
        
        #student exists in attributes, bad session
        student_id = self.test_subject.db.insert({"attributes":{"other_id":"123"},"owner_id":"2"})
        session_id = self.test_subject.session_db.insert({"student_id":str(student_id),"date_created":"now"})
        msg["student_id"] = "123"
        msg["session_id"] = bogus
        
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{"error":"transaction failed; could not find session with id " + str(bogus) +".  Try adding/getting a student for a valid session id.","responder": ["student_manager"]})
        self.test_subject.send_response.reset_mock()
        
        #student exists, attributes good
        msg["student_id"] = student_id
        msg["session_id"] = session_id
        
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "student_id":str(student_id),
            "session_id":str(session_id),
            "responder": ["student_manager","downstream"]
        })
        self.test_subject.send_response.reset_mock()
        
        
        
        
        
        
        
        
