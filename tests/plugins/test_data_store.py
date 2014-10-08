import unittest
from mock import *
from pymongo import MongoClient
from pymongo.collection import Collection

from plugins import DataStoragePlugin

class TestDataStoragePlugin(unittest.TestCase):
    
    def setUp(self):
        self.test_subject = DataStoragePlugin(1234,5678,None)
        self.test_subject.db = self.test_subject.mongo.test_hpit.data_storage
        self.test_subject.send_response = MagicMock()
        
    def tearDown(self):
        client = MongoClient()
        client.drop_database("test_hpit")
        
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
        ds.db.full_name.should.equal("hpit.data_storage")
        
    def test_store_data_callback(self):
        """
        DataStoragePlugin.store_data_callback() Test plan:
            - If logger exists, logger shouldn't be called.  If it does, it should
            - send message with nothing, just key, just data.  response should contain an error
            - ensure database is empty
            -   call insert, ensure item is added to db
            -   call insert again, document should be changed, only 1 document exists
        """
        
        msg= {"message_id":"1","sender_entity_id":"3","data":"data1","key":"key1"}
        self.test_subject.db.remove() #clear database
        
        self.test_subject.store_data_callback(msg)
        result_id =self.test_subject.db.find({"key":"key1","data":"data1","entity_id":"3"}).count().should.equal(1)
        self.test_subject.send_response.assert_called_with("1",{
                "success":True,
        })
        self.test_subject.send_response.reset_mock()

        msg["data"] = "data2"
        self.test_subject.store_data_callback(msg)
        self.test_subject.db.find({"key":"key1","data":"data2","entity_id":"3"}).count().should.equal(1)
        self.test_subject.db.find({}).count().should.equal(1) 
        self.test_subject.send_response.assert_called_with("1",{
                "success":True,
        })    
        
    def test_store_data_callback_no_args(self):
        """
        DataStoragePlugin.store_data_callback() No Args:
        """
        msg = {"message_id":"1","sender_entity_id":"3"}
        self.test_subject.store_data_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{"error":"Error: store_data message must contain a 'key' and 'data'","success":False})
        
    def test_store_data_callback_no_data(self):
        """
        DataStoragePlugin.store_data_callback() No Data:
        """
        msg= {"message_id":"1","sender_entity_id":"3","key":"key1"}
        self.test_subject.store_data_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{"error":"Error: store_data message must contain a 'key' and 'data'","success":False})
        
    def test_store_data_callback_no_key(self):
        """
        DataStoragePlugin.store_data_callback() No Key:
        """
        msg= {"message_id":"1","sender_entity_id":"3","data":"data1"}
        self.test_subject.store_data_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{"error":"Error: store_data message must contain a 'key' and 'data'","success":False})
        
    

    def test_retrieve_data_callback(self):
        """
        DataStoragePlugin.retrieve_data_callback() Test plan:
            - send message with no key.  response should contain error
            - ensure database is empty
            -   should send response with data being none
            - insert two records with same key, different entity ID's
            -   should send response wth right key
        """
        msg = {"message_id":"1","sender_entity_id":"3","key":"key1"}
        self.test_subject.db.insert({"key":"key1","data":"data1","entity_id":"2"})
        self.test_subject.db.insert({"key":"key1","data":"data2","entity_id":"3"}) #should get this one
        
        self.test_subject.retrieve_data_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
                "data":"data2",
                "success":True
        })
        
    def test_retrieve_data_callback_no_key(self):
        """
        DataStoragePlugin.retrieve_data_callback() No Key:
        """
        msg = {"message_id":"1","sender_entity_id":"3"}
        self.test_subject.retrieve_data_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{"error":"Error: retrieve_data message must contain a 'key'","success":False})
    
    def test_retrieve_data_callback_does_note_exist(self):
        """
        DataStoragePlugin.retrieve_data_callback() No Stored Value:
        """
        msg = {"message_id":"1","sender_entity_id":"3","key":"key1"}
        self.test_subject.retrieve_data_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{"error":"Key key1 does not exist.","success":False})


    def test_remove_data_callback(self):
        """
        DataStoragePlugin.remove_data_callback() Test plan:
            - send message with no key.  response should contain error
            - with no records matching filter (entity_id or not existing)
            -   success should be false, error set
            - with 1 record matching filter
            -   remove should send response with success = true, not one of 
        """
        msg = {"message_id":"1","sender_entity_id":"3","key":"key1"}
        self.test_subject.db.insert({"key":"key1","data":"data1","entity_id":"3"})
        self.test_subject.db.insert({"key":"key1","data":"data2","entity_id":"2"})
        
        self.test_subject.remove_data_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{ "success":True})
        self.test_subject.db.find().count().should.equal(1)
        
    def test_remove_data_callback_no_key(self):
        """
        DataStoragePlugin.remove_data_callback() No Key:
        """
        msg = {"message_id":"1","sender_entity_id":"3"}
        self.test_subject.remove_data_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{"error":"Error: remove_data message must contain a 'key'","success":False})
        
    def test_remove_data_callback_does_not_exist(self):
        """
        DataStoragePlugin.remove_data_callback() Does Not Exist:
        """
        msg = {"message_id":"1","sender_entity_id":"3","key":"key1"}
        self.test_subject.remove_data_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{"error":"Key key1 does not exist.", "success":False})

        
        
        
    
    
