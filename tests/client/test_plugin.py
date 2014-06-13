import sure
import pytest
import httpretty
import requests

from client import Plugin
from client.settings import HPIT_URL_ROOT
from client.exceptions import ConnectionError

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
    """
    pass
    
@httpretty.activate
def test_dispatch():
    """
    Plugin._dispatch() Test plan:
    """
    pass

@httpretty.activate
def test_send_reponse():
    """
    Plugin.send_response() Test plan:
    """
    pass
    


