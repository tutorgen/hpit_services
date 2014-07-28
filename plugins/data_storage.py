from hpitclient import Plugin

from pymongo import MongoClient

class DataStoragePlugin(Plugin):

    def __init__(self, entity_id, api_key, logger, args=None):
        super().__init__(entity_id, api_key)
        self.logger = logger
        self.mongo = MongoClient('mongodb://localhost:27017/')
        self.db = self.mongo.hpit_data_storage.data

    def post_connect(self):
        super().post_connect()

        self.subscribe(
            store_data=self.store_data_callback,
            retrieve_data=self.retrieve_data_callback,
            remove_data=self.remove_data_callback)

    def store_data_callback(self, message):
        if self.logger:
            self.logger.debug("STORE_DATA")
            self.logger.debug(message)
        try:
            key = message["key"]
            data = message["data"]
        except KeyError:
            self.send_response(message["message_id"],{"error":"Error: store_data message must contain a 'key' and 'data'"})
            return
            
        insert_id = self.db.insert({"key":key,"data":data})
        self.send_response(message["message_id"],{"insert_id":insert_id})

    def retrieve_data_callback(self, message):
        if self.logger:
            self.logger.debug("RETRIEVE_DATA")
            self.logger.debug(message)
        
        try:
            key = message["key"]
        except KeyError:
            self.send_response(message["message_id"],{"error":"Error: retrieve_data message must contain a 'key'"})
            return
            
        data = self.db.find_one({"key":key})
        
        self.send_response(message["message_id"],{"data":data})

    def remove_data_callback(self, message):
        if self.logger:
            self.logger.debug("REMOVE_DATA")
            self.logger.debug(message)
        
        try:
            key  = message["key"]
        except KeyError:
            self.send_response(message["message_id"],{"error":"Error: remove_data message must contain a 'key'"})
            return
            
        response = self.db.remove({"key":key})
        
        self.send_response(message["message_id"],{"status":response})
