import httpretty
import unittest
from unittest.mock import *

from hpitclient.settings import HpitClientSettings

HPIT_URL_ROOT = HpitClientSettings.settings().HPIT_URL_ROOT

from plugins import DataStoragePlugin

class TestDataStoragePlugin(unittest.TestCase):
    
    def setUp(self):
        httpretty.enable()
        httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/connect",
                                body='{"entity_name":"example_plugin","entity_id":"4"}',
                                )
        httpretty.register_uri(httpretty.POST,HPIT_URL_ROOT+"/plugin/subscribe",
                                body='',
                                )
        
        self.test_subject = DataStoragePlugin(1234,5678,None)
        self.test_subject.db = test_subject.mongo.test_hpit_data_storage
    
    def tearDown(self):
        httpretty.disable()
        httpretty.reset()
        
        client = MongoClient()
        client.drop_database("test_hpit_data_storage")
        
        self.test_subject = None
        
        
    def test_constructor(self):
        """
        DataStoragePlugin.__init__() Test plan:
            -make sure self.mongo is a mongo client
            -make sure self.db is the hpit_data_storage collection
            -make sure logger set correctly
        """
        ds = DataStoragePlugin(1234,5678,None)
        ds.logger.should.equal(None)
        isinstance(ds.mongo,MongoClient).should.equal(True)
        isinstance(ds.db,Collection).should.equal(True)
        ds.db.full_name.should.equal("hpit_data_storage.data")
        
        
    def test_store_data_callback(self):
        """
        DataStoragePlugin.store_data_callback() Test plan:
        """
        pass
    
    def test_retrieve_data_callback(self):
        """
        DataStoragePlugin.retrieve_data_callback() Test plan:
        """
        pass
        
    def test_remove_data_callback(self):
        """
        DataStoragePlugin.remove_data_callback() Test plan:
        """
        pass
        
    
    
