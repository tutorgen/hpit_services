import sure
import httpretty

from client.mixins import RequestsMixin
from client.exceptions import ConnectionError

#@httpretty.activate
#def test_yipit_api_returning_deals():
#    httpretty.register_uri(httpretty.GET, "http://api.yipit.com/v1/deals/",
#                           body='[{"title": "Test Deal"}]',
#                           content_type="application/json")

#    response = requests.get('http://api.yipit.com/v1/deals/')

#    expect(response.json()).to.equal([{"title": "Test Deal"}])

def test__post_data():
    pass

@httpretty.activate
def test__get_data():
    httpretty.register_uri(httpretty.GET, 'http://test__get_data/',
        body='[{"test": "true"}]',
        adding_headers={'X-session-cookie': 'abcd1234'})

    httpretty.register_uri(httpretty.GET, 'http://test__get_data_500/', status=500)

    subject = RequestsMixin()

    subject._get_data('http://test__get_data/').should.be({"test": True})
    subject._get_data('http://test__get_data_500/').should.throw(ConnectionError)


def test__try_hook():
    subject = RequestsMixin()

    #It should return True if the hook exists and return True
    def the_hook():
        return True

    subject.the_hook = the_hook

    subject._try_hook('the_hook').should.be(False)

    #It should return False if the hook exists and returns False
    def the_hook():
        return False

    subject.the_hook = the_hook

    subject._try_hook('the_hook').should.be(False)

    #It should return True if the hook doesn't exist
    subject._try_hook('does_not_exist').should.be(True)
