import sure
import unittest
from mock import *
import nose

from server.settings import ServerSettingsManager
settings = ServerSettingsManager.get_instance().settings

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
            - not round response if a tutor tries to subscribe
            - first time around, ok response, a subscription should be in the db
            - second time around, exists response, nothing should be added
        """
        pass
        
    def test_unsubscribe(self):
        """
        api.unsubscribe() Test plan:
            - if no message_name in request, bad parameter response
            - if not connected, auth_failed response
            - if a tutor tries to do all this, should be a not_found_response
            - with no subscriptions in database, should return not_found_response
            - with a subscription in the database, should return ok_response, no subscription left
            - without a subscription, it will reutrn not_found_response
            
        """
        pass

    def test_plugin_list_subscriptions(self):
        """
        api.plugin_list_subscriptions() Test plan:
            -mock a list of subscriptions in a db for some plugin name
            -ensure list of subscriptions returned on success
            -try to get subscriptions of non existant plugin name
            -ensure that plugins that share names don't share subscriptions
        """
        pass

    def test_plugin_message_history(self):
        """
        api.plugin_message_history() Test plan:
            -mock a db with some events for a given plugin name (at least event need "transaction" as name)
            -ensure a list of names and payloads are returned matches those in DB
            -make sure that plugins that share names do not share histories
            -make sure none of the messages have "transaction" as a name
            -make sure is in the format of event_name and message
        """
        pass

    def test_plugin_transaction_history(self):
        """
        api.plugin_transaction_history() Test plan:
            -mock a db with some events for a given plugin name (at least event need not "transaction" as name)
            -ensure a list of names and payloads are returned matches those in DB
            -make sure that plugins that share names do not share histories
            -make sure all of the messages have "transaction" as a name
            -make sure is in the format of event_name and message
        """
        pass

    def test_plugin_message_preview(self):
        """
        api.plugin_message_preview() Test plan:
            -mock database with transactions, messages, some processed, some not
            -ensure list of names returned matches those in db
            -ensure that none of the returned values have sent_to_plugin be true
            -make sure that plugins that share names do not share previews
            -make sure is in the format of event_name and message
        """
        pass

    def test_plugin_transaction_preview(self):
        """
        api.plugin_transaction_preview() Test plan:
            -mock database with transactions, messages, some processed, some not
            -ensure list of names returned matches those in db
            -ensure that none of the returned values have sent_to_plugin be true
            -make sure that plugins that share names do not share previews
            -make sure is in the format of event_name and message
        """
        pass

    def test_plugin_messages(self):
        """
        api.plugin_messages() Test plan:
            -mock db, add some messages; some sent, some not, some transactions, some not
            -on get, ensure that only sent_to_plugin = false messages are received
            -make sure none of them transactions
            -make sure return value in the form of event,message dict
            -ensure that after fetch, those returned sent_to_plugin is changed to true in the db
            -make sure that two plugins cannot accidentally share messages
            -make sure untouched messages remain unchanged in db
        """
        pass

    def test_plugin_transactions(self):
        """
        api.plugin_transactions() Test plan:
            -mock db, add some messages; some sent, some not, some transactions, some not
            -on get, ensure that only sent_to_plugin = false transactions are received
            -make sure none of them normal messages
            -make sure return value in the form of event,message dict
            -ensure that after fetch, those returned sent_to_plugin is changed to true in the db
            -make sure that two plugins cannot accidentally share transactions
            -make sure untouched messages remain unchanged in db
        """
        pass

    def test_message(self):
        """
        api.message() Test plan:
            -mock a database, empty
            -send a fake request with some data
            -make sure data is correctly propogated to plugin_messagse (fields match)
            -make sure duplicate plugins get duplicate messages (name querying problem probably exists)
            -make sure the returned id is in the plugin_message entries added by the system
        """
        pass

    def test_transaction(self):
        """
        api.transaction() Test plan:
            -mock a database, empty
            -send a fake request with some data
            -make sure data is correctly propogated to plugin_messagse (fields match)
            -transactions should be put in plugin_messages for every plugin that exists (all subscribe to transactions)
            -make sure same named plugins get duplicate messages (name querying problem probably exists)
            -make sure the returned id is in the plugin_message entries added by the system
        """
        pass

    def test_response(self):
        """
        api.response() Test plan:
            -mock db with a message, and no responses
            -Test for invalid message_id... what does it do
            -On success, make sure response written to database
            -reutrned ID should be listed in response database
        """
        pass

    def test_responses(self):
        """
        api.responses() Test plan:
            -ensure 401 returned if session data not available
            -ensure return value is proper format {response: {message: ,response: }}
            -ensure that after response is polled, its received value is set to true
            -ensure that other responses are not touched
        """
        pass
