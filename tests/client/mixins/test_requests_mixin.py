import sure
import httpretty

from client.mixins import RequestsMixin

#@httpretty.activate
#def test_yipit_api_returning_deals():
#    httpretty.register_uri(httpretty.GET, "http://api.yipit.com/v1/deals/",
#                           body='[{"title": "Test Deal"}]',
#                           content_type="application/json")

#    response = requests.get('http://api.yipit.com/v1/deals/')

#    expect(response.json()).to.equal([{"title": "Test Deal"}])

def test__post_data():
    pass

def test__get_data():
    pass

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
