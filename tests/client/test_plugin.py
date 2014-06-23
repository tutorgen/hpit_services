import sure
import pytest
import httpretty
import requests

from client import Plugin
from client.settings import HPIT_URL_ROOT
from client.exceptions import ConnectionError
from client.exceptions import PluginPollError

@httpretty.activate
def test_constructor():
    """
    Plugin.__init__() Test plan:
        -ensure connected is false
        -ensure name is argument
        -ensure is subscribed to transaction
    """
    test_name = "test_name"
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/test_name/subscribe/transaction",
                            body='',
                            )
    
    test_plugin = Plugin(test_name,None)
    
    test_plugin.connected.should.equal(False)
    test_plugin.name.should.equal(test_name)
    test_plugin.callbacks.should.have.key("transaction")
    

@httpretty.activate
def test_connect():
    """
    Plugin.test_connect() Test plan:
        -ensure that true returned on good connection
        -ensure that exception thrown on bad connection
    """
    
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/connect/test_name",
                            body='{"entity_name":"tutor_name","entity_id":"4"}',
                            )
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/test_name/subscribe/transaction",
                            body='',
                            )
    
    test_plugin = Plugin("test_name",None)
    
    test_plugin.connected.should.equal(False)
    test_plugin.connect().should.equal(True)
    test_plugin.connected.should.equal(True)
    
@httpretty.activate
def test_disconnect():
    """
    Plugin.test_disconnect() Test plan:
        -ensure that connected is false after calling.
    """
    
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/disconnect",
                            body='OK',
                            )
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/test_name/subscribe/transaction",
                            body='',
                            )
    
    test_plugin = Plugin("test_name",None)
    test_plugin.connected = True
    
    test_plugin.disconnect().should.equal(False)
    test_plugin.connected.should.equal(False)
    
    
@httpretty.activate
def test_list_subscriptions():
    """
    Plugin.list_subscriptions() Test plan:
        -ensure the subscriptions are in return value
        -ensure that 'unknown' subscriptions set callback to none
        -ensure that 'known' subsriptsion still have their callbacks set
        -ensure that the return value is a dictionary
    """
    httpretty.register_uri(httpretty.GET,HPIT_URL_ROOT+"/plugin/test_name/subscriptions",
                            body='{"subscriptions":["transactions","subscription1","subscription2"]}',
                            )
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/test_name/subscribe/transaction",
                            body='',
                            )
    
    test_plugin = Plugin("test_name",None)
    test_plugin.callbacks["subscription1"] = 4
    
    subscriptions = test_plugin.list_subscriptions()
    
    "transaction".should.be.within(subscriptions)
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
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/test_name/subscribe/test_event",
                            body='OK',
                            )
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/test_name/subscribe/transaction",
                            body='',
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
    
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/test_name/unsubscribe/test_event",
                            body='OK',
                            )
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/test_name/unsubscribe/test_event2",
                            body='OK',
                            )
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/test_name/subscribe/transaction",
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
    
    httpretty.register_uri(httpretty.GET,HPIT_URL_ROOT+"/plugin/test_name/messages",
                            body='{"messages":"4"}',
                            )
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/test_name/subscribe/transaction",
                            body='',
                            )
    
    test_plugin = Plugin("test_name",None)
    test_plugin._poll().should_not.equal(None)
    

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
    
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/test_name/subscribe/transaction",
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
    event_param = [{"event_name":"test_event","message":"test message"}]
    
    
    test_plugin = Plugin("test_name",None)
    
    setattr(test_plugin,"pre_dispatch",returnFalse)
    test_plugin._dispatch(event_param).should.equal(False)
    
    setattr(test_plugin,"pre_dispatch",returnTrue)
    setattr(test_plugin,"post_dispatch",returnFalse)
    test_plugin.callbacks["test_event"] = testCallback
    test_plugin._dispatch(event_param).should.equal(False)
    
    del test_plugin.callbacks["test_event"]
    test_plugin.wildcard_callback = 4
    test_plugin._dispatch.when.called_with(event_param).should.throw(PluginPollError)
    
    setattr(test_plugin,"post_dispatch",returnTrue)
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
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/test_name/subscribe/transaction",
                            body='',
                            )
    
    test_plugin = Plugin("test_name",None)
    test_plugin.send_response(4,{"payload":"4"})
    


