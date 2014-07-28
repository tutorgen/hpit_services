import unittest
from mock import *
from pymongo import MongoClient
from pymongo.collection import Collection

from plugins import DataStoragePlugin

class TestDataStoragePlugin(unittest.TestCase):
    
    def setUp(self):
        self.test_subject = DataStoragePlugin(1234,5678,None)
        self.test_subject.db = self.test_subject.mongo.test_hpit_data_storage.data
    
    def tearDown(self):
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
        self.test_subject.send_response = MagicMock()
       
        msg = {"message_id":"1"}
        self.test_subject.store_data_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{"error":"Error: store_data message must contain a 'key' and 'data'"})
        self.test_subject.send_response.reset_mock()
        
        msg = {"message_id":"1","key":"key1"}
        self.test_subject.store_data_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{"error":"Error: store_data message must contain a 'key' and 'data'"})
        self.test_subject.send_response.reset_mock()
        
        msg = {"message_id":"1","data":"data1"}
        self.test_subject.store_data_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{"error":"Error: store_data message must contain a 'key' and 'data'"})
        self.test_subject.send_response.reset_mock()
        
        self.test_subject.db.remove() #clear database
        
        msg = {"message_id":"1","data":"data1","key":"key1"}
        self.test_subject.store_data_callback(msg)
        
        self.test_subject.send_response.call_args[0][0].should.equal("1")
        insert_id = self.test_subject.send_response.call_args[0][1]["insert_id"]
        
        self.test_subject.store_data_callback(msg)
        insert_id2 = self.test_subject.send_response.call_args[0][1]["insert_id"]
        
        insert_id2.should_not.equal(insert_id)
        
        client = MongoClient()
        result= client.test_hpit_data_storage.data.find({"key":"key1","data":"data1"})
        count =0
        for r in result:
            count+=1
        count.should.equal(2)

    def test_retrieve_data_callback(self):
        """
        DataStoragePlugin.retrieve_data_callback() Test plan:
            - If logger exists, logger shouldn't be called.  If it does, it should
            - send message with no key.  response should contain error
            - ensure database is empty
            -   should send response with data being none
            - insert two records with same key
            -   should send response with first added entry
        """
        self.test_subject.send_response = MagicMock()
        
        msg = {"message_id":"1"}
        self.test_subject.retrieve_data_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{"error":"Error: retrieve_data message must contain a 'key'"})
        self.test_subject.send_response.reset_mock()
        
        self.test_subject.db.remove() #clear database
        
        msg = {"message_id":"1","key":"key1"}
        self.test_subject.retrieve_data_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{"data":None})
        self.test_subject.send_response.reset_mock()
        
        self.test_subject.db.insert({"key":"key1","data":"data1"})
        self.test_subject.db.insert({"key":"key1","data":"data2"}) #insert documents with identical keys
        
        self.test_subject.retrieve_data_callback(msg)
        self.test_subject.send_response.call_args[0][1]["data"]["data"].should.equal("data1")
        
        

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
        self.test_subject.send_response = MagicMock()
        
        msg = {"message_id":"1"}
        self.test_subject.remove_data_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{"error":"Error: remove_data message must contain a 'key'"})
        self.test_subject.send_response.reset_mock()
        
        self.test_subject.db.remove() #clear database

        msg = {"message_id":"1","key":"key1"}
        self.test_subject.remove_data_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{"status":{'ok': 1, 'n': 0}})
        self.test_subject.send_response.reset_mock()
        
        self.test_subject.db.insert({"key":"key1","data":"data1"})
        
        self.test_subject.remove_data_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{"status":{'ok': 1, 'n': 1}})
        self.test_subject.send_response.reset_mock()
        
        
        self.test_subject.db.remove() #clear database
        self.test_subject.db.insert([
            {"key":"key1","data":"data2"},      
            {"key":"key1","data":"data1"},
        ])

        self.test_subject.remove_data_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{"status":{'ok': 1, 'n': 2}})
        self.test_subject.send_response.reset_mock()
        
    
    
