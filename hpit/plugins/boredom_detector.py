from hpitclient import Plugin

from pymongo import MongoClient

from bson import ObjectId
import bson

import time
import json

from hpit.management.settings_manager import SettingsManager
settings = SettingsManager.get_plugin_settings()

class BoredomDetectorPlugin(Plugin):
    
    def __init__(self, entity_id, api_key, logger, args = None):
        super().__init__(entity_id, api_key)
        self.logger = logger
        self.mongo = MongoClient(settings.MONGODB_URI)
        self.db = self.mongo[settings.MONGO_DBNAME].hpit_boredom_detection
        
    def post_connect(self):
        super().post_connect()
        
        self.subscribe({
            "tutorgen.update_boredom":self.update_boredom_callback,
            "tutorgen.boredom_transaction":self.transaction_callback_method
        })
        
    def update_boredom_callback(self,message):
        pass
    
    def transaction_callback_method(self,message):
        pass
