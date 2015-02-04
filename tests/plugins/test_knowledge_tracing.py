import unittest
from mock import *
from pymongo import MongoClient
from pymongo.collection import Collection
from bson.objectid import ObjectId

from hpit.plugins import KnowledgeTracingPlugin

from hpit.management.settings_manager import SettingsManager
settings = SettingsManager.get_plugin_settings()

import shlex
import json

import nose

class TestKnowledgeTracingPlugin(unittest.TestCase):

    def setUp(self):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.test_subject = KnowledgeTracingPlugin(123,456,None,shlex.quote(json.dumps({
                "shared_messages": {
                    "get_student_model_fragment": [
                        "88bb246d-7347-4f57-8cbe-95944a4e0027"
                    ]
                }
            })))
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
        KnowledgeTracingPlugin.__init__() Test plan:
            - make sure logger set right
            - make sure self.mongo is a mongo client
            - make sure db is a collection
            -check full name
        """
        ds = KnowledgeTracingPlugin(1234,5678,None,shlex.quote(json.dumps({
                "shared_messages": {
                    "get_student_model_fragment": [
                        "88bb246d-7347-4f57-8cbe-95944a4e0027"
                    ]
                }
            })))
        ds.logger.should.equal(None)
        isinstance(ds.mongo,MongoClient).should.equal(True)
        isinstance(ds.db,Collection).should.equal(True)
        ds.db.full_name.should.equal("hpit_unit_test_db.hpit_knowledge_tracing")
        
    def test_kt_trace_no_params(self):
        """
        KnowledgeTracingPlugin.kt_trace() Test plan:
            - mock out send response
            - send without each of the required parameters, response should be error
            - send in bogus kt_config values, should send error response
            - set a kt_config with values, send in new message
            - make sure new p_known is updated in db
            - make sure new p_known is returned in response
        """
        msg = {"message_id":"2","sender_entity_id":"3"}
        self.test_subject.kt_trace(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_trace requires 'sender_entity_id', 'skill_id', 'student_id' and 'correct'"})
    
    def test_kt_trace_invalid_skill_id(self):
        """
        KnowledgeTracingPlugin.kt_trace() Invalid Skill Id:
        """
        msg = {"message_id":"2","sender_entity_id":"3","skill_id":"add"}
        self.test_subject.kt_trace(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_trace 'skill_id' is not a valid skill id"})
        
    def test_kt_trace_no_correct(self):
        """
        KnowledgeTracingPlugin.kt_trace() No Correct Parameter:
        """
        msg = {"message_id":"2","sender_entity_id":"3","skill_id":str(ObjectId())}
        self.test_subject.kt_trace(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_trace requires 'sender_entity_id', 'skill_id', 'student_id' and 'correct'"})
    
    def test_kt_trace_no_student_id(self):
        """
        KnowledgeTracingPlugin.kt_trace() Student Id Missing:
        """
        msg = {"message_id":"2","sender_entity_id":"3","skill_id":str(ObjectId()),"correct":True}
        self.test_subject.kt_trace(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_trace requires 'sender_entity_id', 'skill_id', 'student_id' and 'correct'"})
        
    def test_kt_trace_no_initial_settings(self):
        """
        KnowledgeTracingPlugin.kt_trace() No settings in db:
        """
        skill_id = str(ObjectId())
        msg = {"message_id":"2","sender_entity_id":"3","skill_id":skill_id,"correct":True,"student_id":"4"}
        msg["probability_known"] = .7
        msg["probability_learned"] = .2
        msg["probability_guess"] = .3
        msg["probability_mistake"] = .4
        self.test_subject.kt_trace(msg)
        self.test_subject.send_response.assert_called_once_with("2", {
            'probability_guess': 0.5, 
            'probability_known': 0.75, 
            'probability_learned': 0.5, 
            'probability_mistake': 0.5, 
            'skill_id': skill_id, 
            'student_id': '4'
        })


    def test_kt_trace_correct_true(self): 
        """
        KnowledgeTracingPlugin.kt_trace() Correct true:
        """
        skill_id = str(ObjectId())
        msg = {"message_id":"2","sender_entity_id":"3","skill_id":skill_id,"correct":True,"student_id":"4"}
        insert_doc = dict(msg)
        insert_doc["probability_known"] = .7
        insert_doc["probability_learned"] = .2
        insert_doc["probability_guess"] = .3
        insert_doc["probability_mistake"] = .4
        self.test_subject.db.insert(insert_doc)
        
        self.test_subject.kt_trace(msg)
        #with correct  = true and these variables, p_known should be 
        expected_value = (.42 / .51) + ( (1 - (.42 / .51)) * .2)
        self.test_subject.send_response.called.should.equal(True) #can't check params because of float precision
        thing  = self.test_subject.db.find_one({'sender_entity_id':"3",'student_id':"4","skill_id":str(skill_id)})
        nose.tools.assert_almost_equal(thing["probability_known"],expected_value,places=5)

     
    def test_kt_trace_correct_false(self):
        """
        KnowledgeTracingPlugin.kt_trace() Correct false:
        """
        skill_id = str(ObjectId())
        msg = {"message_id":"2","sender_entity_id":"3","skill_id":skill_id,"correct":False,"student_id":"4"}
        insert_doc = dict(msg)
        insert_doc["probability_known"] = .7
        insert_doc["probability_learned"] = .2
        insert_doc["probability_guess"] = .3
        insert_doc["probability_mistake"] = .4
        self.test_subject.db.insert(insert_doc)
        
        self.test_subject.kt_trace(msg)
        #with correct  = false and these variables, p_known should be 
        expected_value = (.28 / .49) + ( (1 - (.28 / .49)) * .2)
        self.test_subject.send_response.called.should.equal(True)
        thing  = self.test_subject.db.find_one({'sender_entity_id':"3",'student_id':"4","skill_id":str(skill_id)})
        nose.tools.assert_almost_equal(thing["probability_known"],expected_value,places=5)
        
        
    def test_kt_set_initial_no_sender_entity_id(self):
        """
        KnowledgeTracingPlugin.kt_set_initial_callback() Test plan:
            - mock out send response
            - send without each of the required parameters, response should be error
            - send message for non existant kt_config, should insert a new one
            - send message for existing kt_config, should update that one
            - response should always echo parameters sent in
        """
        msg = {"message_id":"2"}
        self.test_subject.kt_set_initial_callback(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_set_initial requires 'sender_entity_id', 'skill_id', 'probability_known', 'probability_learned', 'probability_guess', 'probability_mistake', and 'student_id'"})
    
    def test_kt_set_initial_no_skill_id(self):
        """
        KnowledgeTracingPlugin.kt_set_initial_callback() No Skill ID:
        """
        msg = {"message_id":"2","sender_entity_id":"3"}
        self.test_subject.kt_set_initial_callback(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_set_initial requires 'sender_entity_id', 'skill_id', 'probability_known', 'probability_learned', 'probability_guess', 'probability_mistake', and 'student_id'"})
    
    def test_kt_set_initial_invalid_skill_id(self):
        """
        KnowledgeTracingPlugin.kt_set_initial_callback() Invalid Skill ID:
        """        
        msg = {"message_id":"2","sender_entity_id":"3","skill_id":"add"}
        self.test_subject.kt_set_initial_callback(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_trace 'skill_id' is not a valid skill id"})
    
    def test_kt_set_initial_no_probability_known(self):
        """
        KnowledgeTracingPlugin.kt_set_initial_callback() No Skill ID:
        """
        msg = {"message_id":"2","sender_entity_id":"3","skill_id":"add","skill_id":str(ObjectId())}
        self.test_subject.kt_set_initial_callback(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_set_initial requires 'sender_entity_id', 'skill_id', 'probability_known', 'probability_learned', 'probability_guess', 'probability_mistake', and 'student_id'"})
    
    def test_kt_set_initial_no_probability_leraned(self):
        """
        KnowledgeTracingPlugin.kt_set_initial_callback() No Probability Learned:
        """
        msg = {"message_id":"2","sender_entity_id":"3","skill_id":"add","skill_id":str(ObjectId())}
        msg["probability_known"] = "1.1"
        self.test_subject.kt_set_initial_callback(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_set_initial requires 'sender_entity_id', 'skill_id', 'probability_known', 'probability_learned', 'probability_guess', 'probability_mistake', and 'student_id'"})
    
    def test_kt_set_initial_no_probability_guess(self):
        """
        KnowledgeTracingPlugin.kt_set_initial_callback() No Probabilty Guess:
        """
        msg = {"message_id":"2","sender_entity_id":"3","skill_id":"add","skill_id":str(ObjectId())}
        msg["probability_known"] = "1.1"
        msg["probability_learned"] = "1.2"
        self.test_subject.kt_set_initial_callback(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_set_initial requires 'sender_entity_id', 'skill_id', 'probability_known', 'probability_learned', 'probability_guess', 'probability_mistake', and 'student_id'"})
    
    def test_kt_set_intiial_no_probablity_mistake(self):
        """
        KnowledgeTracingPlugin.kt_set_initial_callback() No probability Mistake:
        """
        msg = {"message_id":"2","sender_entity_id":"3","skill_id":"add","skill_id":str(ObjectId())}
        msg["probability_known"] = "1.1"
        msg["probability_learned"] = "1.2"
        msg["probability_guess"] = "1.3"
        self.test_subject.kt_set_initial_callback(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_set_initial requires 'sender_entity_id', 'skill_id', 'probability_known', 'probability_learned', 'probability_guess', 'probability_mistake', and 'student_id'"})
    
    def test_kt_set_intitial_no_student_id(self):
        """
        KnowledgeTracingPlugin.kt_set_initial_callback() No Student ID:
        """
        msg = {"message_id":"2","sender_entity_id":"3","skill_id":"add","skill_id":str(ObjectId())}
        msg["probability_known"] = "1.1"
        msg["probability_learned"] = "1.2"
        msg["probability_guess"] = "1.3"
        msg["probability_mistake"] = "1.4"
        self.test_subject.kt_set_initial_callback(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_set_initial requires 'sender_entity_id', 'skill_id', 'probability_known', 'probability_learned', 'probability_guess', 'probability_mistake', and 'student_id'"})
        self.test_subject.send_response.reset_mock()
    
    def test_kt_set_initial_bad_skill_id(self):
        """
        KnowledgeTracingPlugin.kt_set_initial_callback() Bad Skill ID:
        """
        skill_id = str(ObjectId())
        msg = {"message_id":"2","sender_entity_id":"3","skill_id":"add","skill_id":skill_id,"student_id":"4"}
        msg["probability_known"] = "1.1"
        msg["probability_learned"] = "1.2"
        msg["probability_guess"] = "1.3"
        msg["probability_mistake"] = "1.4"
        
        def send_mock_error(message_name,payload,callback):
            callback({"error":"there was an error"})
            
        self.test_subject.send = MagicMock(side_effect=send_mock_error)
        self.test_subject.kt_set_initial_callback(msg)
        self.test_subject.send.call_count.should.equal(1)
        self.test_subject.send_response.assert_called_once_with("2",{
            "error":"skill_id " + str(skill_id) + " is invalid.",
            "skill_manager_error":"there was an error",
            })


    def test_kt_set_initial_good_skill_id(self):
        """
        KnowledgeTracingPlugin.kt_set_initial_callback() Good Skill ID:
        """
        skill_id = str(ObjectId())
        msg = {"message_id":"2","sender_entity_id":"3","skill_id":"add","skill_id":skill_id,"student_id":"4"}
        msg["probability_known"] = "1.1"
        msg["probability_learned"] = "1.2"
        msg["probability_guess"] = "1.3"
        msg["probability_mistake"] = "1.4"
        
        def send_mock_clean(message_name,payload,callback):
            callback({})
        
        self.test_subject.send = MagicMock(side_effect=send_mock_clean)
        self.test_subject.kt_set_initial_callback(msg)
        self.test_subject.send.call_count.should.equal(1)
        self.test_subject.send_response.assert_called_once_with("2",{
            'skill_id': str(skill_id),
            'probability_known': "1.1",
            'probability_learned': "1.2",
            'probability_guess': "1.3",
            'probability_mistake':"1.4",
            'student_id':"4"
            })
        self.test_subject.db.find().count().should.equal(1)
        

    def test_kt_set_initial_overwrite_data(self):
        """
        KnowledgeTracingPlugin.kt_set_initial_callback() Overwrite data:
        """
        skill_id = str(ObjectId())
        msg = {"message_id":"2","sender_entity_id":"3","skill_id":"add","skill_id":skill_id,"student_id":"4"}
        msg["probability_known"] = "1.1"
        msg["probability_learned"] = "1.2"
        msg["probability_guess"] = "1.3"
        msg["probability_mistake"] = "1.4"
        
        def send_mock_clean(message_name,payload,callback):
            callback({})
        
        self.test_subject.send = MagicMock(side_effect=send_mock_clean)
        
        self.test_subject.db.insert(dict(msg))
        
        msg["probability_known"] = "2.1"
        msg["probability_learned"] = "2.2"
        msg["probability_guess"] = "2.3"
        msg["probability_mistake"] = "2.4"
        self.test_subject.kt_set_initial_callback(msg)
        self.test_subject.send_response.assert_called_once_with("2",{
            'skill_id': str(skill_id),
            'probability_known': "2.1",
            'probability_learned': "2.2",
            'probability_guess': "2.3",
            'probability_mistake':"2.4",
            'student_id':"4"
            })
        thing = self.test_subject.db.find_one({"sender_entity_id":"3","skill_id":str(skill_id),"student_id":"4"})
        thing["probability_known"].should.equal("2.1")
        thing["probability_learned"].should.equal("2.2")
        thing["probability_guess"].should.equal("2.3")
        thing["probability_mistake"].should.equal("2.4")
    
    def test_kt_reset(self):
        """
        KnowledgeTracingPlugin.kt_reset() Test plan:
            - mock out send response
            - send without entity_id, skill, or student_id. should have error response
            - send with bogus info, should still return response with everything 0
            - put a kt_config in the db, with non zero values
            - response should be sent, db should have zeroed out values
        """
    def test_kt_reset_no_skill_id(self):
        """
        KnowledgeTracingPlugin.kt_reset() No Skill Id:
        """
        msg = {"message_id":"2","sender_entity_id":"3"}
        self.test_subject.kt_reset(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_reset requires 'sender_entity_id', 'skill_id', and 'student_id'"})
       
    def test_kt_reset_invalid_skill_id(self):
        """
        KnowledgeTracingPlugin.kt_reset() Invalid Id:
        """
        msg = {"message_id":"2","sender_entity_id":"3","skill_id":"add"}
        self.test_subject.kt_reset(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_trace 'skill_id' is not a valid skill id"})
    
    def test_kt_reset_no_student_id(self):
        """
        KnowledgeTracingPlugin.kt_reset() No Student Id:
        """
        msg = {"message_id":"2","sender_entity_id":"3","skill_id":"add","skill_id":str(ObjectId())}
        self.test_subject.kt_reset(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_reset requires 'sender_entity_id', 'skill_id', and 'student_id'"})
        
    def test_kt_reset_no_data(self):
        """
        KnowledgeTracingPlugin.kt_reset() No kt_config:
        """
        skill_id = str(ObjectId())
        msg = {"message_id":"2","sender_entity_id":"3","skill_id":"add","skill_id":skill_id,"student_id":"4"}
        
        self.test_subject.kt_reset(msg)
        self.test_subject.send_response.assert_called_once_with("2", {
            'error': 'No configuration found in knowledge tracer for skill/student combination.'
        })
        
    def test_kt_reset_data_present(self):
        """
        KnowledgeTracingPlugin.kt_reset() kt_config Exists:
        """
        skill_id = str(ObjectId())
        msg = {"message_id":"2","sender_entity_id":"3","skill_id":"add","skill_id":skill_id,"student_id":"4"}

        oid = self.test_subject.db.insert({"sender_entity_id":"3","skill_id":str(skill_id),"student_id":"4"})
        self.test_subject.kt_reset(msg)
        self.test_subject.send_response.assert_called_once_with("2",{
            'skill_id': str(skill_id),
            'probability_known': 0.5,
            'probability_learned': 0.5,
            'probability_guess': 0.5,
            'probability_mistake': 0.5,
            'student_id':"4"
        })
        
        ob = self.test_subject.db.find_one({"_id":oid})
        ob["probability_known"].should.equal(0.5)
        ob["probability_learned"].should.equal(0.5)
        ob["probability_guess"].should.equal(0.5)
        ob["probability_mistake"].should.equal(0.5)
        
        
    def test_get_student_model_fragment_no_student_id(self):
        """
        KnowledgeTracingPlugin.get_student_model_fragment() Test plan:
            - if nothing in db, response should have empty list
            - add some skills to db, make sure exist in list.
        """
        
        msg = {"message_id":"1","sender_entity_id":"2"}
        
        self.test_subject.get_student_model_fragment(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "error":"knowledge tracing get_student_model_fragment requires 'student_id'",
            })
        
        
    def test_get_student_model_fragment_empty_db(self):
        """
        KnowledgeTracingPlugin.get_student_model_fragment() Empty DB:
        """ 
        msg = {"message_id":"1","sender_entity_id":"2","student_id":"3"}
        self.test_subject.get_student_model_fragment(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "name":"knowledge_tracing",
            "fragment":[],
        })
        
    def test_get_student_model_fragment_full_db(self):
        """
        KnowledgeTracingPlugin.get_student_model_fragment() Non Empty DB:
        """ 
        msg = {"message_id":"1","sender_entity_id":"2","student_id":"123"}
        self.test_subject.db.insert([
            {
                'sender_entity_id': "2",
                'skill_id': "567",
                'probability_known': 1,
                'probability_learned': 1,
                'probability_guess': 0,
                'probability_mistake': 0,
                'student_id': "123",
            },
            {
                'sender_entity_id': "2",
                'skill_id': "8910",
                'probability_known': 0,
                'probability_learned': 0,
                'probability_guess': 1,
                'probability_mistake': 1,
                'student_id': "123",
            },
            {
                'sender_entity_id': "2",
                'skill_id': "8910",
                'probability_known': 0,
                'probability_learned': 0,
                'probability_guess': 1,
                'probability_mistake': 1,
                'student_id': "333",
            },
        ])
        
        #should return values 1 and 2 from above
        self.test_subject.get_student_model_fragment(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "name":"knowledge_tracing",
            "fragment":[{
                'skill_id': "567",
                'probability_known': 1,
                'probability_learned': 1,
                'probability_guess': 0,
                'probability_mistake': 0,
                'student_id': "123",
                },
                {
                'skill_id': "8910",
                'probability_known': 0,
                'probability_learned': 0,
                'probability_guess': 1,
                'probability_mistake': 1,
                'student_id': "123",
                }
            ],
        })
        
    def test_transaction_callback_method(self):
        """
        KnowledgeTracingPlugin.transaction_callback_method() Test plan:
            - try without skill_ids, student_id, and correct, should reply with error
            - try with skill_ids not dict, should reply with error
            - first pass, all skills should be set to .75, ensure called with those values
            - next pass, all skill should be close to the expected values
        """
        def mock_send(message_name,payload,callback):
            callback({"responder":["downstream"]})
                
        self.test_subject.send = MagicMock(side_effect = mock_send)
        self.test_subject.send_response = MagicMock()
        
        #no args
        msg = {"message_id":"1","sender_entity_id":"2","orig_sender_id":"2"}
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
             "error":"knowledge tracing not done because 'skill_ids', 'student_id', or 'outcome' not found.",
             "responder":"kt",   
        })
        self.test_subject.send_response.reset_mock()
               
        #just outcome
        msg["outcome"] = "correct"
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
             "error":"knowledge tracing not done because 'skill_ids', 'student_id', or 'outcome' not found.",
             "responder":"kt"  
        })
        self.test_subject.send_response.reset_mock()
        
        #no skill_ids
        msg["student_id"] = "123"
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
             "error":"knowledge tracing not done because 'skill_ids', 'student_id', or 'outcome' not found.",
             "responder":"kt"    
        })
        self.test_subject.send_response.reset_mock()
        
        #skill ids not valid
        msg["skill_ids"] = "4"
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
             "error":"knowledge tracing not done because supplied 'skill_ids' is not valid; must be dict.",
             "responder":"kt"    
        })
        self.test_subject.send_response.reset_mock()
        
        #outcome is not string
        msg["skill_ids"] = {"skill1":"skill1_id","skill2":"skill2_id"}
        msg["outcome"] = True
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
             "error": "knowledge tracing not done because outcome was neither 'correct' or 'incorrect'",
             "responder":"kt"  
        })
        self.test_subject.send_response.reset_mock()
        
        #first run, default values
        msg["outcome"] = "correct"
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
             "traced_skills" : {
                 "skill1":{
                    'skill_id': "skill1_id",
                    'student_id': "123",
                    'probability_known': 0.75,
                    'probability_learned': 0.5,
                    'probability_guess': 0.5,
                    'probability_mistake': 0.5,
                },
                "skill2":{
                    'skill_id': "skill2_id",
                    'student_id': "123",
                    'probability_known': 0.75,
                    'probability_learned': 0.5,
                    'probability_guess': 0.5,
                    'probability_mistake': 0.5,
             }},
             "responder":"kt",  
        })
        self.test_subject.send_response.reset_mock()
        
        #second run, values should change
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
             "traced_skills" : {
                 "skill1":{
                    'skill_id': "skill1_id",
                    'student_id': "123",
                    'probability_known': 0.875,
                    'probability_learned': 0.5,
                    'probability_guess': 0.5,
                    'probability_mistake': 0.5,
                },
                "skill2":{
                    'skill_id': "skill2_id",
                    'student_id': "123",
                    'probability_known': 0.875,
                    'probability_learned': 0.5,
                    'probability_guess': 0.5,
                    'probability_mistake': 0.5,
             }},
             "responder":"kt",  
        })
        self.test_subject.send_response.reset_mock()
        
       
        
