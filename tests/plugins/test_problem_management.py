import unittest
from mock import *
from pymongo import MongoClient
from pymongo.collection import Collection
from bson.objectid import ObjectId

from hpit.plugins import ProblemManagementPlugin

from hpit.management.settings_manager import SettingsManager
settings = SettingsManager.get_plugin_settings()

import shlex
import json

class TestProblemManagementPlugin(unittest.TestCase):

    def setUp(self):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.test_subject = ProblemManagementPlugin(123,456,None,shlex.quote(json.dumps({
                "shared_messages": {
                    "get_student_model_fragment": [
                        "88bb246d-7347-4f57-8cbe-95944a4e0027"
                    ]
                }
            })) )   
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
        ProblemManagementPlugin.__init__() Test plan:
            - make sure logger, problem_fields set
            - make sure mongo is instance of MongoClient
            - make sure db is instance of collection
            - make sure db full name is hpit.hpit_problems
            - make sure step_db is instance of collection
            - make sure step_db name is hpit.hpit_steps
        """
        pmp = ProblemManagementPlugin(123,456,None,shlex.quote(json.dumps({
                "shared_messages": {
                    "get_student_model_fragment": [
                        "88bb246d-7347-4f57-8cbe-95944a4e0027"
                    ]
                }
            })))
        pmp.logger.should.equal(None)
        isinstance(pmp.mongo,MongoClient).should.equal(True)
        isinstance(pmp.db,Collection).should.equal(True)
        pmp.db.full_name.should.equal("hpit_unit_test_db.hpit_problems")
        isinstance(pmp.step_db,Collection).should.equal(True)
        pmp.step_db.full_name.should.equal("hpit_unit_test_db.hpit_steps")
        isinstance(pmp.worked_db,Collection).should.equal(True)
        pmp.worked_db.full_name.should.equal("hpit_unit_test_db.hpit_problems_worked")
        
    def test_add_problem_callback(self):
        """
        ProblemManagementPlugin.add_problem_callback() Test plan:
            - send in message w/o problem name or text, response should have error
            - send in valid stuff, make sure response contains proper values, record in db
            - send in same stuff, make sure that an error response is found
        """
        msg = {"message_id":"1", "sender_entity_id":"2","problem_name":"problem 1","problem_text":"123"}
        self.test_subject.add_problem_callback(msg)
        
        problem_id = self.test_subject.db.find_one({})["_id"]
        problem_id.should_not.equal(None)
        
        self.test_subject.send_response.assert_called_with("1", {
                'problem_name': "problem 1",
                'problem_text': "123",
                'success': True,
                'problem_id':str(problem_id)
            })
        
    def test_add_problem_callback_no_problem_name(self):
        """
        ProblemManagementPlugin.add_problem_callback() No Problem Name:
        """
        msg = {"message_id":"1", "sender_entity_id":"2"}
        self.test_subject.add_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {"error":"Add problem requires 'problem_name' and 'problem_text'","success":False})
    
    def test_add_problem_callback_no_problem_text(self):
        """
        ProblemManagementPlugin.add_problem_callback() No Problem Text:
        """
        msg = {"message_id":"1", "sender_entity_id":"2","problem_name":"problem 1"}
        self.test_subject.add_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {"error":"Add problem requires 'problem_name' and 'problem_text'","success":False})      
        
    def test_add_problem_callback_existing_problem(self):
        """
        ProblemManagementPlugin.add_problem_callback() Existing Problem:
        """
        msg = {"message_id":"1", "sender_entity_id":"2","problem_name":"problem 1","problem_text":"123","edit_allowed_id":"2"}
        problem_id = self.test_subject.db.insert(msg)
        
        self.test_subject.add_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "error": "This problem already exists.",
                "problem_id": str(problem_id),
                "success":False,
        })

    def test_remove_problem_callback(self):
        """
        ProblemManagementPlugin.remove_problem_callback() Test plan:
            - send message w/out problem id, reponse should have error
            - with empty db, should return not found error
            - put something in db, should return success message
            - record should be gone
        """
        problem_id = self.test_subject.db.insert({
                "problem_name":"problem 1",
                "problem_text": "123",
                "date_created": "3:40",
                "edit_allowed_id":"2"
         })
        msg = {"message_id":"1","sender_entity_id":"2","problem_id":problem_id}
        another_problem_id = self.test_subject.db.insert({
                "problem_name":"problem 1",
                "problem_text": "123",
                "date_created": "3:40",
                "edit_allowed_id":"2"
         })
        self.test_subject.remove_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                'exists': True,
                'success': True,
            })
        
        self.test_subject.db.find_one({"_id":problem_id}).should.equal(None)
        self.test_subject.db.find({}).count().should.equal(1)
        
    def test_remove_problem_callback_no_problem_id(self):
        """
        ProblemManagementPlugin.remove_problem_callback() No Problem Id:
        """
        msg = {"message_id":"1","sender_entity_id":"2"}
        self.test_subject.remove_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error":"remove_problem requires 'problem_id'",
                "success":False,
        })
        
    def test_remove_problem_callback_no_problem_exists(self):
        """
        ProblemManagementPlugin.remove_problem_callback() No Problem Exists:
        """
        msg = {"message_id":"1","sender_entity_id":"2","problem_id":str(ObjectId())}
        self.test_subject.remove_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error": "Could not delete problem; it does not exist",
                'problem_id': str(msg["problem_id"]),
                'exists': False,
                'success': False
            })
    
    def test_get_problem_callback(self):
        """
        ProblemManagementPlugin.get_problem_callback() Test plan:
            - send message without problem id, should return error response
            - send in bogus id, should return error response
            - send in id of existing, should return valid response
        """
        good_id = self.test_subject.db.insert({
                "problem_name":"problem 1",
                "problem_text":"123",
                "date_created":"3:40",
                "edit_allowed_id":"2",
        })
        msg = {"message_id":"1","sender_entity_id":"2","problem_id":good_id}
        self.test_subject.get_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "problem_id":str(good_id),
                "problem_name":"problem 1",
                "problem_text":"123",
                "date_created":"3:40",
                "edit_allowed_id":"2",
                'exists':True,
                'success':True
        })
        
    def test_get_problem_callback_no_problem_id(self):
        """
        ProblemManagementPlugin.get_problem_callback() No Problem Id:
        """
        msg = {"message_id":"1","sender_entity_id":"2"}
        self.test_subject.get_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error":"get_problem requires a 'problem_id'",
                "success":False,
        })
        
    def test_get_problem_callback_no_problem_exists(self):
        """
        ProblemManagementPlugin.get_problem_callback() No Problem Exists:
        """
        bogus_id = ObjectId()
        msg = {"message_id":"1","sender_entity_id":"2","problem_id":bogus_id}
        self.test_subject.get_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                'error': "Error:  problem with id" + str(bogus_id) + " does not exist.",
                'exists': False,
                'success': False
            })
   
    def test_edit_problem_callback(self):
        """
        ProblemManagementPlugin.edit_problem_callback() Test plan:
            - send message without problem_id and fields, should respond with error
            - send in bogus id, should respond with error
            - send bogus entity_id, should respond with error
            - send in non subscriptable element for fields, should respond with error
            - fields: bogus elements, no changes
            - fields: one bogus, one right.  one chanes, one shouldnt
            - fields: both good: both should change.
            - response returns success for all three.  
        """
        good_id = self.test_subject.db.insert({
                "edit_allowed_id":"2",
                "problem_name":"problem 1",
                "problem_text": "123",
                "date_created":"3:40",
        })
        msg = {"message_id":"1","sender_entity_id":"2","problem_id":good_id}
        msg["fields"] = {"problem_name":"new problem 1","problem_text":"321"}
        self.test_subject.edit_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                'problem_name': "new problem 1",
                'problem_text': "321",
                'date_created': "3:40",
                'edit_allowed_id' : "2",
                'success': True
            })
        
        self.test_subject.db.find_one({
                'problem_name': "new problem 1",
                'problem_text': "321",
                'date_created': "3:40",
                'edit_allowed_id' : "2",
        }).should_not.equal(None)
        
    def test_edit_problem_callback_no_problem_id(self):
        """
        ProblemManagementPlugin.edit_problem_callback() No Problem Id:
        """
        msg = {"message_id":"1","sender_entity_id":"2"}
        self.test_subject.edit_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
            "error":"edit_problem requires 'problem_id' and 'fields'",
            "success":False      
        })
        
    def test_edit_problem_callback_no_fields(self):
        """
        ProblemManagementPlugin.edit_problem_callback() No Fields:
        """
        msg = {"message_id":"1","sender_entity_id":"2","problem_id":ObjectId()}
        self.test_subject.edit_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
            "error":"edit_problem requires 'problem_id' and 'fields'",
            "success":False      
        })
        
    def test_edit_problem_callback_invalid_id(self):
        """
        ProblemManagementPlugin.edit_problem_callback() Invalid Problem Id:
        """
        msg = {"message_id":"1","sender_entity_id":"2","problem_id":ObjectId()}
        msg["fields"] = {"bogus1":"value","bogus2":"value"}
        self.test_subject.edit_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
            "error": "Error: either problem with provided id doesn't exist, or you do not have permission to edit.",
            "success":False,
        })
        
    def test_edit_problem_callback_permission_denied(self):
        """
        ProblemManagementPlugin.edit_problem_callback() Permission Denied:
        """
        bad_id = self.test_subject.db.insert({
                "edit_allowed_id":"3",
                "problem_name":"problem 2",
                "problem_text": "456",
                "date_created":"3:40",
        })
        msg = {"message_id":"1","sender_entity_id":"2","problem_id":bad_id}
        msg["fields"] = {"bogus1":"value","bogus2":"value"}
        
        self.test_subject.edit_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
            "error": "Error: either problem with provided id doesn't exist, or you do not have permission to edit.",
            "success":False,
        })
        
    def test_edit_problem_callback_bad_fields(self):
        """
        ProblemManagementPlugin.edit_problem_callback() Fields Not Dict:
        """
        good_id = self.test_subject.db.insert({
                "edit_allowed_id":"2",
                "problem_name":"problem 1",
                "problem_text": "123",
                "date_created":"3:40",
        })
        msg = {"message_id":"1","sender_entity_id":"2","problem_id":good_id}
        msg["fields"] = 4
        self.test_subject.edit_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "error":"Fields needs to be a dict.",
                "success":False
        })
        
    def test_edit_problem_callback_ignored_fields(self):
        """
        ProblemManagementPlugin.edit_problem_callback() Ignored Fields:
        """
        good_id = self.test_subject.db.insert({
                "edit_allowed_id":"2",
                "problem_name":"problem 1",
                "problem_text": "123",
                "date_created":"3:40",
        })
        msg = {"message_id":"1","sender_entity_id":"2","problem_id":good_id}
        msg["fields"] = {"bogus1":"value","bogus2":"value"}
        self.test_subject.edit_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                'problem_name': "problem 1",
                'problem_text': "123",
                'date_created': "3:40",
                'edit_allowed_id' : "2",
                'success': True
            })
        
    def test_edit_problem_callback_one_ignored_field(self):
        """
        ProblemManagementPlugin.edit_problem_callback() One Ignored Field:
        """
        good_id = self.test_subject.db.insert({
                "edit_allowed_id":"2",
                "problem_name":"problem 1",
                "problem_text": "123",
                "date_created":"3:40",
        })
        msg = {"message_id":"1","sender_entity_id":"2","problem_id":good_id}
        msg["fields"] = {"problem_name":"new problem 1","bogus2":"value"}
        self.test_subject.edit_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                'problem_name': "new problem 1",
                'problem_text': "123",
                'date_created': "3:40",
                'edit_allowed_id' : "2",
                'success': True
            })
        
           
    def test_list_problems_callback(self):
        """
        ProblemManagementPlugin.list_problems_callback() Test plan:
            - if problems empty, response should be empty
            - else, response added should be present
        """
        msg = {"message_id":"1"}
        self.test_subject.db.insert([
                {
                    "problem_text":"123"
                },
                {
                    "problem_text":"456"
                }
        ])
        
        self.test_subject.list_problems_callback(msg)
        len(self.test_subject.send_response.call_args[0][1]).should.equal(2)
        
    def test_list_problems_empty_set(self):
        """
        ProblemManagementPlugin.list_problems_callback() Empty Set:
        """
        msg = {"message_id":"1"}
        self.test_subject.list_problems_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "problems":[],
                "success":True,
        })
        
        
        
    def test_clone_problem_callback(self):
        """
        ProblemManagementPlugin.clone_problem_callback() Test plan:
            - send message without problem_id, should respond with error
            - if bogus id passed, should respond with error
            - ensure new problem added with same fields, sender entity id matching caller
            - make sure steps copied properly
            - response should be correct
        """
        bogus_id = ObjectId()
        good_id = self.test_subject.db.insert({
                "problem_name" : "problem 1",
                "problem_text" : "123",
                "date_created" : "3:40",
                "edit_allowed_id": "3"
        })
        step_ids = self.test_subject.step_db.insert([
                {
                    "step_text":"subtract",
                    "date_created":"3:40",
                    "problem_id":good_id,
                    "edit_allowed_id":"3",
                    "skill_ids":{"addition":"44"},
                    "skill_names":{"math":"addition"},
                },
                {
                    "step_text":"subtract",
                    "date_created":"3:40",
                    "problem_id":good_id,
                    "edit_allowed_id":"3",
                    "skill_ids":{"addition":"44"},
                    "skill_names":{"math":"addition"},
                },
                {
                    "step_text":"subtract",
                    "date_created":"3:40",
                    "problem_id":bogus_id,
                    "edit_allowed_id":"4",
                    "skill_ids":{"addition":"44"},
                    "skill_names":{"math":"addition"},
                },
        ])
        for sid in step_ids:
            self.test_subject.transaction_db.insert([
                 {
                    "transaction_text":"transaction",
                    "date_created":"3:40",
                    "step_id":sid,
                    "edit_allowed_id":"3",
                    "skill_ids":{"addition":"44"},
                    "skill_names":{"math":"addition"},
                },
                {
                    "transaction_text":"transaction",
                    "date_created":"3:40",
                    "step_id":sid,
                    "edit_allowed_id":"3",
                    "skill_ids":{"addition":"44"},
                    "skill_names":{"math":"addition"},
                },
                {
                    "transaction_text":"transaction",
                    "date_created":"3:40",
                    "step_id":sid,
                    "edit_allowed_id":"4",
                    "skill_ids":{"addition":"44"},
                    "skill_names":{"math":"addition"},
                },  
            ])
        
        msg = {"message_id":"1","sender_entity_id":"2","problem_id":good_id}
        self.test_subject.clone_problem_callback(msg)
        
        new_added_problem = self.test_subject.db.find_one({
            "problem_name" : "problem 1",
            "problem_text" : "123",
            "edit_allowed_id": "2"
        })
        new_added_problem.should_not.equal(None)
        
        new_added_ids = self.test_subject.step_db.find({
                "step_text":"subtract",
                "problem_id":new_added_problem["_id"],
                "edit_allowed_id":"2", 
        })
        
        new_added_transactions = self.test_subject.transaction_db.find({
               "transaction_text":"transaction",
                "edit_allowed_id":"2",  
        })
        
        new_added_ids.count().should.equal(2)
        new_added_transactions.count().should.equal(4)
        
        self.test_subject.send_response.assert_called_with("1", {
                "problem_id": str(new_added_problem["_id"]),
                "step_ids": [str(s["_id"]) for s in new_added_ids],
                "transaction_ids":[str(t["_id"]) for t in new_added_transactions],
                "success": True
        })
        
    def test_clone_problem_callback_no_problem_id(self):
        """
        ProblemManagementPlugin.clone_problem_callback() No Problem Id:
        """
        msg = {"message_id":"1","sender_entity_id":"2"}
        self.test_subject.clone_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                    "error": "clone_problem requires a 'problem_id'.",
                    "success":False,
            })
        
    def test_clone_problem_callback_problem_non_exist(self):
        """
        ProblemManagementPlugin.clone_problem_callback() Problem Does Not Exist:
        """
        bogus_id = ObjectId()
        msg = {"message_id":"1","sender_entity_id":"2","problem_id":bogus_id}
        self.test_subject.clone_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                    "error": "Problem with id " + str(bogus_id) + " does not exist.",
                    "success":False
            })
        self.test_subject.send_response.reset_mock()
        
        
 
    def test_add_problem_worked_callback(self):
        """
        ProblemManagementPlugin.add_problem_worked_callback() Test plan:
            - mock send response
            - send message without problem_id and student_id, should respond with error
            - with bogus problem ID, should return error that it isn't valid
            - with an ID that doesn't exist ( but object ID) it should return an error
            - otherwise, success should be sent, and a record mapping student_id and problem_id should exist
        """
        problem_id = self.test_subject.db.insert({"problem_name": "hello"})
        msg = {"message_id":"1","student_id":"2","problem_id":problem_id}
        self.test_subject.add_problem_worked_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "success":True,
        })
        
        self.test_subject.worked_db.find_one({"student_id":"2","problem_id":problem_id}).should_not.equal(None)
        
    def test_add_problem_worked_callback_no_student_id(self):
        """
        ProblemManagementPlugin.add_problem_worked_callback() No Student Id:
        """
        msg = {"message_id":"1"}
        self.test_subject.add_problem_worked_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error" : "add_problem_worked requires a 'problem_id' and 'student_id'",
                 "success":False
             })
        
    def test_add_problem_worked_callback_no_problem_id(self):
        """
        ProblemManagementPlugin.add_problem_worked_callback() No Problem Id:
        """
        msg = {"message_id":"1","student_id":"2"}
        self.test_subject.add_problem_worked_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error" : "add_problem_worked requires a 'problem_id' and 'student_id'",
                 "success":False
             })
        
    def test_add_problem_worked_callback_invalid_problem_id(self):
        """
        ProblemManagementPlugin.add_problem_worked_callback() Invalid Problem Id:
        """
        msg = {"message_id":"1","student_id":"2","problem_id":"3"}
        self.test_subject.add_problem_worked_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                    "error" : "The supplied 'problem_id' is not a valid ObjectId.",
                    "success":False
            })
        
    def test_add_problem_worked_callback_problem_not_exist(self):
        """
        ProblemManagementPlugin.add_problem_worked_callback() Problem Does Not Exist Id:
        """
        bogus = ObjectId()
        msg = {"message_id":"1","student_id":"2","problem_id":bogus}
        self.test_subject.add_problem_worked_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
             "error" : "Problem with ID "+str(bogus) + " does not exist.",
                    "success":False  
        })
    
    def test_get_problems_worked_callback(self):
        """
        ProblemManagementPlugin.get_problems_worked_callback() Test plan:
            -mock send response
            - send message without student_id, should respnd with error
            - if nothing in db, should return empty list
            - otherwise, should return problems that map to the student ID
        """
        msg = {"message_id":"1","student_id":"2"}
        self.test_subject.worked_db.insert([      
            {"student_id":"2","problem_id":"123"},
            {"student_id":"2","problem_id":"456"},
            {"student_id":"3","problem_id":"123"},
        ])
        
        cur = self.test_subject.worked_db.find({
            "student_id": "2",       
        })
        problems = [p for p in cur]
        
        self.test_subject.get_problems_worked_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
              "success":True,
              "problems_worked" : problems
        })

    def test_get_problems_worked_callback_no_student_id(self):
        """
        ProblemManagementPlugin.get_problems_worked_callback() No Student Id:
        """
        msg = {"message_id":"1"}
        self.test_subject.get_problems_worked_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
              "error" : "add_problem_worked requires a 'student_id'",
               "success":False  
        })
    
    def test_get_problems_worked_callback_empty_set(self): 
        """
        ProblemManagementPlugin.get_problems_worked_callback() Empty Set:
        """
        msg = {"message_id":"1","student_id":"2"}
        self.test_subject.get_problems_worked_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
              "success":True,
              "problems_worked" : [],
        })
        
       
        
    def test_add_step_callback(self):
        """
        ProblemManagementPlugin.add_step_callback() Test plan:
            - send in message without problem id and step text, should return error
            - send in bogus id, bogus entity_id, should each return error
            - make sure step_text, allowed_entity_id, and problem_id all set
            - response should contain step id and success
        """
        good_id = self.test_subject.db.insert({
                "edit_allowed_id":"2",
        })
        msg = {"message_id":"1", "sender_entity_id":"2","step_text":"subtract","problem_id":good_id}
        msg["skill_names"] = {"math":"addition"}
        
        self.test_subject.add_step_callback(msg)
        
        step = self.test_subject.step_db.find_one({"step_text":"subtract","skill_names":{"math":"addition"},"skill_ids":{}})
        step.should_not.equal(None)
        
        self.test_subject.send_response.assert_called_with("1",{
                    "step_id":str(step["_id"]),
                    "success":True,
            })
        
    def test_add_step_callback_no_step_text(self):
        """
        ProblemManagementPlugin.add_step_callback() No Step Text:
        """
        msg = {"message_id":"1", "sender_entity_id":"2"}
        self.test_subject.add_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
               "error": "add_step requires a 'problem_id' and 'step_text'",
               "success":False,
        })
        
    def test_add_step_callback_no_problem_id(self):
        """
        ProblemManagementPlugin.add_step_callback() No Problem Id:
        """
        msg = {"message_id":"1", "sender_entity_id":"2","step_text":"subtract"}
        self.test_subject.add_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
               "error": "add_step requires a 'problem_id' and 'step_text'",
               "success":False
        })
        
    def test_add_step_callback_no_problem(self):
        """
        ProblemManagementPlugin.add_step_callback() Problem Does Not Exist:
        """
        msg = {"message_id":"1", "sender_entity_id":"2","step_text":"subtract","problem_id":ObjectId()}
        self.test_subject.add_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error": "Error: either problem with provided id doesn't exist, or you do not have permission to edit.",
                "success":False,
        })
    
    def test_add_step_callback_permission_denied(self):
        """
        ProblemManagementPlugin.add_step_callback() Permission Denied:
        """
        good_id = self.test_subject.db.insert({
                "edit_allowed_id":"2",
        })
        msg = {"message_id":"1", "sender_entity_id":"3","step_text":"subtract","problem_id":ObjectId()}
        self.test_subject.add_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error": "Error: either problem with provided id doesn't exist, or you do not have permission to edit.",
                "success":False,
        })

    def test_remove_step_callback(self):
        """
        ProblemManagmentPlugin.remove_step_callback() Test plan:
            - send message without step_id, should send error response
            - send in bogus entity_id and step_id, should each return error response
            - if nothing in db, error response should be called
            - make sure proper response is removed, record removed on good call
        """
        good_id = self.test_subject.step_db.insert({
                "edit_allowed_id":"2",
        })
        msg = {"message_id":"1", "sender_entity_id":"2","step_id":good_id}
        self.test_subject.remove_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                    "success":True,
                    "exists":True,
            })
        self.test_subject.step_db.find({}).count().should.equal(0)
        
    def test_remove_step_callback_no_step_id(self):
        """
        ProblemManagmentPlugin.remove_step_callback() No step Id:
        """
        msg = {"message_id":"1", "sender_entity_id":"2"}
        self.test_subject.remove_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
               "error": "remove_step requires 'step_id'",
               "success":False,
        })
        
    def test_remove_step_callback_step_no_exist(self):
        """
        ProblemManagmentPlugin.remove_step_callback() Does Not Exist:
        """
        msg = {"message_id":"1", "sender_entity_id":"2","step_id":ObjectId()}
        
        self.test_subject.remove_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error": "Either the step doesn't exist or you don't have permission to remove it.",
                "success":False,
        })
        
    def test_remove_step_callback_permission_denied(self):
        """
        ProblemManagmentPlugin.remove_step_callback() Permission Denied:
        """
        good_id = self.test_subject.step_db.insert({
                "edit_allowed_id":"2",
        })
        msg = {"message_id":"1", "sender_entity_id":"3","step_id":good_id}  
        self.test_subject.remove_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error": "Either the step doesn't exist or you don't have permission to remove it.",
                "success":False,
        })
        
        
        
       
    def test_get_step_callback(self):
        """
        ProblemManagementPlugin.get_step_callback() Test plan:
            - if step_id not sent, respond with error
            - if bogus id and step doesn't exist, return error
            - put a step in the db, make sure values returned when called
        """
        good_id = self.test_subject.step_db.insert({
                    "step_text": "subtract",
                    "date_created": "3:40",
                    "edit_allowed_id": "2",
                    "skill_ids":{"subtract":"44"},
                    "skill_names":{"math":"subtract"}
            })
        msg = {"message_id":"1", "sender_entity_id":"2","step_id":good_id}
        
        msg["step_id"] = good_id
        self.test_subject.get_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                    "step_id": str(good_id),
                    "step_text": "subtract",
                    "date_created": "3:40",
                    "edit_allowed_id": "2",
                    "success":True,
                    "skill_ids":{"subtract":"44"},
                    "skill_names":{"math":"subtract"}
            })
        
    def test_get_step_callback_no_step_id(self):
        """
        ProblemManagementPlugin.get_step_callback() No Step Id:
        """
        msg = {"message_id":"1", "sender_entity_id":"2"}
        self.test_subject.get_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                    "error": "get_step requires a 'step_id'",
                    "success":False,
            })
        
    def test_get_step_callback_step_no_exist(self):
        """
        ProblemManagementPlugin.get_step_callback() Step Does Not Exist:
        """
        msg = {"message_id":"1", "sender_entity_id":"2","step_id":ObjectId()}
        self.test_subject.get_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                    "error": "Step does not exist.",
                    "success":False
            })

    def test_get_problem_steps_callback(self):
        """
        ProblemManagementPlugin.get_problem_steps_callback() Test plan:
            - if problem_id not sent, respond with an error
            - if bogus problem_id, respond with an error
            - insert 3 steps, two with problem_id, 1 without
            - two should be returned in response
        """
        bogus_id = ObjectId()
        good_id = self.test_subject.db.insert({
            "problem_name":"problem 1",
        })
        
        ids = self.test_subject.step_db.insert([
                {
                    "step_text":"subtract",
                    "date_created":"3:40",
                    "problem_id":good_id,
                    "edit_allowed_id":"2",
                    "skill_ids":{"subtract":"44"},
                    "skill_names":{"math":"subtract"}
                },
                {
                    "step_text":"subtract",
                    "date_created":"3:40",
                    "problem_id":good_id,
                    "edit_allowed_id":"2",
                    "skill_ids":{"subtract":"44"},
                    "skill_names":{"math":"subtract"}
                },
                {
                    "step_text":"subtract",
                    "date_created":"3:40",
                    "problem_id":bogus_id,
                    "edit_allowed_id":"2",
                    "skill_ids":{"multiplication":"44"},
                    "skill_names":{"math":"multiplication"}
                },
        ])
        
        msg = {"message_id":"1", "sender_entity_id":"2","problem_id":good_id}
        self.test_subject.get_problem_steps_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "steps": [
                    {
                        "step_id" : str(ids[0]),
                        "step_text": "subtract",
                        "date_created": "3:40",
                        "edit_allowed_id": "2",
                        "skill_ids":{"subtract":"44"},
                        "skill_names":{"math":"subtract"}
                    },
                    {
                        "step_id" : str(ids[1]),
                        "step_text": "subtract",
                        "date_created": "3:40",
                        "edit_allowed_id": "2",
                        "skill_ids":{"subtract":"44"},
                        "skill_names":{"math":"subtract"}
                    }
                ],
                "problem_id":str(good_id),
                "success":True,
        })
        
    def test_get_problem_steps_callback_no_problem_id(self):
        """
        ProblemManagementPlugin.get_problem_steps_callback() No Problem Id:
        """
        msg = {"message_id":"1", "sender_entity_id":"2"}
        self.test_subject.get_problem_steps_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error":"get_problem_callback requires a 'problem_id'",   
                "success":False
            })
        
    def test_get_problem_steps_callback_problem_no_exist(self):
        """
        ProblemManagementPlugin.get_problem_steps_callback() Problem Does Not Exist:
        """
        bogus_id = ObjectId()
        msg = {"message_id":"1", "sender_entity_id":"2","problem_id":bogus_id}
        self.test_subject.get_problem_steps_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error":"Problem with ID " + str(bogus_id) + " does not exist.",
                "success":False
            })
        
        
    def test_add_transaction_callback(self):     
        """
        ProblemManagementPlugin.add_transaction_callback() Test plan:
            - pass message without step_id or transaction text, should return error
            - pass bogus step id, should return error
            - if skill_ids and skill_namnes set, should use, else default to {}
            - if step doesn't exist, should reply with error
            - finally, success response sent when eb is filled with transaction
        """
        #no transaaction text or step id
        msg = {"message_id":"1","sender_entity_id":"2"}
        self.test_subject.add_transaction_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "error":"add_transaction requires a 'step_id', 'session_id','student_id' and 'transaction_text'",
                    "success":False     
        })
        
    def test_add_transaction_callback_no_transaction_text(self):
        """
        ProblemManagementPlugin.add_transaction_callback() No transaction Text:
        """
        bogus_id = ObjectId()
        msg = {"message_id":"1","sender_entity_id":"2","step_id":bogus_id}
        self.test_subject.add_transaction_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "error": "add_transaction requires a 'step_id', 'session_id','student_id' and 'transaction_text'",
            "success":False     
        })
    
    def test_add_transaction_callback_no_session_id(self):
        """
        ProblemManagementPlugin.add_transaction_callback() No session id:
        """
        bogus_id = ObjectId()
        msg = {"message_id":"1","sender_entity_id":"2","step_id":bogus_id,"transaction_text":"transaction"}
        self.test_subject.add_transaction_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "error": "add_transaction requires a 'step_id', 'session_id','student_id' and 'transaction_text'",
            "success":False     
        })
    
    def test_add_transaction_callback_no_student_id(self):
        """
        ProblemManagementPlugin.add_transaction_callback() No student_id:
        """
        bogus_id = ObjectId()
        msg = {"message_id":"1","sender_entity_id":"2","step_id":bogus_id,"transaction_text":"transaction","student_id":"456"}
        self.test_subject.add_transaction_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "error": "add_transaction requires a 'step_id', 'session_id','student_id' and 'transaction_text'",
            "success":False     
        })
    
    def test_add_transaction_callback_bad_step_id(self):
        """
        ProblemManagementPlugin.add_transaction_callback() Bad step_id:
        """
        msg = {"message_id":"1","sender_entity_id":"2","step_id":4,"transaction_text":"transaction"}
        self.test_subject.add_transaction_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "error": "The supplied 'step_id' is not a valid ObjectId.",
            "success":False     
        })
        
    def test_add_transaction_callback_step_no_exist(self):
        """
        ProblemManagementPlugin.add_transaction_callback() Step doesn't exist:
        """
        bogus_id = ObjectId()
        msg = {"message_id":"1","sender_entity_id":"2","step_id":bogus_id,"transaction_text":"transaction","student_id":"000","session_id":"999"}
        self.test_subject.add_transaction_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "error": "Error: either step with provided id doesn't exist, or you do not have permission to edit.",
            "success":False     
        })
        
    def test_add_transaction_callback_success(self):
        """
        ProblemManagementPlugin.add_transaction_callback() Success:
        """
        step_id = self.test_subject.step_db.insert({
                    "step_text":"subtract",
                    "date_created":"3:40",
                    "problem_id":"123",
                    "edit_allowed_id":"2",
                    "skill_ids":{"subtract":"44"},
                    "skill_names":{"math":"subtract"}
                })
        
        msg = {"message_id":"1","sender_entity_id":"2","step_id":step_id,"transaction_text":"transaction","student_id":"000","session_id":"999"}
        self.test_subject.add_transaction_callback(msg)
        
        new_transaction = self.test_subject.transaction_db.find_one({"step_id":step_id})
        new_transaction.should_not.equal(None)

        self.test_subject.send_response.assert_called_with("1", {
            "transaction_id": str(new_transaction["_id"]),
            "success": True,
        })
        self.test_subject.send_response.reset_mock()
        
        msg["skill_ids"] = {"skill":"skill_id"}
        msg["skill_names"] = {"skill_model":"skill_name"}
        self.test_subject.add_transaction_callback(msg)
        new_transaction = self.test_subject.transaction_db.find_one({"step_id":step_id,"skill_names":{"skill_model":"skill_name"},"skill_ids":{"skill":"skill_id"},"student_id":"000","session_id":"999"})
        new_transaction.should_not.equal(None)
        
        
    
    def test_remove_transaction_callback(self):
        """
        ProblemManagementPlugin.remove_transaction_callback() Test plan:
            - pass no transaction id, should throw error
            - pass invalid transaction id, should throw error
            - try a transaction Id that doesn't exist, should throw error
            - try a transaction that doesn't have our entity Id, should throw error
            - on success, make sure transaction gets removed
        """
        #no transaction id
        msg = {"message_id":"1", "sender_entity_id":"2"}
        self.test_subject.remove_transaction_callback(msg) 
        self.test_subject.send_response.assert_called_with("1",{
                "error": "remove_transaction requires 'transaction_id'",
                 "success":False
        })
        
    def test_remove_transaction_callback_invalid_id(self):
        """
        ProblemManagementPlugin.remove_transaction_callback() Invalid transaction ID:
        """
        msg = {"message_id":"1", "sender_entity_id":"2","transaction_id":4}
        self.test_subject.remove_transaction_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error": "The supplied 'transaction_id' is not a valid ObjectId.",
                 "success":False
        })
        
    def test_remove_transaction_callback_transaction_no_exist(self):
        """
        ProblemManagementPlugin.remove_transaction_callback() Transaction does not exist:
        """
        msg = {"message_id":"1", "sender_entity_id":"2","transaction_id":ObjectId()}
        self.test_subject.remove_transaction_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error": "Either the transaction doesn't exist or you don't have permission to remove it.",
                 "success":False
        })
        
    def test_remove_transaction_callback_bad_permission(self):
        """
        ProblemManagementPlugin.remove_transaction_callback() Bad permission:
        """
        new_transaction = self.test_subject.transaction_db.insert({
                    "transaction_text":"transaction",
                    "date_created":"3:40",
                    "step_id":"123",
                    "edit_allowed_id":"3",
                    "skill_ids":{"addition":"44"},
                    "skill_names":{"math":"addition"},
        })
        msg = {"message_id":"1", "sender_entity_id":"2","transaction_id":new_transaction}
        self.test_subject.remove_transaction_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error": "Either the transaction doesn't exist or you don't have permission to remove it.",
                 "success":False
        })
        
    def test_remove_transaction_callback_success(self):
        """
        ProblemManagementPlugin.remove_transaction_callback() Success:
        """
        new_transaction = self.test_subject.transaction_db.insert({
                    "transaction_text":"transaction",
                    "date_created":"3:40",
                    "step_id":"123",
                    "edit_allowed_id":"2",
                    "skill_ids":{"addition":"44"},
                    "skill_names":{"math":"addition"},
        })
        msg = {"message_id":"1", "sender_entity_id":"2","transaction_id":new_transaction}
        self.test_subject.remove_transaction_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "success":True,
                "exists":True,
        })
        
        self.test_subject.transaction_db.find({}).count().should.equal(0)
        
    def test_get_step_transactions_callback(self):
        """
        ProblemManagementPlugin.get_step_transactions_callback() Test plan:
            - if no step_id, then return error
            - if step id is invalid, return error
            - if no step, should reply with error
            - othwersise, should return transactions
        """
        #no step id
        msg = {"message_id":"1","sender_entity_id":"2"}
        self.test_subject.get_step_transactions_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "error":"get_step_transactions_callback requires a 'step_id'",   
            "success":False        
        })
        
    def test_get_step_transactions_callback_invalid_id(self):
        """
        ProblemManagementPlugin.get_step_transactions_callback() Invalid Id:
        """
        msg = {"message_id":"1","sender_entity_id":"2","step_id":4}
        self.test_subject.get_step_transactions_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "error":"The supplied 'step_id' is not a valid ObjectId.",
            "success":False        
        })
        
    def test_get_step_transactions_callback_no_step(self):
        """
        ProblemManagementPlugin.get_step_transactions_callback() No step:
        """
        bogus_id = ObjectId()
        msg = {"message_id":"1","sender_entity_id":"2","step_id":bogus_id}
        self.test_subject.get_step_transactions_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "error":"Step with ID " + str(bogus_id) + " does not exist.",
            "success":False        
        })
        
    def test_get_step_transactions_callback_success(self):
        """
        ProblemManagementPlugin.get_step_transactions_callback() Success:
        """
        
        sid = self.test_subject.step_db.insert({
                    "step_text":"subtract",
                    "date_created":"3:40",
                    "problem_id":"123",
                    "edit_allowed_id":"2",
                    "skill_ids":{"subtract":"44"},
                    "skill_names":{"math":"subtract"}
                })
        
        transaction_ids = self.test_subject.transaction_db.insert([
                 {
                    "transaction_text":"transaction",
                    "date_created":"3:40",
                    "step_id":sid,
                    "edit_allowed_id":"2",
                    "skill_ids":{"addition":"44"},
                    "skill_names":{"math":"addition"},
                },
                {
                    "transaction_text":"transaction",
                    "date_created":"3:40",
                    "step_id":sid,
                    "edit_allowed_id":"2",
                    "skill_ids":{"addition":"44"},
                    "skill_names":{"math":"addition"},
                }])
        
        msg = {"message_id":"1","sender_entity_id":"2","step_id":sid}
        self.test_subject.get_step_transactions_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "step_id":str(sid),
                "success":True,
                "transactions":[
                    {
                    "transaction_id":str(transaction_ids[0]),
                    "transaction_text":"transaction",
                    "date_created":"3:40",
                    "edit_allowed_id":"2",
                    "skill_ids":{"addition":"44"},
                    "skill_names":{"math":"addition"},
                },
                {
                    "transaction_id":str(transaction_ids[1]),
                    "transaction_text":"transaction",
                    "date_created":"3:40",
                    "edit_allowed_id":"2",
                    "skill_ids":{"addition":"44"},
                    "skill_names":{"math":"addition"},
                }]
        })
        
    def test_get_problem_by_skill(self):
        """
        ProblemManagementPlugin.get_problem_by_skill() Test Plan:
            -   send without skill name, should return with error
            -   send with skill name, should be empty
            -   and problems and steps, two with skill, 1 without, should return correct
        """
        msg = {"message_id":"1"}
        self.test_subject.get_problem_by_skill(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error":"problem_management get_problem_by_skill requires 'skill_name'"       
            })
        self.test_subject.send_response.reset_mock()
        
        msg["skill_name"] = "addition"
        self.test_subject.get_problem_by_skill(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "problems":{}      
            })
        self.test_subject.send_response.reset_mock()
        
        problem1 = self.test_subject.db.insert({"problem_name":"problem1","problem_text":"4+3"})
        problem1_step1 = self.test_subject.step_db.insert({"problem_id":problem1,"skill_ids":{"subtraction":"123"}})
        problem1_step2 = self.test_subject.step_db.insert({"problem_id":problem1,"skill_ids":{"addition":"456"}})    
        
        problem2 = self.test_subject.db.insert({"problem_name":"problem2","problem_text":"5+3"})
        problem2_step1 = self.test_subject.step_db.insert({"problem_id":problem2,"skill_ids":{"addition":"123"}})  
            
        problem3 = self.test_subject.db.insert({"problem_name":"problem1","problem_text":"6-3"})
        problem3_step1 = self.test_subject.step_db.insert({"problem_id":problem3,"skill_ids":{"subtraction":"123"}})
        problem3_step2 = self.test_subject.step_db.insert({"problem_id":problem3,"skill_ids":{"subtraction":"123"}})
        
        self.test_subject.get_problem_by_skill(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "problems":{
                    "problem1":str(problem1),
                    "problem2":str(problem2),
                }      
            })
        self.test_subject.send_response.reset_mock()
            
        
        
 
    def test_get_student_model_fragment_callback(self):
        """
        ProblemManagementPlugin.get_student_model_fragment_callback() Test plan:
            - mock send response
            - if not student_id, should respond with error
            - if nothing in db, shoudl respond with list 
            - otherwise, should have all the values that map student to problem
        """
        msg = {"message_id":"1","student_id":"2"}
        self.test_subject.worked_db.insert([      
            {"student_id":"2","problem_id":"123"},
            {"student_id":"2","problem_id":"456"},
            {"student_id":"3","problem_id":"123"},
        ])
        
        cur = self.test_subject.worked_db.find({
            "student_id": "2",       
        })
        problems = [p for p in cur]
        
        self.test_subject.get_student_model_fragment_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
              "name" : "problem_management",
              "fragment" : problems
        })
        
    def test_get_student_model_fragment_callback_no_student_id(self):
        """
        ProblemManagementPlugin.get_student_model_fragment_callback() No student Id:
        """
        msg = {"message_id":"1"}
        
        self.test_subject.get_student_model_fragment_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
              "error" : "problem_managment get_student_model_fragment requires 'student_id'" ,
        })
        
    def test_get_student_model_fragment_empty_set(self):
        """
        ProblemManagementPlugin.get_student_model_fragment_callback() Empty Set:
        """
        msg = {"message_id":"1","student_id":"2"}
        self.test_subject.get_student_model_fragment_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
              "name":"problem_management",
              "fragment": [],
        })
        
    def test_transaction_callback_method(self):
        """
        ProblemManagementPlugin.transaction_callback_method() Test plan:
            - send without parameters, should reply error
            - if skill ids not dict, should return error
            - if skill names not dict, should return error
            - with nothing in db, problem, step, and transaction should all be defaults
            - next time around, those ids should be returned again
        """
        
        self.test_subject.send_response = MagicMock()
        
        #no parameters
        msg = {"message_id":"1","sender_entity_id":"2","orig_sender_id":"3"}
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
             "error":"Problem Manager transactions require a problem_name, step_text, transaction_text, session_id, and student_id",
             "responder":"problem"   
        })
        self.test_subject.send_response.reset_mock()
        
        #problem name
        msg["problem_name"] = "problem1"
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
             "error":"Problem Manager transactions require a problem_name, step_text, transaction_text, session_id, and student_id",
             "responder":"problem"  
        })
        self.test_subject.send_response.reset_mock()
        
        #step_text
        msg["step_text"] = "step stuff"
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
             "error":"Problem Manager transactions require a problem_name, step_text, transaction_text, session_id, and student_id",
             "responder":"problem"  
        })
        self.test_subject.send_response.reset_mock()
        
        #transaction_text
        msg["transaction_text"] = "transaction stuff"
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
             "error":"Problem Manager transactions require a problem_name, step_text, transaction_text, session_id, and student_id",
             "responder":"problem"  
        })
        self.test_subject.send_response.reset_mock()
        
        #session
        msg["session_id"] = "456"
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
             "error":"Problem Manager transactions require a problem_name, step_text, transaction_text, session_id, and student_id",
             "responder":"problem"   
        })
        self.test_subject.send_response.reset_mock()
        
        
        #student_id
        msg["student_id"] = "123"
        self.test_subject.transaction_callback_method(msg)
        
        transaction = self.test_subject.transaction_db.find_one({"transaction_text":"transaction stuff"})
        step = self.test_subject.step_db.find_one({"step_text":"step stuff"})
        problem = self.test_subject.db.find_one({"problem_name":"problem1"})

        self.test_subject.send_response.assert_called_with("1",{
            "transaction_id": str(transaction["_id"]),
            "step_id": str(step["_id"]),
            "problem_id":str(problem["_id"]),
            "responder" : "problem" 
        })
        self.test_subject.send_response.reset_mock()
        
        #try again
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "transaction_id": str(transaction["_id"]),
            "step_id": str(step["_id"]),
            "problem_id":str(problem["_id"]),
            "responder" : "problem" 
        })
        self.test_subject.send_response.reset_mock()
        
        
        
        
        
       
