import sure
import unittest
from mock import *

from server.app import ServerApp
app_instance = ServerApp.get_instance()
app = app_instance.app

from server.settings import ServerSettingsManager
settings = ServerSettingsManager.get_instance().settings

class TestServerAPI(unittest.TestCase):

    def setUp(self):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        selftest_client = app.test_client()
        
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
        #response = test_client.get("/version")
        #str(response.get_data()).should.contain(settings.HPIT_VERSION)
        pass
        
    def test_connect_tutor(self):
        """
        api.connect_tutor() Test plan:
            -ensure response contains the tutor name passed
            -ensure that HPIT_STATUS contains a new entry, that contains tutor name
            -ensure that the session has been set correctly
            -ensure not crash on parameters: #__ plugin, 439034, ""
        """
        pass

    def test_connect_plugin(self):
        """
        api.connect_plugin() Test plan:
            -ensure response contains the plugin name passed
            -ensure that HPIT_STATUS contains a new entry, that contains plugin name
            -ensure that the session has been set correctly
            -ensure not crash on parameters: #__ tutor, 439034, ""
        """
        pass

    def test_tutor_disconnect(self):
        """
        api.disconnect_tutor() Test plan:
            -ensure that HPIT_STATUS loses entity, if exists
            -ensure that HPIT_STATUS is fine if session does not exist
            -ensure remove session entity_name and id
        """
        pass

    def test_plugin_disconnect(self):
        """
        api.disconnect_plugin() Test plan:
            -ensure that HPIT_STATUS loses entity, if exists
            -ensure that HPIT_STATUS is fine if session does not exist
            -ensure remove session entity_name and id
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
