import unittest
from mock import *
from pymongo import MongoClient
from pymongo.collection import Collection
from bson.objectid import ObjectId

import requests

from hpit.plugins import TransactionManagementPlugin

from hpit.management.settings_manager import SettingsManager
settings = SettingsManager.get_plugin_settings()

class TestTransactionManagementPlugin(unittest.TestCase):
    
    def setUp(self):
        self.test_subject = TransactionManagementPlugin(123,456,None)

        self.test_subject.logger = MagicMock()
        self.test_subject.send_log_entry = MagicMock()
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
        TransactionManagementPlugin.__init__() Test plan:
            - make sure logger set
            - make sure tracker set
        """
        tmp = TransactionManagementPlugin(123,456,None)
        tmp.logger.should.equal(None)
        tmp.tracker.should.equal({})
    
    def test_post_connect(self):
        """
        TransactionManagementPlugin.post_connect() Test plan:
            - mock register_transaction_callback, make sure called
        """
        self.test_subject.register_transaction_callback = MagicMock()
        self.test_subject.post_connect()
        self.test_subject.register_transaction_callback.assert_called_with(self.test_subject.transaction_callback_method)
    
    def test_transaction_callback_method(self):
        """
        TransactionManagementPlugin.transaction_callback_method() Test plan:
            - if student errors out first, send_rest should not be called
            - if skill errors out first, send_rest should not be called
            - if both error, should only call send_response once
            - if both do not error, send_rest should be called
            - when send rest called, send should be called for other messages (send_rest)
            - if one doesn't respond, should send no response
        """       
        def mock_send_student_error(message_name,payload,callback):
            if message_name == "tutorgen.student_transaction":
                callback({"error":"error message"})
            if message_name == "tutorgen.skill_transaction":
                callback({"skill_ids":{"skill_name":"678"}})
                
        def mock_send_skill_error(message_name,payload,callback):
            if message_name == "tutorgen.student_transaction":
                callback({"student_id":"123","session_id":"456"})
            if message_name == "tutorgen.skill_transaction":
                callback({"error":"error message"})
                
        def mock_send_both_error(message_name,payload,callback):
            if message_name == "tutorgen.student_transaction":
                callback({"error":"error message"})
            if message_name == "tutorgen.skill_transaction":
                callback({"error":"error message"})
        
        def mock_send_no_error(message_name,payload,callback):
            if message_name == "tutorgen.student_transaction":
                callback({"student_id":"123","session_id":"456"})
            if message_name == "tutorgen.skill_transaction":
                callback({"skill_ids":{"skill_name":"678"}})
            
            if message_name == "tutorgen.kt_transaction":
                callback({"responder":"kt"})
            if message_name == "tutorgen.hf_transaction":
                callback({"responder":"hf"})
            if message_name == "tutorgen.boredom_transaction":
                callback({"responder":"boredom"})
            if message_name == "tutorgen.problem_transaction":
                callback({"responder":"problem"})
                
        def mock_send_missing_responder(message_name,payload,callback):
            if message_name == "tutorgen.student_transaction":
                callback({"student_id":"123","session_id":"456"})
            if message_name == "tutorgen.skill_transaction":
                callback({"skill_ids":{"skill_name":"678"}})
            
            if message_name == "tutorgen.kt_transaction":
                callback({"responder":"kt"})
            if message_name == "tutorgen.hf_transaction":
                callback({"responder":"hf"})
            if message_name == "tutorgen.boredom_transaction":
                callback({"responder":"boredom"})
            if message_name == "tutorgen.problem_transaction":
                pass
                
        msg = {"message_id":"1","sender_entity_id":"2"}
        
        #student errors out
        self.test_subject.send = MagicMock(side_effect = mock_send_student_error)
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{"error":"error message"})
        self.test_subject.send_response.reset_mock()
        
        #skill errors out
        self.test_subject.send = MagicMock(side_effect = mock_send_skill_error)
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{"error":"error message"})
        self.test_subject.send_response.reset_mock()

        #both error out
        self.test_subject.send = MagicMock(side_effect = mock_send_both_error)
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{"error":"error message"})
        self.test_subject.send_response.call_count.should.equal(1)
        self.test_subject.send_response.reset_mock()
        
        #neither error out, someone doesn't respond
        self.test_subject.send = MagicMock(side_effect = mock_send_missing_responder)
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.call_count.should.equal(0)

        #neither error out, everyone responds
        self.test_subject.send = MagicMock(side_effect = mock_send_no_error)
        self.test_subject.transaction_callback_method(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "student_id":"123",
            "session_id":"456",
            "skill_ids":{"skill_name":"678"},
            "student_response":{"student_id":"123","session_id":"456"},
            "skill_response":{"skill_ids":{"skill_name":"678"}},
            "kt_response":{
                "responder":"kt",   
            },
            "hf_response":{
                "responder":"hf",   
            },
            "boredom_response":{
                "responder":"boredom",   
            },
            "problem_response":{
                "responder":"problem",   
            },       
        })
        self.test_subject.send_response.reset_mock()
        
        
        
        
        
        
        
