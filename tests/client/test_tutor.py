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
        -entity_id and api_key are set to params as strings
    """
    test_entity_id = 1234
    test_api_key = 4567
    test_tutor = Tutor(test_entity_id,test_api_key,None)
    
    test_tutor.entity_id.should.equal(str(test_entity_id))
    test_tutor.api_key.should.equal(str(test_api_key))
    test_tutor.callback.should.equal(None)
    
    


