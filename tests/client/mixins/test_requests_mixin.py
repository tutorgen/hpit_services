import sure
import httpretty
import json

from client.settings import HPIT_URL_ROOT
from client.mixins import RequestsMixin
from client.exceptions import AuthenticationError, ResourceNotFoundError,InternalServerError
from unittest.mock import MagicMock


@httpretty.activate
def test_connect():
    """
    Plugin.test_connect() Test plan:
        -if not called yet, self.connected should be false
        -self.connected should be true
        -post_connect should be called
        -return value should match self.equal
    """
    
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/connect",
                            body='OK',
                            )
    test_requests_mixin = RequestsMixin()
    test_requests_mixin.connected.should.equal(False)
    test_requests_mixin.post_connect = MagicMock()
    test_requests_mixin.connect().should.equal(True)
    test_requests_mixin.post_connect.assert_called_with()
    test_requests_mixin.connected.should.equal(True)
    

@httpretty.activate
def test_disconnect():
    """
    Plugin.test_disconnect() Test plan:
        -ensure that connected is false after calling.
        -ensure hook is called
        -ensure return value matches self.connected
    """
    
    httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/disconnect",
                            body='OK',
                            )
    
    test_requests_mixin = RequestsMixin()
    test_requests_mixin.connected = True
    test_requests_mixin.post_disconnect = MagicMock()
    
    test_requests_mixin.disconnect().should.equal(False)
    test_requests_mixin.post_disconnect.assert_called_with()
    test_requests_mixin.connected.should.equal(False)


@httpretty.activate
def test__post_data():
    httpretty.register_uri(httpretty.POST, "http://test__post_data/",
                           body='{"username": "jiansun"}',
                           adding_headers={'X-session-cookie': 'abcd1234'})
    
    test_requests_mixin = RequestsMixin()
    #it should return the username as jiansun when we post the username as jiansun
    test_requests_mixin._post_data('http://test__post_data/', data='{"username": "jiansun"}').text.should.equal('{"username": "jiansun"}')

    #it should return 200 when we post nothing
    test_requests_mixin._post_data('http://test__post_data/').status_code.should.equal(200)
    
    #it should throw an connection error when status code is 500
    httpretty.register_uri(httpretty.POST, "http://test__post_data_500/", status=500)
    test_requests_mixin._post_data.when.called_with('http://test__post_data_500/').should.throw(InternalServerError)
    
    #it should throw an connection error when status code is 404
    httpretty.register_uri(httpretty.POST, "http://test__post_data_404/", status=404)
    test_requests_mixin._post_data.when.called_with('http://test__post_data_404/').should.throw(ResourceNotFoundError)
    
    #it should throw an connection error when status code is 403
    httpretty.register_uri(httpretty.POST, "http://test__post_data_403/", status=403)
    test_requests_mixin._post_data.when.called_with('http://test__post_data_403/').should.throw(AuthenticationError)

@httpretty.activate
def test__get_data():
    
    test_requests_mixin = RequestsMixin()  
    
    #normal execution
    httpretty.register_uri(httpretty.GET, 'http://test__get_data/',
        body='[{"test": "true"}]',
        adding_headers={'X-session-cookie': 'abcd1234'})
      
    test_requests_mixin._get_data('http://test__get_data/').should.equal([{"test": "true"}])

    #it should throw an connection error when status code is 500
    httpretty.register_uri(httpretty.GET, "http://test__post_data_500/", status=500)
    test_requests_mixin._get_data.when.called_with('http://test__post_data_500/').should.throw(InternalServerError)
    
    #it should throw an connection error when status code is 404
    httpretty.register_uri(httpretty.GET, "http://test__post_data_404/", status=404)
    test_requests_mixin._get_data.when.called_with('http://test__post_data_404/').should.throw(ResourceNotFoundError)
    
    #it should throw an connection error when status code is 403
    httpretty.register_uri(httpretty.GET, "http://test__post_data_403/", status=403)
    test_requests_mixin._get_data.when.called_with('http://test__post_data_403/').should.throw(AuthenticationError)
    
    
def test__try_hook():
    test_requests_mixin = RequestsMixin()
    #It should return True if the hook exists and return True
    def the_hook():
        return True

    test_requests_mixin.the_hook = the_hook

    test_requests_mixin._try_hook('the_hook').should.be(True)

    #It should return False if the hook exists and returns False
    def the_hook():
        return False

    test_requests_mixin.the_hook = the_hook

    test_requests_mixin._try_hook('the_hook').should.be(False)

    #It should return True if the hook doesn't exist
    test_requests_mixin._try_hook('does_not_exist').should.be(True)
