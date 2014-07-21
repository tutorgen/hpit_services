from hpitclient import Plugin

from pymongo import MongoClient

class DataStoragePlugin(Plugin):

    def __init__(self, entity_id, api_key, logger, args=None):
        super().__init__(entity_id, api_key)
        self.logger = logger
        self.mongo = MongoClient('mongodb://localhost:27017/')
        self.db = self.mongo.hpit_data_storage


    def post_connect(self):
        super().post_connect()

        self.subscribe(
            store_data=self.store_data_callback,
            retrieve_data=self.retrieve_data_callback,
            remove_data=self.remove_data_callback)

    def store_data_callback(self, message):
        self.logger.debug("STORE_DATA")
        self.logger.debug(message)

    def retrieve_data_callback(self, message):
        self.logger.debug("RETRIEVE_DATA")
        self.logger.debug(message)

    def remove_data_callback(self, message):
        self.logger.debug("REMOVE_DATA")
        self.logger.debug(message)
