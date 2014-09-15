import sure
import unittest
from mock import *
import nose

from environment.settings_manager import SettingsManager
settings = SettingsManager.get_server_settings()

import json

import flask

from server.models import Plugin, Tutor, Subscription
from server.app import ServerApp
app_instance = ServerApp.get_instance()
app = app_instance.app
mongo = app_instance.mongo
db = app_instance.db
csrf = app_instance.csrf

from uuid import uuid4

from pymongo import MongoClient
from bson.objectid import ObjectId


from datetime import datetime

class TestServerAPI(unittest.TestCase):
    
    def connect_helper(self,entity_type):
        if entity_type == "tutor":
            response = self.test_client.post("/connect",data = json.dumps({"entity_id":self.tutor_entity_id,"api_key":self.tutor_secret_key}),content_type="application/json")
        else:
            response = self.test_client.post("/connect",data = json.dumps({"entity_id":self.plugin_entity_id,"api_key":self.plugin_secret_key}),content_type="application/json")               
        if b'OK' not in response.data:
            raise Exception("connect_helper failed")
         
    def disconnect_helper(self, entity_type):
        if entity_type == "tutor":
            response = self.test_client.post("/disconnect",data = json.dumps({"entity_id":self.tutor_entity_id,"api_key":self.tutor_secret_key}),content_type="application/json")
        else:
            response = self.test_client.post("/disconnect",data = json.dumps({"entity_id":self.plugin_entity_id,"api_key":self.plugin_secret_key}),content_type="application/json")               
        if b'OK' not in response.data:
            raise Exception("connect_helper failed")
        
    def setUp(self):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        app.config['TESTING'] = True
        app.testing = True
        self.test_client = app.test_client()
        
        db.create_all()
        
        self.tutor = Tutor()
        self.tutor_name = "Test tutor"
        self.tutor.name = self.tutor_name
        self.tutor_description = "for testing."
        self.tutor.description = self.tutor_description
        
        self.tutor_entity_id = str(uuid4())
        self.tutor.entity_id = self.tutor_entity_id
        self.tutor_secret_key = self.tutor.generate_key()
        
        db.session.add(self.tutor)
        db.session.commit()
        
        
        self.plugin = Plugin()
        self.plugin_name = "Test plugin"
        self.plugin.name = self.plugin_name
        self.plugin_description = "for testing."
        self.plugin.description = self.plugin_description
        
        self.plugin_entity_id = str(uuid4())
        self.plugin.entity_id = self.plugin_entity_id
        self.plugin_secret_key = self.plugin.generate_key()
        
        db.session.add(self.plugin)
        db.session.commit()
        
        client = MongoClient()
        client.drop_database(settings.MONGO_DBNAME)
        
    def tearDown(self):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        self.test_client = None
        db.drop_all()
        db.session.commit()
     
    def test_version(self):
        """
        api.version() Test plan:
            -ensure that return value contains version from settings
        """
        response = self.test_client.get("/version")
        str(response.get_data()).should.contain(settings.HPIT_VERSION)
           
    def test_connect(self):
        """
        api.connect() Test plan:
            -ensure that entity_id and api_key, if either missing, will return a bad parameter
            -mock tutor.query.filter_by and plugin.query.filter_by, ensure plugin.query called if tutor.query returns nothing
            -if not found, should issue a not_found_response
            -send in bum secret, to fail, issuing auth_failed response
            -make sure session conatins entity name, description and id
            -mock db.session.add, called with entity
            -mock db.session.commit, ensure called
            -make sure an ok response is returned
        """
        response = self.test_client.post("/connect",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Missing parameter:')
        response = self.test_client.post("/connect",data = json.dumps({"api_key":"1234"}),content_type="application/json")
        response.data.should.contain(b'Missing parameter:')
        response = self.test_client.post("/connect",data = json.dumps({"entity_id":"1234"}),content_type="application/json")
        response.data.should.contain(b'Missing parameter:')
        
        olddbsessionadd = db.session.add
        olddbsessioncommit = db.session.commit
        db.session.add = MagicMock()
        db.session.commit = MagicMock()
        
        response = self.test_client.post("/connect",data = json.dumps({"entity_id":"bogus","api_key":"bogus"}),content_type="application/json")
        response.data.should.contain(b'Could not find the requested resource.')
        
        response = self.test_client.post("/connect",data = json.dumps({"entity_id":self.tutor_entity_id,"api_key":self.tutor_secret_key+"bum"}),content_type="application/json")
        response.data.should.contain(b'Could not authenticate. Invalid entity_id/api_key combination.')

        with app.test_client() as c:
            response = c.post("/connect",data = json.dumps({"entity_id":self.tutor_entity_id,"api_key":self.tutor_secret_key}),content_type="application/json")
            flask.session["entity_name"].should.equal("Test tutor")
            flask.session["entity_description"].should.equal("for testing.")
            flask.session["entity_id"].should.equal(self.tutor_entity_id)
            response.data.should.contain(b'OK')
            
            response = c.post("/connect",data = json.dumps({"entity_id":self.plugin_entity_id,"api_key":self.plugin_secret_key}),content_type="application/json")
            flask.session["entity_name"].should.equal("Test plugin")
            flask.session["entity_description"].should.equal("for testing.")
            flask.session["entity_id"].should.equal(self.plugin_entity_id)
            response.data.should.contain(b'OK')
                
            
        db.session.add.call_count.should.equal(2)
        db.session.commit.call_count.should.equal(2)
        
        db.session.add = olddbsessionadd
        db.session.commit = olddbsessioncommit
        
    def test_disconnect(self):
        """
        api.disconnect() Test plan:
            - no entity id/api key should return a bad param reposne
            - if no entity_id in session, should return auth_failed
            - if entity_id does not match session, return auth_failed
            
            - if entity does not exist, not found response
            - if can't authenticate with secret, return auth_failed
            
            - db.session.add should be mocked and called
            - db.session.commit should be mocked and called
            - session should be empty
            - ok response returned     
        """
        response = self.test_client.post("/disconnect",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Missing parameter:')
        response = self.test_client.post("/disconnect",data = json.dumps({"api_key":"1234"}),content_type="application/json")
        response.data.should.contain(b'Missing parameter:')
        response = self.test_client.post("/disconnect",data = json.dumps({"entity_id":"1234"}),content_type="application/json")
        response.data.should.contain(b'Missing parameter:')
        
        #entity_id should not be in session
        response = self.test_client.post("/disconnect",data = json.dumps({"entity_id":self.tutor_entity_id,"api_key":self.tutor_secret_key}),content_type="application/json")
        response.data.should.contain(b'Could not authenticate. Invalid entity_id/api_key combination.')
        
        self.connect_helper("tutor")
        #session entity_id should not match request entity_id
        response = self.test_client.post("/disconnect",data = json.dumps({"entity_id":self.tutor_entity_id + "bum","api_key":self.tutor_secret_key+"bum"}),content_type="application/json")
        response.data.should.contain(b'Could not authenticate. Invalid entity_id/api_key combination.')
        
        #[TODO] how can I fail the search entity step while still being authenticated?
        
        olddbsessionadd = db.session.add
        olddbsessioncommit = db.session.commit
        db.session.add = MagicMock()
        db.session.commit = MagicMock()
        
        with app.test_client() as c:
            c.post("/connect",data = json.dumps({"entity_id":self.tutor_entity_id,"api_key":self.tutor_secret_key}),content_type="application/json")
            response = c.post("/disconnect",data = json.dumps({"entity_id":self.tutor_entity_id,"api_key":self.tutor_secret_key}),content_type="application/json")
            len(flask.session.keys()).should.equal(0)
            response.data.should.contain(b'OK')
            
            c.post("/connect",data = json.dumps({"entity_id":self.plugin_entity_id,"api_key":self.plugin_secret_key}),content_type="application/json")
            response = c.post("/disconnect",data = json.dumps({"entity_id":self.plugin_entity_id,"api_key":self.plugin_secret_key}),content_type="application/json")
            len(flask.session.keys()).should.equal(0)
            response.data.should.contain(b'OK')
            
        db.session.add.call_count.should.equal(4)
        db.session.commit.call_count.should.equal(4)
        
        db.session.add = olddbsessionadd
        db.session.commit = olddbsessioncommit
         
    def test_log(self):
        """
        api.log() Test plan:
            - bad parameter raised if log entry not in request
            - no auth raised if entity_id not in session
            - log entry should be present
            - same log entries should be logged twice
            - ok response returned
        """
        response = self.test_client.post("/log",data = json.dumps({"entity_id":self.plugin_entity_id,"log_entry":"log"}),content_type="application/json")
        response.data.should.contain(b'Could not authenticate. Invalid entity_id/api_key combination.')
        
        self.connect_helper("plugin")
        
        response = self.test_client.post("/log",data = json.dumps({"entity_id":self.plugin_entity_id}),content_type="application/json")
        response.data.should.contain(b'Missing parameter:')
        
        response = self.test_client.post("/log",data = json.dumps({"entity_id":self.plugin_entity_id,"log_entry":"This is a log entry"}),content_type="application/json")
        response.data.should.contain(b'OK')
        
        client = MongoClient()
        item = client[settings.MONGO_DBNAME].entity_log.find_one({
                "entity_id":self.plugin_entity_id,
                "log_entry":"This is a log entry",
                'deleted':False
        })
        
        item.should_not.equal(None)
        
        response = self.test_client.post("/log",data = json.dumps({"entity_id":self.plugin_entity_id,"log_entry":"This is a log entry"}),content_type="application/json")
        response.data.should.contain(b'OK')
        
        client = MongoClient()
        item = client[settings.MONGO_DBNAME].entity_log.find({
                "entity_id":self.plugin_entity_id,
                "log_entry":"This is a log entry",
                'deleted':False
        }).count().should.equal(2)
        
        self.disconnect_helper("plugin")
        
    def test_log_list(self):
        """
        api.log_list() Test plan:
            - if not connected, should return auth failed
            - insert some documents, 2 with deleted = false, 1 with true, 1 with different entity_id (4 total)
            - result should be list of 2 records
        """
        client = MongoClient()
        client[settings.MONGO_DBNAME].entity_log.insert([
            {
                'entity_id':self.plugin_entity_id,
                'deleted':False,
                'log_entry':"This is a log entry",
                'created_on': datetime.now().isoformat(),
            },
            {
                'entity_id':self.plugin_entity_id,
                'deleted':False,
                'log_entry':"This is another log entry",
                'created_on': datetime.now().isoformat(),
            },
            {
                'entity_id':"1234",
                'deleted':False,
                'log_entry':"This is a log entry from another entity.",
                'created_on': datetime.now().isoformat(),
            },
            {
                'entity_id':self.plugin_entity_id,
                'deleted':True,
                'log_entry':"This is a deleted log entry",
                'created_on': datetime.now().isoformat(),
            },
        ])
        
        response = self.test_client.get("/log/list",data = json.dumps({}),content_type="application/json")
        response.get_data().should.contain(b'Could not authenticate. Invalid entity_id/api_key combination.')
        
        self.connect_helper("plugin")
        
        response = self.test_client.get("/log/list",data = json.dumps({}),content_type="application/json")
        response.get_data().should.contain(b"This is a log entry")
        response.get_data().should.contain(b"This is another log entry")
        response.get_data().should_not.contain(b"This is a deleted log entry")
        response.get_data().should_not.contain(b"This is a log entry from another entity")
        
        self.disconnect_helper("plugin")
    
    def test_log_clear(self):
        """
        api.log_clear() Test plan:
            - if not connected, should return auth fail
            - insert some docs with deleted = false, call, then should be true
        """
        response = self.test_client.get("/log/clear",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Could not authenticate. Invalid entity_id/api_key combination.')
        
        client = MongoClient()
        client[settings.MONGO_DBNAME].entity_log.insert([
            {
                'entity_id':self.plugin_entity_id,
                'deleted':False,
                'log_entry':"This is a log entry",
                'created_on': datetime.now().isoformat(),
            },
            {
                'entity_id':self.plugin_entity_id,
                'deleted':False,
                'log_entry':"This is another log entry",
                'created_on': datetime.now().isoformat(),
            },
        ])
        
        self.connect_helper("plugin")
        
        response = self.test_client.get("/log/clear",data = json.dumps({}),content_type="application/json")
        response.get_data().should_not.contain(b"false")
        
        self.disconnect_helper("plugin")
        
    def test_subscribe(self):
        """
        api.subscribe() Test plan:
            - if message_name not in request, then bad_parameter response
            - if not connected, return auth_failed_response
            - not found response if a tutor tries to subscribe
            - first time around, ok response, a subscription should be in the db
            - second time around, exists response, nothing should be added
        """
        response = self.test_client.post("/plugin/subscribe",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Missing parameter:')
        
        response = self.test_client.post("/plugin/subscribe",data = json.dumps({"message_name":"test_message"}),content_type="application/json")
        response.data.should.contain(b'Could not authenticate. Invalid entity_id/api_key combination.')
        
        self.connect_helper("tutor")
        response = self.test_client.post("/plugin/subscribe",data = json.dumps({"message_name":"test_message"}),content_type="application/json")
        response.data.should.contain(b'Could not find the requested resource.')
        self.disconnect_helper("tutor")
        
        self.connect_helper("plugin")
        response = self.test_client.post("/plugin/subscribe",data = json.dumps({"message_name":"test_message"}),content_type="application/json")
        response.data.should.contain(b'OK')
        plugin = Plugin.query.filter_by(entity_id=self.plugin_entity_id).first()
        subscription = Subscription.query.filter_by(plugin=plugin, message_name="test_message").first()
        subscription.should_not.equal(None)
        
        response = self.test_client.post("/plugin/subscribe",data = json.dumps({"message_name":"test_message"}),content_type="application/json")
        response.data.should.contain(b'EXISTS')
        self.disconnect_helper("plugin")
        
    def test_unsubscribe(self):
        """
        api.unsubscribe() Test plan:
            - if no message_name in request, bad parameter response
            - if not connected, auth_failed response
            - if a tutor tries to do all this, should be a not_found_response
            - with no subscriptions in database, should return not_found_response
            - with a subscription in the database, should return ok_response, no subscription left
            
        """
        response = self.test_client.post("/plugin/unsubscribe",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Missing parameter:')
        
        response = self.test_client.post("/plugin/unsubscribe",data = json.dumps({"message_name":"test_message"}),content_type="application/json")
        response.data.should.contain(b'Could not authenticate. Invalid entity_id/api_key combination.')
        
        self.connect_helper("tutor")
        response = self.test_client.post("/plugin/unsubscribe",data = json.dumps({"message_name":"test_message"}),content_type="application/json")
        response.data.should.contain(b'Could not find the requested resource.')
        self.disconnect_helper("tutor")
        
        self.connect_helper("plugin")
        response = self.test_client.post("/plugin/unsubscribe",data = json.dumps({"message_name":"test_message"}),content_type="application/json")
        response.data.should.contain(b'Could not find the requested resource.')
        
        self.test_client.post("/plugin/subscribe",data = json.dumps({"message_name":"test_message"}),content_type="application/json") #subscribe to message
        response = self.test_client.post("/plugin/unsubscribe",data = json.dumps({"message_name":"test_message"}),content_type="application/json")
        
        plugin = Plugin.query.filter_by(entity_id=self.plugin_entity_id).first()
        subscription = Subscription.query.filter_by(plugin=plugin, message_name="test_message").first()
        subscription.should.equal(None)
        response.get_data().should.contain(b'OK')
        
        self.disconnect_helper("plugin")

    def test_plugin_list_subscriptions(self):
        """
        api.plugin_list_subscriptions() Test plan:
            - if not connected, return auth_failed
            - if a tutor connected, should return a not_found response
            - if no subscriptions, subscriptions should still be in the response
            - put some subscriptions in the sql database
            - their names should be in the response also
        """
        response = self.test_client.get("/plugin/subscription/list",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Could not authenticate. Invalid entity_id/api_key combination.')
        
        self.connect_helper("tutor")
        response = self.test_client.get("/plugin/subscription/list",data = json.dumps({}),content_type="application/json")
        response.get_data().should.contain(b'Could not find the requested resource.')
        self.disconnect_helper("tutor")
        
        self.connect_helper("plugin")
        response = self.test_client.get("/plugin/subscription/list",data = json.dumps({}),content_type="application/json")
        response.get_data().should.contain(b'subscriptions')
        
        self.test_client.post("/plugin/subscribe",data = json.dumps({"message_name":"test_message"}),content_type="application/json") #subscribe to message
        
        response = self.test_client.get("/plugin/subscription/list",data = json.dumps({}),content_type="application/json")
        response.get_data().should.contain(b'test_message')
        
    def test_plugin_message_history(self):
        """
        api.plugin_message_history() Test plan:
            - if not connected, should return an auth_failed
            - if no messages in mongodb, then message-history should be in result
            - put some messages in the mongo db, and a transaction, and one from another entity
            - should be returned in response (not transactions)
        """
        response = self.test_client.get("/plugin/message/history",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Could not authenticate. Invalid entity_id/api_key combination.')
        
        self.connect_helper("plugin")
        response = self.test_client.get("/plugin/message/history",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'message-history')
        
        client = MongoClient()
        client[settings.MONGO_DBNAME].plugin_messages.insert([
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"some_message",
                'payload':{"msg":"Valid payload 1"},
            },
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"some_message",
                'payload':{"msg":"Valid payload 2"},
            },
            {
                'receiver_entity_id':"1234",
                'message_name':"some message",
                'payload':{"msg":"Bad value"},
            },
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"transaction",
                'payload':{"msg":"Bad value 2"},
            },
        ])
        
        response = self.test_client.get("/plugin/message/history",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Valid payload 1')
        response.data.should.contain(b'Valid payload 2')
        response.data.should_not.contain(b'Bad value')
        response.data.should_not.contain(b'Bad value 2')
       
        self.disconnect_helper("plugin")

    def test_plugin_transaction_history(self):
        """
        api.plugin_transaction_history() Test plan:
            - if not connected, should return an auth_failed
            - if no messages in mongodb, then transaction-history should be in result
            - put some messages in the mongo db, some transactions, some not, some from another entity
            - transaction be returned in response
        """
        response = self.test_client.get("/plugin/transaction/history",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Could not authenticate. Invalid entity_id/api_key combination.')
        
        self.connect_helper("plugin")
        response = self.test_client.get("/plugin/transaction/history",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'transaction-history')
        
        client = MongoClient()
        client[settings.MONGO_DBNAME].plugin_messages.insert([
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"transaction",
                'payload':{"msg":"Valid payload 1"},
            },
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"transaction",
                'payload':{"msg":"Valid payload 2"},
            },
            {
                'receiver_entity_id':"1234",
                'message_name':"transaction",
                'payload':{"msg":"Bad value"},
            },
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"some_message",
                'payload':{"msg":"Bad value 2"},
            },
        ])
        
        response = self.test_client.get("/plugin/transaction/history",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Valid payload 1')
        response.data.should.contain(b'Valid payload 2')
        response.data.should_not.contain(b'Bad value')
        response.data.should_not.contain(b'Bad value 2')
       
        self.disconnect_helper("plugin")

    def test_plugin_message_preview(self):
        """
        api.plugin_message_preview() Test plan:
            - if not connected, should return an auth_failed
            - if nothing in messages, message-preview should still be in response
            - add some messages; some transactions, some of other entity ids, some sent to plugin
            - response should only contain those not sent to plugin, with this entity_id, and no transactions
        """
        response = self.test_client.get("/plugin/message/preview",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Could not authenticate. Invalid entity_id/api_key combination.')
        
        self.connect_helper("plugin")
        response = self.test_client.get("/plugin/message/preview",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'message-preview')
        
        client = MongoClient()
        client[settings.MONGO_DBNAME].plugin_messages.insert([
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"some_message",
                'payload':{"msg":"Valid payload 1"},
                'sent_to_plugin': False,
            },
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"some_message",
                'payload':{"msg":"Valid payload 2"},
                'sent_to_plugin': False,
            },
            {
                'receiver_entity_id':"1234",
                'message_name':"some_message",
                'payload':{"msg":"Bad value"},
                'sent_to_plugin': False,
            },
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"transaction",
                'payload':{"msg":"Bad value 2"},
                'sent_to_plugin': False,
            },
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"some_message",
                'payload':{"msg":"Bad value 3"},
                'sent_to_plugin': True,
            },
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"transaction",
                'payload':{"msg":"Bad value 4"},
                'send_to_plugin': True,
            },
        ])
        
        response = self.test_client.get("/plugin/message/preview",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Valid payload 1')
        response.data.should.contain(b'Valid payload 2')
        response.data.should_not.contain(b'Bad value')
        response.data.should_not.contain(b'Bad value 2')
        response.data.should_not.contain(b'Bad value 3')
        response.data.should_not.contain(b'Bad value 4')
       
        self.disconnect_helper("plugin")

    def test_plugin_transaction_preview(self):
        """
        api.plugin_transaction_preview() Test plan:
            - if not connected, should return an auth_failed
            - if nothing in messages, transaction-preview should still be in response
            - add some messages; some transactions, some of other entity ids, some sent to plugin
            - response should only contain those not sent to plugin, with this entity_id, and only transactions
        """
        response = self.test_client.get("/plugin/transaction/preview",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Could not authenticate. Invalid entity_id/api_key combination.')
        
        self.connect_helper("plugin")
        response = self.test_client.get("/plugin/transaction/preview",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'transaction-preview')
        
        client = MongoClient()
        client[settings.MONGO_DBNAME].plugin_messages.insert([
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"transaction",
                'payload':{"msg":"Valid payload 1"},
                'sent_to_plugin': False,
            },
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"transaction",
                'payload':{"msg":"Valid payload 2"},
                'sent_to_plugin': False,
            },
            {
                'receiver_entity_id':"1234",
                'message_name':"transaction",
                'message_payload':{"msg":"Bad value"},
                'sent_to_plugin': False,
            },
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"some_message",
                'payload':{"msg":"Bad value 2"},
                'sent_to_plugin': False,
            },
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"transaction",
                'payload':{"msg":"Bad value 3"},
                'sent_to_plugin': True,
            },
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"some_message",
                'payload':{"msg":"Bad value 4"},
                'send_to_plugin': True,
            },
        ])
        
        response = self.test_client.get("/plugin/transaction/preview",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Valid payload 1')
        response.data.should.contain(b'Valid payload 2')
        response.data.should_not.contain(b'Bad value')
        response.data.should_not.contain(b'Bad value 2')
        response.data.should_not.contain(b'Bad value 3')
        response.data.should_not.contain(b'Bad value 4')
       
        self.disconnect_helper("plugin")

    def test_plugin_message_list(self):
        """
        api.plugin_message_list() Test plan:
            - If not connected, should return an auth_failed
            - if empty, result should still be in response
            - put some messages in db, some sent to plugin = true, some false, some transactions, some of other entity_id
            - those messages should have sent_to_plugin set to false
            - the messages with equal entity_id, not transaction, and origionally sent_to_plugin false should be in the result
        """
        response = self.test_client.get("/plugin/message/list",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Could not authenticate. Invalid entity_id/api_key combination.')
        
        self.connect_helper("plugin")
        response = self.test_client.get("/plugin/message/list",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'messages')
        
        client = MongoClient()
        client[settings.MONGO_DBNAME].plugin_messages.insert([
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"some_message",
                'payload':{"msg":"Valid payload 1"},
                'sent_to_plugin': False,
                'message_id':"1",
                'sender_entity_id':"1",
            },
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"some_message",
                'payload':{"msg":"Valid payload 2"},
                'sent_to_plugin': False,
                'message_id':"1",
                'sender_entity_id':"1",
            },
            {
                'receiver_entity_id':"1234",
                'message_name':"some_message",
                'payload':{"msg":"Bad value"},
                'sent_to_plugin': False,
                'message_id':"1",
                'sender_entity_id':"1",
            },
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"transaction",
                'payload':{"msg":"Bad value 2"},
                'sent_to_plugin': False,
                'message_id':"1",
                'sender_entity_id':"1",
            },
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"some_message",
                'payload':{"msg":"Bad value 3"},
                'sent_to_plugin': True,
                'message_id':"1",
                'sender_entity_id':"1",
            },
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"transaction",
                'payload':{"msg":"Bad value 4"},
                'send_to_plugin': True,
                'message_id':"1",
                'sender_entity_id':"1",
            },
        ])
        
        response = self.test_client.get("/plugin/message/list",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Valid payload 1')
        response.data.should.contain(b'Valid payload 2')
        response.data.should_not.contain(b'Bad value')
        response.data.should_not.contain(b'Bad value 2')
        response.data.should_not.contain(b'Bad value 3')
        response.data.should_not.contain(b'Bad value 4')
       
        client[settings.MONGO_DBNAME].plugin_messages.find(
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"some_message",
                'sent_to_plugin': True,
            }     
        ).count().should.equal(3)
        
       
        self.disconnect_helper("plugin")

    def test_plugin_transaction_list(self):
        """
        api.plugin_transaction_list() Test plan:
            - If not connected, should return an auth_failed
            - if empty, result should still be in response
            - put some messages in db, some sent to plugin = true, some false, some transactions, some of other entity_id
            - those messages should have sent to plugin set to false
            - the messages with equal entity_id, transaction, and origionally sent to plugin false should be in the result
        """
        response = self.test_client.get("/plugin/transaction/list",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Could not authenticate. Invalid entity_id/api_key combination.')
        
        self.connect_helper("plugin")
        response = self.test_client.get("/plugin/transaction/list",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'transactions')
        
        client = MongoClient()
        client[settings.MONGO_DBNAME].plugin_messages.insert([
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"transaction",
                'payload':{"msg":"Valid payload 1"},
                'sent_to_plugin': False,
                'message_id':"1",
                'sender_entity_id':"1",
            },
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"transaction",
                'payload':{"msg":"Valid payload 2"},
                'sent_to_plugin': False,
                'message_id':"1",
                'sender_entity_id':"1",
            },
            {
                'receiver_entity_id':"1234",
                'message_name':"transaction",
                'payload':{"msg":"Bad value"},
                'sent_to_plugin': False,
                'message_id':"1",
                'sender_entity_id':"1",
            },
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"some_message",
                'payload':{"msg":"Bad value 2"},
                'sent_to_plugin': False,
                'message_id':"1",
                'sender_entity_id':"1",
            },
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"transaction",
                'payload':{"msg":"Bad value 3"},
                'sent_to_plugin': True,
                'message_id':"1",
                'sender_entity_id':"1",
            },
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"some_message",
                'payload':{"msg":"Bad value 4"},
                'send_to_plugin': True,
                'message_id':"1",
                'sender_entity_id':"1",
            },
        ])
        
        response = self.test_client.get("/plugin/transaction/list",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Valid payload 1')
        response.data.should.contain(b'Valid payload 2')
        response.data.should_not.contain(b'Bad value')
        response.data.should_not.contain(b'Bad value 2')
        response.data.should_not.contain(b'Bad value 3')
        response.data.should_not.contain(b'Bad value 4')
       
        client[settings.MONGO_DBNAME].plugin_messages.find(
            {
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"transaction",
                'sent_to_plugin': True,
            }     
        ).count().should.equal(3)
        
       
        self.disconnect_helper("plugin")

    def test_message(self):
        """
        api.message() Test plan:
            - if not conected, should return an auth_failed
            - request should have name and payload params, otherwise bad response
            - message should be written to db, sender id correctly set
            - if a subscription exists
                - message should be written to plugin_messages
                - receiver_entity_id should be the subscription plugin_entity_id
                - sender_id same as sender's entity_id
            -response should have message_id
        """
        response = self.test_client.post("/message",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Could not authenticate. Invalid entity_id/api_key combination.')
        
        self.connect_helper("plugin")
        response = self.test_client.post("/message",data = json.dumps({"name":"test"}),content_type="application/json")
        response.data.should.contain(b'Missing parameter:')
        
        response = self.test_client.post("/message",data = json.dumps({"payload":{"test":"test"}}),content_type="application/json")
        response.data.should.contain(b'Missing parameter:')
        
        response = self.test_client.post("/message",data = json.dumps({"name":"test","payload":{"test":"test"}}),content_type="application/json")
        response.data.should.contain(b'message_id')
        
        client = MongoClient()
        client[settings.MONGO_DBNAME].messages.find(
            {
                'sender_entity_id':self.plugin_entity_id,
                'message_name':"test",
                'payload': {"test":"test"},
            }     
        ).count().should.equal(1)
        
        self.test_client.post("/plugin/subscribe",data = json.dumps({"message_name":"test"}),content_type="application/json") #subscribe to message

        response = self.test_client.post("/message",data = json.dumps({"name":"test","payload":{"test":"test"}}),content_type="application/json")
        response.data.should.contain(b'message_id')
        
        client[settings.MONGO_DBNAME].plugin_messages.find(
            {
                'sender_entity_id':self.plugin_entity_id,
                'receiver_entity_id':self.plugin_entity_id,
                'message_name':"test",
                'payload': {"test":"test"},
                'sent_to_plugin':False,
            }     
        ).count().should.equal(1)
        

    def test_response(self):
        """
        api.response() Test plan:
            - if not connected, should return an auth_failed
            - if no message_id or payload, should issue bad_parameter response
            - add two messages to plugin_messages
                - one has receiver_entity_id to entity_id, one has bogus value
            - respondes should have a record inserted
                - message id should equal plugin_message message_id
                - sender_id should equal the plugins entity_id
                - receiver_id should be the plugin_message sender_entity_id
            - response should contain response_id
        """
        response = self.test_client.post("/response",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Could not authenticate. Invalid entity_id/api_key combination.')
        
        self.connect_helper("plugin")
        self.test_client.post("/plugin/subscribe",data = json.dumps({"message_name":"test"}),content_type="application/json") #subscribe to message
        response = self.test_client.post("/response",data = json.dumps({"name":"name"}),content_type="application/json")
        response.data.should.contain(b'Missing parameter:')
        response = self.test_client.post("/response",data = json.dumps({"payload":{"test":"test"}}),content_type="application/json")
        response.data.should.contain(b'Missing parameter:')
        self.disconnect_helper("plugin")
        
        self.connect_helper("tutor")
        response = self.test_client.post("/message",data = json.dumps({"name":"test","payload":{"test":"test"}}),content_type="application/json")#put a message
        response_string= response.get_data().decode('utf-8')
        message_id = json.loads(response_string)["message_id"]
        response = self.test_client.post("/message",data = json.dumps({"name":"test","payload":{"bogus":"bogus"}}),content_type="application/json")#put a message
        self.disconnect_helper("tutor")
        
        self.connect_helper("plugin")
        response = self.test_client.post("/response",data = json.dumps({"message_id":str(message_id),"payload":{"response":"test response"}}),content_type="application/json")
        response.data.should.contain(b'response_id')

        client=MongoClient()
        client[settings.MONGO_DBNAME].responses.find(
            {
                'message_id':ObjectId(message_id),
                'sender_entity_id':self.plugin_entity_id,
                'receiver_entity_id':self.tutor_entity_id,
                'response': {"response":"test response"},
                'response_received':False,
            }     
        ).count().should.equal(1)
        self.disconnect_helper("plugin")
        
    def test_response_list(self):
        """
        api.response_list() Test plan:
            - if not connected, should return an auth_failed
            - if no responses, responses should still be in response
            - add some responses to the db, with some with received as false, some true
            - those with received as false should be updated to true and returned
        """
        response = self.test_client.get("/response/list",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Could not authenticate. Invalid entity_id/api_key combination.')
        
        self.connect_helper("plugin")
        response = self.test_client.get("/response/list",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'responses')
        
        client = MongoClient()
        client[settings.MONGO_DBNAME].responses.insert([
                {
                    "receiver_entity_id":self.plugin_entity_id,
                    "response_received":False,
                    "response":{"res":"Good value 1"},
                    "message":{"m":"some message"},
                },
                {
                    "receiver_entity_id":self.plugin_entity_id,
                    "response_received":False,
                    "response":{"res":"Good value 2"},
                    "message":{"m":"some message"},
                },
                {
                    "receiver_entity_id":self.plugin_entity_id,
                    "response_received":True,
                    "response":{"res":"Bad value 1"},
                    "message":{"m":"some message"},
                },
                {
                    "receiver_entity_id":"1234",
                    "response_received":False,
                    "response":{"res":"Bad value 2"},
                    "message":{"m":"some message"},
                },
        ])
        
        response = self.test_client.get("/response/list",data = json.dumps({}),content_type="application/json")
        response.data.should.contain(b'Good value 1')
        response.data.should.contain(b'Good value 2')
        response.data.should_not.contain(b'Bad value 1')
        response.data.should_not.contain(b'Bad value 2')
        
        client[settings.MONGO_DBNAME].responses.find({"response_received":True}).count().should.equal(3)
        
        self.disconnect_helper("plugin")

