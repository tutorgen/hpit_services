import unittest
from mock import *
from pymongo import MongoClient
from pymongo.collection import Collection
from bson.objectid import ObjectId

from plugins import KnowledgeTracingPlugin

import nose

class TestKnowledgeTracingPlugin(unittest.TestCase):

    def setUp(self):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.test_subject = KnowledgeTracingPlugin(123,456,None)
        self.test_subject.db = self.test_subject.mongo.test_hpit.hpit_knowledge_tracing
        
    def tearDown(self):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        client = MongoClient()
        client.drop_database("test_hpit")
        
        self.test_subject = None
        
    def test_constructor(self):
        """
        KnowledgeTracingPlugin.__init__() Test plan:
            - make sure logger set right
            - make sure self.mongo is a mongo client
            - make sure db is a collection
            -check full name
        """
        ds = KnowledgeTracingPlugin(1234,5678,None)
        ds.logger.should.equal(None)
        isinstance(ds.mongo,MongoClient).should.equal(True)
        isinstance(ds.db,Collection).should.equal(True)
        ds.db.full_name.should.equal("hpit.hpit_knowledge_tracing")
    
    def test_kt_trace(self):
        """
        KnowledgeTracingPlugin.kt_trace() Test plan:
            - mock out send response
            - send without each of the required parameters, response should be error
            - send in bogus kt_config values, should send error response
            - set a kt_config with values, send in new message
            - make sure new p_known is updated in db
            - make sure new p_known is returned in response
        """
        self.test_subject.send_response = MagicMock()
        
        msg = {"message_id":"2"}
        self.test_subject.kt_trace(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_trace requires 'sender_entity_id', 'skill', 'student_id' and 'correct'"})
        self.test_subject.send_response.reset_mock()
        msg["sender_entity_id"] = "3"
        self.test_subject.kt_trace(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_trace requires 'sender_entity_id', 'skill', 'student_id' and 'correct'"})
        self.test_subject.send_response.reset_mock()
        msg["skill"] = "add"
        self.test_subject.kt_trace(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_trace requires 'sender_entity_id', 'skill', 'student_id' and 'correct'"})
        self.test_subject.send_response.reset_mock()
        msg["correct"] = True
        self.test_subject.kt_trace(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_trace requires 'sender_entity_id', 'skill', 'student_id' and 'correct'"})
        self.test_subject.send_response.reset_mock()
        
        msg["student_id"] = "4"
        insert_doc = dict(msg)
        insert_doc["probability_known"] = .7
        insert_doc["probability_learned"] = .2
        insert_doc["probability_guess"] = .3
        insert_doc["probability_mistake"] = .4
        
        self.test_subject.kt_trace(msg)
        self.test_subject.send_response.assert_called_once_with("2",{
                'error': 'No initial settings for plugin (KnowledgeTracingPlugin).',
                'send': {
                    'event_name': 'kt_set_initial',
                    'probability_known': 'float(0.0-1.0)', 
                    'probability_learned': 'float(0.0-1.0)',
                    'probability_guess': 'float(0.0-1.0)',
                    'probability_mistake': 'float(0.0-1.0)',
                    'student_id:':'str(ObjectId)',
                }
            })
        self.test_subject.send_response.reset_mock()
        
        client = MongoClient()
        client.test_hpit.hpit_knowledge_tracing.insert(insert_doc)
        self.test_subject.kt_trace(msg)
        #with correct  = true and these variables, p_known should be 
        expected_value = (.42 / .51) + ( (1 - (.42 / .51)) * .2)
        self.test_subject.send_response.called.should.equal(True) #can't check params because of float precision
        thing  = client.test_hpit.hpit_knowledge_tracing.find_one({'sender_entity_id':"3",'student_id':"4","skill":"add"})
        nose.tools.assert_almost_equal(thing["probability_known"],expected_value,places=5)
        self.test_subject.send_response.reset_mock()
        
        msg["correct"] = False
        client = MongoClient()
        client.test_hpit.hpit_knowledge_tracing.remove({})
        client.test_hpit.hpit_knowledge_tracing.insert(insert_doc)    
        self.test_subject.kt_trace(msg)
        #with correct  = false and these variables, p_known should be 
        expected_value = (.28 / .49) + ( (1 - (.28 / .49)) * .2)
        self.test_subject.send_response.called.should.equal(True)
        thing  = client.test_hpit.hpit_knowledge_tracing.find_one({'sender_entity_id':"3",'student_id':"4","skill":"add"})
        nose.tools.assert_almost_equal(thing["probability_known"],expected_value,places=5)
        
    def test_kt_set_initial_callback(self):
        """
        KnowledgeTracingPlugin.kt_set_initial_callback() Test plan:
            - mock out send response
            - send without each of the required parameters, response should be error
            - send message for non existant kt_config, should insert a new one
            - send message for existing kt_config, should update that one
            - response should always echo parameters sent in
        """
        self.test_subject.send_response = MagicMock()
        
        msg = {"message_id":"2"}
        self.test_subject.kt_set_initial_callback(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_set_initial requires 'sender_entity_id', 'skill', 'probability_known', 'probability_learned', 'probability_guess', 'probability_mistake', and 'student_id'"})
        self.test_subject.send_response.reset_mock()
        msg["sender_entity_id"] = "3"
        self.test_subject.kt_set_initial_callback(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_set_initial requires 'sender_entity_id', 'skill', 'probability_known', 'probability_learned', 'probability_guess', 'probability_mistake', and 'student_id'"})
        self.test_subject.send_response.reset_mock()
        msg["skill"] = "add"
        self.test_subject.kt_set_initial_callback(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_set_initial requires 'sender_entity_id', 'skill', 'probability_known', 'probability_learned', 'probability_guess', 'probability_mistake', and 'student_id'"})
        self.test_subject.send_response.reset_mock()
        msg["probability_known"] = "1.1"
        self.test_subject.kt_set_initial_callback(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_set_initial requires 'sender_entity_id', 'skill', 'probability_known', 'probability_learned', 'probability_guess', 'probability_mistake', and 'student_id'"})
        self.test_subject.send_response.reset_mock()
        msg["probability_learned"] = "1.2"
        self.test_subject.kt_set_initial_callback(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_set_initial requires 'sender_entity_id', 'skill', 'probability_known', 'probability_learned', 'probability_guess', 'probability_mistake', and 'student_id'"})
        self.test_subject.send_response.reset_mock()
        msg["probability_guess"] = "1.3"
        self.test_subject.kt_set_initial_callback(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_set_initial requires 'sender_entity_id', 'skill', 'probability_known', 'probability_learned', 'probability_guess', 'probability_mistake', and 'student_id'"})
        self.test_subject.send_response.reset_mock()
        msg["probability_mistake"] = "1.4"
        self.test_subject.kt_set_initial_callback(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_set_initial requires 'sender_entity_id', 'skill', 'probability_known', 'probability_learned', 'probability_guess', 'probability_mistake', and 'student_id'"})
        self.test_subject.send_response.reset_mock()
        
        msg["student_id"] = "4"
        self.test_subject.kt_set_initial_callback(msg)
        self.test_subject.send_response.assert_called_once_with("2",{
            'skill': "add",
            'probability_known': "1.1",
            'probability_learned': "1.2",
            'probability_guess': "1.3",
            'probability_mistake':"1.4",
            'student_id':"4"
            })
        self.test_subject.send_response.reset_mock()
        
        client = MongoClient()
        thing = client.test_hpit.hpit_knowledge_tracing.find_one({"sender_entity_id":"3","skill":"add","student_id":"4"})
        thing.should_not.equal(None)
        
        msg["probability_known"] = "2.1"
        msg["probability_learned"] = "2.2"
        msg["probability_guess"] = "2.3"
        msg["probability_mistake"] = "2.4"
        self.test_subject.kt_set_initial_callback(msg)
        self.test_subject.send_response.assert_called_once_with("2",{
            'skill': "add",
            'probability_known': "2.1",
            'probability_learned': "2.2",
            'probability_guess': "2.3",
            'probability_mistake':"2.4",
            'student_id':"4"
            })
        self.test_subject.send_response.reset_mock()
        
        client.test_hpit.hpit_knowledge_tracing.find({}).count().should.equal(1)
        thing = client.test_hpit.hpit_knowledge_tracing.find_one({"sender_entity_id":"3","skill":"add","student_id":"4"})
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
        self.test_subject.send_response = MagicMock()
        
        msg = {"message_id":"2"}
        self.test_subject.kt_reset(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_reset requires 'sender_entity_id', 'skill', and 'student_id'"})
        self.test_subject.send_response.reset_mock()
        msg['sender_entity_id'] = "3"
        self.test_subject.kt_reset(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_reset requires 'sender_entity_id', 'skill', and 'student_id'"})
        self.test_subject.send_response.reset_mock()
        msg['skill'] = "add"
        self.test_subject.kt_reset(msg)
        self.test_subject.send_response.assert_called_once_with("2",{"error":"kt_reset requires 'sender_entity_id', 'skill', and 'student_id'"})
        self.test_subject.send_response.reset_mock()
        msg['student_id'] = "4"
        
        self.test_subject.kt_reset(msg)
        self.test_subject.send_response.assert_called_once_with("2",{
            'skill': "add",
            'probability_known': 0.0,
            'probability_learned': 0.0,
            'probability_guess': 0.0,
            'probability_mistake': 0.0,
            'student_id':"4"
        })
        self.test_subject.send_response.reset_mock()
        
        oid = self.test_subject.db.insert({"sender_entity_id":"3","skill":"add","student_id":"4"})
        self.test_subject.kt_reset(msg)
        self.test_subject.send_response.assert_called_once_with("2",{
            'skill': "add",
            'probability_known': 0.0,
            'probability_learned': 0.0,
            'probability_guess': 0.0,
            'probability_mistake': 0.0,
            'student_id':"4"
        })
        
        ob = self.test_subject.db.find_one({"_id":oid})
        ob["probability_known"].should.equal(0.0)
        ob["probability_learned"].should.equal(0.0)
        ob["probability_guess"].should.equal(0.0)
        ob["probability_mistake"].should.equal(0.0)
        
