import sure
import httpretty
import json

from client.mixins import RequestsMixin
from client.exceptions import ConnectionError

@httpretty.activate
def test__post_data():
    httpretty.register_uri(httpretty.POST, "http://test__post_data/",
                           body='{"username": "jiansun"}',
                           adding_headers={'X-session-cookie': 'abcd1234'})

    subject = RequestsMixin()
    #it should return the username as jiansun when we post the username as jiansun
    subject._post_data('http://test__post_data/', data='{"username": "jiansun"}').text.should.equal('{"username": "jiansun"}')

    #it should return 200 when we post nothing
    subject._post_data('http://test__post_data/').status_code.should.equal(200)
    
    #it should throw an connection error when status code is 500
    httpretty.register_uri(httpretty.POST, "http://test__post_data_500/", status=500)
    subject._post_data.when.called_with('http://test__post_data_500/').should.throw(ConnectionError)

@httpretty.activate
def test__get_data():
    httpretty.register_uri(httpretty.GET, 'http://test__get_data/',
        body='[{"test": "true"}]',
        adding_headers={'X-session-cookie': 'abcd1234'})

    httpretty.register_uri(httpretty.GET, 'http://test__get_data_500/', status=500)

    subject = RequestsMixin()
    
    subject._get_data('http://test__get_data/').should.equal([{"test": "true"}])

    subject._get_data.when.called_with('http://test__get_data_500/').should.throw(ConnectionError)


def test__try_hook():
    subject = RequestsMixin()

    #It should return True if the hook exists and return True
    def the_hook():
        return True

    subject.the_hook = the_hook

    subject._try_hook('the_hook').should.be(True)

    #It should return False if the hook exists and returns False
    def the_hook():
        return False

    subject.the_hook = the_hook

    subject._try_hook('the_hook').should.be(False)

    #It should return True if the hook doesn't exist
    subject._try_hook('does_not_exist').should.be(True)
