import httpretty
import unittest
from unittest.mock import *
from pymongo import MongoClient
from pymongo.collection import Collection

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
        self.test_subject.db = self.test_subject.mongo.test_hpit_data_storage
    
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
            - If logger exists, logger shouldn't be called.  If it does, it should
            - send message with nothing, just key, just data.  response should contain an error
            - ensure database is empty
            -   call insert, ensure id is returned
            -   call insert again, id should be different
        """
        pass
    
    def test_retrieve_data_callback(self):
        """
        DataStoragePlugin.retrieve_data_callback() Test plan:
            - If logger exists, logger shouldn't be called.  If it does, it should
            - send message with no key.  response should contain error
            - ensure database is empty
            -   should send response with data being none
            - insert two records with same key
            -   should send response with most recent entry
        """
        pass
        
    def test_remove_data_callback(self):
        """
        DataStoragePlugin.remove_data_callback() Test plan:
            - If logger exists, logger shouldn't be called.  If it does, it should
            - send message with no key.  response should contain error
            - with no records matching filter
            -   remove should send response with n:0 ok:1
            - with 1 record matching filter
            -   remove should send response with n:1 ok:1
            - with 2 records matching filter
            -   remove should send response with n:2 ok:1
        """
        pass
        
    
    
