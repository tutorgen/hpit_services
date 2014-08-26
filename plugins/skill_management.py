from hpitclient import Plugin

from pymongo import MongoClient

from couchbase import Couchbase

class SkillManagementPlugin(Plugin):
    def __init__(self, entity_id, api_key, logger, args = None):
        super().__init__(entity_id, api_key)
        self.logger = logger
        self.mongo = MongoClient('mongodb://localhost:27017/')
        self.db = self.mongo.hpit.hpit_skills
        
        self.cache = Couchbase.connect(bucket = "default", host = "127.0.0.1")

    def post_connect(self):
        super().post_connect()
        
        self.subscribe(
            get_skill_name=self.get_skill_name_callback,
            get_skill_id = self.get_skill_id_callback)

    #Skill Management Plugin
    def get_skill_name_callback(self, message):
        self.logger.debug("GET_NAME")
        self.logger.debug(message)

    def get_skill_id_callback(self, message):
        self.logger.debug("GET_ID")
        self.logger.debug(message)
