import unittest
from mock import *
from pymongo import MongoClient
from pymongo.collection import Collection
from bson.objectid import ObjectId

from plugins import StudentManagementPlugin

class TestStudentManagementPlugin(unittest.TestCase):

    def setUp(self):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.test_subject = StudentManagementPlugin(123,456,None)
        self.test_subject.db = self.test_subject.mongo.test_hpit.hpit_students
        
    def tearDown(self):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        client = MongoClient()
        client.drop_database("test_hpit")
        
        self.test_subject = None

    def test_constructor(self):
        """
        StudentManagementPlugin.__init__() Test plan:
            -ensure name, logger set as parameters
            -ensure that mongo is an instance of MongoClient
            -ensure that db is an instance of Collection
            -ensure that the full name is test_hpit.hpit_students
        """
        smp = StudentManagementPlugin(123,456,None)
        isinstance(smp.mongo,MongoClient).should.equal(True)
        isinstance(smp.db,Collection).should.equal(True)
        smp.db.full_name.should.equal("hpit.hpit_students")
        
    def test_add_student_callback(self):
        """
        StudentManagementPlugin.add_student_callback() Test plan:
            -Mock logger, ensure written to when called
            -Send message without attributes, attributes should be empty in db
            -Send in attributes, should be present in database
            -Should be two distinc messages now
            -mock response, should have a call with the message id and student id
        """
        test_message = {"message_id":"2"}
        calls = [call("ADD_STUDENT"),call(test_message)]
        self.test_subject.logger = MagicMock()
        self.test_subject.send_response = MagicMock()
        
        self.test_subject.add_student_callback(test_message)
        self.test_subject.logger.debug.assert_has_calls(calls)
        
        client = MongoClient()
        result = client.test_hpit.hpit_students.find({})
        result.count().should.equal(1)
        result[0]["attributes"].should.equal({})  
        self.test_subject.send_response.assert_called_with("2",{"student_id":str(result[0]["_id"]),"attributes":{}})
        self.test_subject.send_response.reset_mock()
        
        test_message = {"message_id":"2","attributes":{"attr":"value"}}
        self.test_subject.add_student_callback(test_message)
        result = client.test_hpit.hpit_students.find({})
        result.count().should.equal(2)
        result[1]["attributes"].should.equal({"attr":"value"})
        self.test_subject.send_response.assert_called_with("2",{"student_id":str(result[1]["_id"]),"attributes":{"attr":"value"}})
        
    def test_get_student_callback(self):
        """
        StudentManagementPlugin.get_skill_callback() Test plan:
            - Mock logger, ensure written to when called
            - mock response
            - send message without student id, response should contain error
            - with no student, should return an error
            - add a student
            - response should have call with student_id, and attributes
        """
        test_message = {"message_id":"2"}
        calls = [call("GET_STUDENT"),call(test_message)]
        self.test_subject.logger = MagicMock()
        self.test_subject.send_response = MagicMock()
        
        self.test_subject.get_student_callback(test_message)
        self.test_subject.logger.debug.assert_has_calls(calls)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"Must provide a 'student_id' to get a student"})
        self.test_subject.send_response.reset_mock()
        
        bogus_id = ObjectId()
        test_message = {"message_id":"2","student_id":str(bogus_id)}
        self.test_subject.get_student_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"Student with id "+str(bogus_id)+" not found."})
        self.test_subject.send_response.reset_mock()
        
        sid = self.test_subject.db.insert({"attributes":{"key":"value"}})
        test_message = {"message_id":"2","student_id":sid}
        self.test_subject.get_student_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"student_id":str(sid),"attributes":{"key":"value"}})
      
    def test_set_attribute_callback(self):
        """
        StudentManagementPlugin.set_attribute_callback() Test plan:
            - Mock logger, ensure written to when called
            - Try lacking id, name, and value; response should have an error
            - Get an attribute with a bum ID; should send back error
            - Send in a real OID, should have real response.  Attribute should be changed in response and in db
        """
        test_message = {"message_id":"2"}
        calls = [call("SET_ATTRIBUTE"),call(test_message)]
        self.test_subject.logger = MagicMock()
        self.test_subject.send_response = MagicMock()
        
        self.test_subject.set_attribute_callback(test_message)
        self.test_subject.logger.debug.assert_has_calls(calls)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"Must provide a 'student_id', 'attribute_name' and 'attribute_value'"})
        self.test_subject.send_response.reset_mock()
        
        test_message = {"message_id":"2","student_id":ObjectId()}
        self.test_subject.set_attribute_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"Must provide a 'student_id', 'attribute_name' and 'attribute_value'"})
        self.test_subject.send_response.reset_mock()
        
        test_message = {"message_id":"2","student_id":ObjectId(),"attribute_name":"attr"}
        self.test_subject.set_attribute_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"Must provide a 'student_id', 'attribute_name' and 'attribute_value'"})
        self.test_subject.send_response.reset_mock()
        
        bogus_id = ObjectId()
        test_message = {"message_id":"2","student_id":str(bogus_id),"attribute_name":"attr","attribute_value":"val"}
        self.test_subject.set_attribute_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"Student with id "+str(bogus_id)+" not found."})
        self.test_subject.send_response.reset_mock()
        
        sid = self.test_subject.db.insert({"attributes":{"key":"value"}})
        test_message = {"message_id":"2","student_id":sid,"attribute_name":"key","attribute_value":"new_value"} #override previous val
        self.test_subject.set_attribute_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"student_id":str(sid),"attributes":{"key":"new_value"}})
        self.test_subject.db.find_one({"_id":sid})["attributes"]["key"].should.equal("new_value")
        
    def test_get_attribute_callback(self):
        """
        StudentManagementPlugin.get_attribute_callback() Test plan:
            - Mock logger, ensure written to when called
            - Try missing id and attribute name, should respond with error
            - Try with bogus student, should show error
            - Try with valid attribute, should respond with value
            - Try with bogus attribute, should reply empty
        """
        test_message = {"message_id":"2"}
        calls = [call("GET_ATTRIBUTE"),call(test_message)]
        self.test_subject.logger = MagicMock()
        self.test_subject.send_response = MagicMock()
        
        self.test_subject.get_attribute_callback(test_message)
        self.test_subject.logger.debug.assert_has_calls(calls)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"Must provide a 'student_id' and 'attribute_name'"})
        self.test_subject.send_response.reset_mock()
        
        test_message = {"message_id":"2","student_id":ObjectId()}
        self.test_subject.get_attribute_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"Must provide a 'student_id' and 'attribute_name'"})
        self.test_subject.send_response.reset_mock()
        
        bogus_id = ObjectId()
        test_message = {"message_id":"2","student_id":str(bogus_id),"attribute_name":"attr"}
        self.test_subject.get_attribute_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"Student with id "+str(bogus_id)+" not found."})
        self.test_subject.send_response.reset_mock()
        
        sid = self.test_subject.db.insert({"attributes":{"key":"value"}})
        test_message = {"message_id":"2","student_id":sid,"attribute_name":"key"}
        self.test_subject.get_attribute_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"student_id":str(sid),"key":"value"})
        self.test_subject.send_response.reset_mock()
        
        test_message = {"message_id":"2","student_id":sid,"attribute_name":"bogus_key"}
        self.test_subject.get_attribute_callback(test_message)
        self.test_subject.send_response.assert_called_once_with("2",{"student_id":str(sid),"bogus_key":""})
        
        
        
        
        
