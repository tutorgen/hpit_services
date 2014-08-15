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
        self.test_subject.step_db = self.test_subject.mongo.test_hpit.hpit_steps
        
    def tearDown(self):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        client = MongoClient()
        client.drop_database("test_hpit")
        
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
        pmp = ProblemManagementPlugin(123,456,None)
        pmp.logger.should.equal(None)
        isinstance(pmp.mongo,MongoClient).should.equal(True)
        isinstance(pmp.db,Collection).should.equal(True)
        pmp.db.full_name.should.equal("hpit.hpit_problems")
        isinstance(pmp.step_db,Collection).should.equal(True)
        pmp.step_db.full_name.should.equal("hpit.hpit_steps")
        
    def test_add_problem_callback(self):
        """
        ProblemManagementPlugin.add_problem_callback() Test plan:
            - send in message w/o problem name or text, response should have error
            - send in valid stuff, make sure response contains proper values, record in db
            - send in same stuff, make sure that an error response is found
        """
        self.test_subject.send_response = MagicMock()
        
        msg = {"message_id":"1", "sender_entity_id":"2"}
        self.test_subject.add_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {"error":"Add problem requires 'problem_name' and 'problem_text'","success":False})
        self.test_subject.send_response.reset_mock()
        
        msg["problem_name"] = "problem 1"
        self.test_subject.add_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {"error":"Add problem requires 'problem_name' and 'problem_text'","success":False})
        self.test_subject.send_response.reset_mock()
        
        msg["problem_text"] = "123"
        self.test_subject.add_problem_callback(msg)
        
        problem_id = self.test_subject.db.find_one({})["_id"]
        problem_id.should_not.equal(None)
        
        self.test_subject.send_response.assert_called_with("1", {
                'problem_name': "problem 1",
                'problem_text': "123",
                'success': True,
                'problem_id':str(problem_id)
            })
        self.test_subject.send_response.reset_mock()
        
        self.test_subject.add_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "error": "This problem already exists.  Try cloning the 'problem_id' sent in this response.",
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
        self.test_subject.send_response = MagicMock()
        
        msg = {"message_id":"1","sender_entity_id":"2"}
        self.test_subject.remove_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error":"remove_problem requires 'problem_id'",
                "success":False,
        })
        self.test_subject.send_response.reset_mock()
        
        msg["problem_id"] = ObjectId()
        self.test_subject.remove_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error": "Could not delete problem; it does not exist",
                'problem_id': str(msg["problem_id"]),
                'exists': False,
                'success': False
            })
        self.test_subject.send_response.reset_mock()
        
        problem_id = self.test_subject.db.insert({
                "problem_name":"problem 1",
                "problem_text": "123",
                "date_created": "3:40",
                "edit_allowed_id":"2"
         })
        msg["problem_id"] = problem_id
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
            
    def test_get_problem_callback(self):
        """
        ProblemManagementPlugin.get_problem_callback() Test plan:
            - send message without problem id, should return error response
            - send in bogus id, should return error response
            - send in id of existing, should return valid response
        """
        self.test_subject.send_response = MagicMock()
        
        msg = {"message_id":"1","sender_entity_id":"2"}
        self.test_subject.get_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error":"get_problem requires a 'problem_id'",
                "success":False,
        })
        self.test_subject.send_response.reset_mock()
        
        bogus_id = ObjectId()
        msg["problem_id"] = bogus_id
        self.test_subject.get_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                'error': "Error:  problem with id" + str(bogus_id) + " does not exist.",
                'exists': False,
                'success': False
            })
        self.test_subject.send_response.reset_mock()
        
        good_id = self.test_subject.db.insert({
                "problem_name":"problem 1",
                "problem_text":"123",
                "date_created":"3:40",
                "edit_allowed_id":"2",
        })
        msg["problem_id"] = str(good_id)
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
        self.test_subject.send_response = MagicMock()
        
        msg = {"message_id":"1","sender_entity_id":"2"}
        self.test_subject.edit_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
            "error":"edit_problem requires 'problem_id' and 'fields'",
            "success":False      
        })
        msg["problem_id"] = ObjectId()
        self.test_subject.edit_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
            "error":"edit_problem requires 'problem_id' and 'fields'",
            "success":False      
        })
        
        msg["fields"] = {"bogus1":"value","bogus2":"value"}
        self.test_subject.edit_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
            "error": "Error: either problem with provided id doesn't exist, or you do not have permission to edit.",
            "success":False,
        })
        
        good_id = self.test_subject.db.insert({
                "edit_allowed_id":"2",
                "problem_name":"problem 1",
                "problem_text": "123",
                "date_created":"3:40",
        })
        
        bad_id = self.test_subject.db.insert({
                "edit_allowed_id":"3",
                "problem_name":"problem 2",
                "problem_text": "456",
                "date_created":"3:40",
        })
        
        msg["problem_id"] = str(bad_id)
        self.test_subject.edit_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
            "error": "Error: either problem with provided id doesn't exist, or you do not have permission to edit.",
            "success":False,
        })
        
        msg["problem_id"] = str(good_id)
        msg["fields"] = 4
        self.test_subject.edit_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "error":"Fields needs to be a dict.",
                "success":False
        })
        
        msg["fields"] = {"bogus1":"value","bogus2":"value"}
        self.test_subject.edit_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                'problem_name': "problem 1",
                'problem_text': "123",
                'date_created': "3:40",
                'edit_allowed_id' : "2",
                'success': True
            })
        
        msg["fields"] = {"problem_name":"new problem 1","bogus2":"value"}
        self.test_subject.edit_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                'problem_name': "new problem 1",
                'problem_text': "123",
                'date_created': "3:40",
                'edit_allowed_id' : "2",
                'success': True
            })
        
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
        
    def test_list_problems_callback(self):
        """
        ProblemManagementPlugin.list_problems_callback() Test plan:
            - if problems empty, response should be empty
            - else, response added should be present
        """
        self.test_subject.send_response = MagicMock()
        msg = {"message_id":"1"}
        
        self.test_subject.list_problems_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "problems":[],
                "success":True,
        })
        self.test_subject.send_response.reset_mock()
     
        
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
        self.test_subject.send_response.reset_mock()
        
    def test_clone_problem_callback(self):
        """
        ProblemManagementPlugin.clone_problem_callback() Test plan:
            - send message without problem_id, should respond with error
            - if bogus id passed, should respond with error
            - ensure new problem added with same fields, sender entity id matching caller
            - make sure steps copied properly
            - response should be correct
        """
        self.test_subject.send_response = MagicMock()
        
        msg = {"message_id":"1","sender_entity_id":"2"}
        self.test_subject.clone_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                    "error": "clone_problem requires a 'problem_id'.",
                    "success":False,
            })
        self.test_subject.send_response.reset_mock()
        
        bogus_id = ObjectId()
        msg["problem_id"] = bogus_id
        self.test_subject.clone_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                    "error": "Problem with id " + str(bogus_id) + " does not exist.",
                    "success":False
            })
        self.test_subject.send_response.reset_mock()
        
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
                    "allowed_edit_id":"3",
                },
                {
                    "step_text":"subtract",
                    "date_created":"3:40",
                    "problem_id":good_id,
                    "allowed_edit_id":"3",
                },
                {
                    "step_text":"subtract",
                    "date_created":"3:40",
                    "problem_id":bogus_id,
                    "allowed_edit_id":"4",
                },
        ])
        
        msg["problem_id"] = str(good_id)
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
                "allowed_edit_id":"2", 
        })
        
        new_added_ids.count().should.equal(2)
        
        self.test_subject.send_response.assert_called_with("1", {
                "problem_id": str(new_added_problem["_id"]),
                "step_ids": [str(s["_id"]) for s in new_added_ids],
                "success": True
        })
 
    def test_add_step_callback(self):
        """
        ProblemManagementPlugin.add_step_callback() Test plan:
            - send in message without problem id and step text, should return error
            - send in bogus id, bogus entity_id, should each return error
            - make sure step_text, allowed_entity_id, and problem_id all set
            - response should contain step id and success
        """
        self.test_subject.send_response = MagicMock()
        
        msg = {"message_id":"1", "sender_entity_id":"2"}
        self.test_subject.add_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
               "error": "add_step requires a 'problem_id' and 'step_text'",
               "success":False,
        })
        self.test_subject.send_response.reset_mock()
        
        msg["step_text"] = "subtract"
        self.test_subject.add_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
               "error": "add_step requires a 'problem_id' and 'step_text'",
               "success":False
        })
        self.test_subject.send_response.reset_mock()
        
        msg["problem_id"] = ObjectId()
        self.test_subject.add_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error": "Error: either problem with provided id doesn't exist, or you do not have permission to edit.",
                "success":False,
        })
        self.test_subject.send_response.reset_mock()
        
        msg["sender_entity_id"] = "3"
        good_id = self.test_subject.db.insert({
                "allowed_edit_id":"2",
        })
        msg["problem_id"] = good_id
        self.test_subject.add_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error": "Error: either problem with provided id doesn't exist, or you do not have permission to edit.",
                "success":False,
        })
        self.test_subject.send_response.reset_mock()
        
        msg["sender_entity_id"] = "2"
        self.test_subject.add_step_callback(msg)
        
        step = self.test_subject.step_db.find_one({"step_text":"subtract"})
        step.should_not.equal(None)
        
        self.test_subject.send_response.assert_called_with("1",{
                    "step_id":str(step["_id"]),
                    "success":True,
            })
        self.test_subject.send_response.reset_mock()

    def test_remove_step_callback(self):
        """
        ProblemManagmentPlugin.remove_step_callback() Test plan:
            - send message without step_id, should send error response
            - send in bogus entity_id and step_id, should each return error response
            - if nothing in db, error response should be called
            - make sure proper response is removed, record removed on good call
        """
        self.test_subject.send_response = MagicMock()
        
        msg = {"message_id":"1", "sender_entity_id":"2"}
        self.test_subject.remove_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
               "error": "remove_step requires 'step_id'",
               "success":False,
        })
        self.test_subject.send_response.reset_mock()
        
        
        msg["step_id"] = ObjectId()
        self.test_subject.remove_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error": "Either the step doesn't exist or you don't have permission to remove it.",
                "success":False,
        })
        self.test_subject.send_response.reset_mock()
                
        good_id = self.test_subject.step_db.insert({
                "allowed_edit_id":"2",
        })
        msg["step_id"] = ObjectId()
        self.test_subject.remove_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error": "Either the step doesn't exist or you don't have permission to remove it.",
                "success":False,
        })
        self.test_subject.send_response.reset_mock()
        msg["sender_entity_id"] = "3"
        msg["step_id"] = good_id
        self.test_subject.remove_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error": "Either the step doesn't exist or you don't have permission to remove it.",
                "success":False,
        })
        self.test_subject.send_response.reset_mock()
        
        msg["sender_entity_id"] = "2"
        self.test_subject.remove_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                    "success":True,
                    "exists":True,
            })
        self.test_subject.step_db.find({}).count().should.equal(0)
       
    def test_get_step_callback(self):
        """
        ProblemManagementPlugin.get_step_callback() Test plan:
            - if step_id not sent, respond with error
            - if bogus id and step doesn't exist, return error
            - put a step in the db, make sure values returned when called
        """
        self.test_subject.send_response = MagicMock()
        
        msg = {"message_id":"1", "sender_entity_id":"2"}
        self.test_subject.get_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                    "error": "get_step requires a 'step_id'",
                    "success":False,
            })
        self.test_subject.send_response.reset_mock()
        
        msg["step_id"] = ObjectId()
        self.test_subject.get_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                    "error": "Step does not exist.",
                    "success":False
            })
        self.test_subject.send_response.reset_mock()
        
        good_id = self.test_subject.step_db.insert({
                    "step_text": "subtract",
                    "date_created": "3:40",
                    "allowed_edit_id": "2",
            })
        
        self.test_subject.get_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                    "error": "Step does not exist.",
                    "success":False
            })
        self.test_subject.send_response.reset_mock()
        
        msg["step_id"] = good_id
        self.test_subject.get_step_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                    "step_id": str(good_id),
                    "step_text": "subtract",
                    "date_created": "3:40",
                    "allowed_edit_id": "2",
                    "success":True,
            })

    def test_get_problem_steps_callback(self):
        """
        ProblemManagementPlugin.get_problem_steps_callback() Test plan:
            - if problem_id not sent, respond with an error
            - if bogus problem_id, respond with an error
            - insert 3 steps, two with problem_id, 1 without
            - two should be returned in response
        """
        self.test_subject.send_response = MagicMock()
        
        msg = {"message_id":"1", "sender_entity_id":"2"}
        self.test_subject.get_problem_steps_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error":"get_problem_callback requires a 'problem_id'",   
                "success":False
            })
        self.test_subject.send_response.reset_mock()
        
        bogus_id = ObjectId()
        msg["problem_id"] = bogus_id
        self.test_subject.get_problem_steps_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error":"Problem with ID " + str(bogus_id) + " does not exist.",
                "success":False
            })
        self.test_subject.send_response.reset_mock()
        
        good_id = self.test_subject.db.insert({
            "problem_name":"problem 1",
        })
        
        ids = self.test_subject.step_db.insert([
                {
                    "step_text":"subtract",
                    "date_created":"3:40",
                    "problem_id":good_id,
                    "allowed_edit_id":"2",
                },
                {
                    "step_text":"subtract",
                    "date_created":"3:40",
                    "problem_id":good_id,
                    "allowed_edit_id":"2",
                },
                {
                    "step_text":"subtract",
                    "date_created":"3:40",
                    "problem_id":bogus_id,
                    "allowed_edit_id":"2",
                },
        ])
        
        msg["problem_id"] = good_id
        self.test_subject.get_problem_steps_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "steps": [
                    {
                        "step_id" : str(ids[0]),
                        "step_text": "subtract",
                        "date_created": "3:40",
                        "allowed_edit_id": "2",
                    },
                    {
                        "step_id" : str(ids[1]),
                        "step_text": "subtract",
                        "date_created": "3:40",
                        "allowed_edit_id": "2",
                    }
                ],
                "problem_id":str(good_id),
                "success":True,
        })
