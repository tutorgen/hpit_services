import sure
import pytest
import httpretty
import requests

from client import Plugin
from client.settings import HPIT_URL_ROOT
from client.exceptions import ConnectionError

@httpretty.activate
def test_connect():
    """
    Plugin.test_connect() Test plan:
        -ensure that true returned on good connection
        -ensure that exception thrown on bad connection
    """

    test_plugin = Plugin("test_name",None)
    
    test_plugin.connect().should.throw.(ConnectionError)
    
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/connect/",
                            body='{"entity_name":"tutor_name","entity_id":"4"}',
                            )
    
    test_plugin.connected.should.equal(False)
    test_plugin.connect().should.equal(True)
    test_plugin.connected.should.equal(True)
    
@httpretty.activate
def test_disconnect():
    """
    Plugin.test_disconnect() Test plan:
        -ensure that connected is false after calling.
    """
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/tutor/disconnect",
                            body='OK',
                            )
    
    test_plugin = Plugin("test_name",None)
    test_plugin.connected = True
    
    test_plugin.disconnect().should.equal(False)
    test_plugin.connected.should.equal(False)
    

def test_list_connections():
    
    
@httpretty.activate
def test_list_subscriptions():
    """
    Plugin.list_subscriptions() Test plan:
        -ensure that 'unknown' subscriptions set callback to none
        -ensure that 'known' subsriptsion still have their callbacks set
        -ensure that the return value is a dictionary
    """
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/disconnect",
                            body='{"subscriptions":{"subscription1","subscription2"}}',
                            )
    
    test_plugin = Plugin("test_name",None)
    subscriptions = test_plugin

@httpretty.activate
def test_subscribe():
    """
    Plugin.subscribe() Test plan:
    """
    pass

@httpretty.activate
def test_unsubscribe():
    """
    Plugin.unsubscribe() Test plan:
    """
    psas
    
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
    


