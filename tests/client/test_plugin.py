import sure
import pytest
import httpretty
import requests

from client import Plugin
from client.settings import HPIT_URL_ROOT
from client.exceptions import ConnectionError, PluginPollError, BadCallbackException


test_entity_id = 1234
test_api_key = 4567
test_plugin = None

def setup_function(function):
    global test_plugin
    test_plugin = Plugin(test_entity_id,test_api_key,None)

def teardown_function(function):
    global test_plugin    
    test_plugin = None

@httpretty.activate
def test_constructor():
    """
    Plugin.__init__() Test plan:
        -ensure connected is false
        -ensure name is argument
        -entity id and api key are strings
    """
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/subscribe",
                            body='',
                            )
    
    test_plugin.connected.should.equal(False)
    test_plugin.entity_id.should.equal(str(test_entity_id))
    test_plugin.api_key.should.equal(str(test_api_key))
    

@httpretty.activate
def test_register_transaction_callback():
    """
    Plugin.register_transaction_callback() Test plan:
        -check if transaction_callback = param
        -make sure callback is callable
    """
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/subscribe",
                            body='',
                            )
   
    def simple_callback():
        pass
    
    test_plugin.register_transaction_callback.when.called_with(4).should.throw(BadCallbackException)
    test_plugin.register_transaction_callback(simple_callback)
    test_plugin.transaction_callback.should.equal(simple_callback)


@httpretty.activate
def test_clear_transaction_callback():
    """
    Plugin.clear_transaction_callback() Test plan:
        - make sure self.transaction_callback is None
    """
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/unsubscribe",
                            body='',
                            )
    
    def simple_callback():
        pass
    test_plugin.transaction_callback = simple_callback
    test_plugin.clear_transaction_callback()
    test_plugin.transaction_callback.should.equal(None)
    
    
@httpretty.activate
def test_list_subscriptions():
    """
    Plugin.list_subscriptions() Test plan:
        -ensure the subscriptions are in return value
        -ensure that 'unknown' subscriptions set callback to none
        -ensure that 'known' subsriptsion still have their callbacks set
        -ensure that the return value is a dictionary
    """
    httpretty.register_uri(httpretty.GET,HPIT_URL_ROOT+"/plugin/subscription/list",
                            body='{"subscriptions":["subscription1","subscription2"]}',
                            )
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/subscribe",
                            body='',
                            )
    
    test_plugin.callbacks["subscription1"] = 4
    
    subscriptions = test_plugin.list_subscriptions()
    
    "subscription1".should.be.within(subscriptions)
    "subscription2".should.be.within(subscriptions)
    
    test_plugin.callbacks["subscription1"].should.equal(4)
    test_plugin.callbacks["subscription2"].should.equal(None)
    
    subscriptions.should.be.a('dict')
    
    
   
@httpretty.activate
def test_subscribe():
    """
    Plugin.subscribe() Test plan:
        -ensure that args passed are then in callbacks dict 
    """
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/subscribe",
                            body='OK',
                            )
    
    def test_callback():
        pass
    
    test_plugin = Plugin("test_name",None)
    
    test_plugin.subscribe(test_event=test_callback)
    test_plugin.callbacks["test_event"].should.equal(test_callback)
    

@httpretty.activate
def test_unsubscribe():
    """
    Plugin.unsubscribe() Test plan:
        -ensure that called numerous times for args
        -ensure event name is removed from callbacks
        -if not in callbacks, make sure keyerror not raised
    """
   
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/unsubscribe",
                            body='OK',
                            )
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/subscribe",
                            body='',
                            )
    
    test_plugin = Plugin("test_name",None)
        
    def test_callback():
        pass
    
    test_plugin.callbacks["test_event2"] = test_callback

    test_plugin.unsubscribe("test_event","test_event2")
    
    test_plugin.callbacks.should_not.have.key("test_event")
    test_plugin.callbacks.should_not.have.key("test_event2")
    
    
@httpretty.activate
def test_poll():
    """
    Plugin._poll() Test plan:
        -ensure we get something from server
    """
    
    httpretty.register_uri(httpretty.GET,HPIT_URL_ROOT+"/plugin/message/list",
                            body='{"messages":"4"}',
                            )
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/subscribe",
                            body='',
                            )
    
    test_plugin = Plugin("test_name",None)
    test_plugin._poll().should_not.equal(None)
    

def test_handle_transactions():
    """
    Plugin._handle_transactions() Test plan:
        -
    """
    pass


wildCardCalled = False
@httpretty.activate
def test_dispatch():
    """
    Plugin._dispatch() Test plan:
        -if pre_dispatch hook not defined or false, return false
        -if post_dispatch hook not defined or false, return false
        -ensure pluginpollerror raised if wildcard callback not set on key error
        -ensure wildcard callback is called if callback not set on key error if exists
        -ensure pluginpollerror raised if no callback set
        -ensure typerror raised if its not a function
        -true on success
        
        Table:
        pre_dispatch   post dispatch    callback[event]=    wildcard set  callback callable     result            
        
        returnFalse    *                set                 *             *                     false
        returnTrue     returnFalse      set                 *             Yes                   false
        returnTrue     returnTrue       not set             Not callable  *                     PluginPollError
        returnTrue     returntrue       not set             Yes           *                     callbackCalled = True, rv True
        returnTrue     returnTrue       None                *             No (none)             PluginPollError
        returnTrue     returnTrue       4                   *             No (4)                TypeError
        returnTrue     returnTrue       set                 *             Yes                   true
    """
    
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/subscribe",
                            body='',
                            )
    
    def returnTrue():
        return True
    def returnFalse():
        return False
    def testCallback(param):
        pass
    def wildCard(param):
        global wildCardCalled
        wildCardCalled = True      
    event_param = [{"message_id": '1234', "sender_entity_id": '4567', "message_name":"test_event","message":{"thing": "test message"}}]
    
    
    
    setattr(test_plugin,"pre_dispatch_messages",returnFalse)
    test_plugin._dispatch(event_param).should.equal(False)
    
    setattr(test_plugin,"pre_dispatch_messages",returnTrue)
    setattr(test_plugin,"post_dispatch_messages",returnFalse)
    test_plugin.callbacks["test_event"] = testCallback
    test_plugin._dispatch(event_param).should.equal(False)
    
    del test_plugin.callbacks["test_event"]
    test_plugin.wildcard_callback = 4
    test_plugin._dispatch.when.called_with(event_param).should.throw(PluginPollError)
    
    setattr(test_plugin,"post_dispatch_messages",returnTrue)
    test_plugin.wildcard_callback = wildCard
    test_plugin._dispatch(event_param).should.equal(True)
    wildCardCalled.should.equal(True)
    
    test_plugin.callbacks["test_event"] = None
    test_plugin._dispatch.when.called_with(event_param).should.throw(PluginPollError)
    
    test_plugin.callbacks["test_event"] = 4
    test_plugin._dispatch.when.called_with(event_param).should.throw(TypeError)
    
    test_plugin.callbacks["test_event"] = testCallback
    test_plugin._dispatch(event_param).should.equal(True)
    

@httpretty.activate
def test_send_reponse():
    """
    Plugin.send_response() Test plan:
        -make sure no exception raised
    """
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/response",
                            body='OK',
                            )
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/subscribe",
                            body='',
                            )
    
    test_plugin = Plugin("test_name",None)
    test_plugin.send_response(4,{"payload":"4"})
    


