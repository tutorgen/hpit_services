import sure
import pytest
import httpretty
import requests

from client import Tutor
from client.settings import HPIT_URL_ROOT
from client.exceptions import ConnectionError

def test_constructor():
    """
    Tutor.__init__() Test plan:
        -ensure name is set
        -ensure connected is false
    """
    test_tutor = Tutor("test_name",None)
    test_tutor.name.should.equal("test_name")
    test_tutor.connected.should.equal(False)

@httpretty.activate
def test_connect():
    """
    Tutor.test_connect() Test plan:
        -ensure that true returned on good connection
        -ensure that exception thrown on bad connection
    """

    test_tutor = Tutor("test_name",None)
    
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/tutor/connect/test_name",
                            body='{"entity_name":"tutor_name","entity_id":"4"}',
                            )
    
    test_tutor.connected.should.equal(False)
    test_tutor.connect().should.equal(True)
    test_tutor.connected.should.equal(True)
    
@httpretty.activate
def test_disconnect():
    """
    Tutor.test_disconnect() Test plan:
        -ensure that connected is false after calling.
    """
    
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/tutor/disconnect",
                            body='OK',
                            )
    
    test_tutor = Tutor("test_name",None)
    test_tutor.connected = True
    
    test_tutor.disconnect().should.equal(False)
    test_tutor.connected.should.equal(False)
    
    


