import sure
import unittest
from unittest.mock import *

from server.app import ServerApp
app_instance = ServerApp.get_instance()
app = app_instance.app

from server.settings import ServerSettingsManager
settings = ServerSettingsManager.get_instance().settings

import flask
from flask import session, jsonify, abort, request, Response
from server.models import Plugin, Tutor, Subscription
from server.app import ServerApp
app_instance = ServerApp.get_instance()
app = app_instance.app
mongo = app_instance.mongo
db = app_instance.db
csrf = app_instance.csrf

class TestServerAPI(unittest.TestCase):
    
    class DummyEntity():
        def __init__(self):
            self.name = "name"
            self.description= "description"
            self.entity_id = "3"
        def first(self):
            return self
        def authenticate(self,api_key):
            return True
    
    def setUp(self):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        app.config['TESTING'] = True
        app.testing = True
        self.test_client = app.test_client()
        
    def tearDown(self):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        self.test_client = None
     

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
            -mock authenticate to fail, issuing auth_failed response
            -make sure session conatins entity name, description and id
            -mock db.session.add, called with entity
            -mock db.session.commit, ensure called
            -make sure an ok response is returned
        """
        
     
        
        #response = self.test_client.post("/connect",data = {})
        #response.data.should.contain(b'Missing parameter:')
        response = self.test_client.post("/connect",data = {"api_key":"1234"})
        response.data.should.contain(b'Missing parameter:')
        response = self.test_client.post("/connect",data = {"entity_id":"1234"},content_type="application/json")
        response.data.should.contain(b'Missing parameter:')
        
        db.session.add = MagicMock()
        db.session.commit = MagicMock()
        Tutor.query.filter_by = MagicMock(return_value = TestServerAPI.DummyEntity())
        
        response = self.test_client.post("/connect",data = {"entity_id":"1234","api_key":"1234"},content_type="application/json")
        response.data.should.contain(b'OK')
        

    def test_disconnect(self):
        """
        api.disconnect() Test plan:
            
        """
        pass

    def test_subscribe(self):
        """
        api.subscribe() Test plan:
            -generate 2 payloads, one existing in mock db, one doesn't.
            -return OK if new, EXISTS if not new.
            -ensure new record in DB on OK, and no additional records added on EXISTS
        """
        #response = test_client.post("/plugin/someplugin/subscribe/someevent")
        

    def test_unsubscribe(self):
        """
        api.unsubscribe() Test plan:
            -generate 2 payloads, one existing in mock db, one doesn't.
            -return OK if exists, DOES_NOT_EXIST if new.
            -ensure record removed in DB on OK, and same number of records on DOES_NOT_EXIST
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
