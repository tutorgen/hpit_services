from hpitclient import Plugin

from pymongo import MongoClient
from bson.objectid import ObjectId

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
        if self.logger:
            self.logger.debug("GET_NAME")
            self.logger.debug(message)
            
        try:
            skill_id = message["skill_id"]
        except KeyError:
            self.send_response(message["message_id"],{
                "error":"Message must contain a 'skill_id'",       
            })
            return
        
        skill = self.db.find_one({"_id":ObjectId(str(skill_id))})
        if not skill:
            self.send_response(message["message_id"],{
                "error":"Skill with id " + str(skill_id) + " does not exist.",     
            })
            return
            
        else:
            self.send_response(message["message_id"],{
                "skill_name":str(skill["skill_name"]),
                "skill_id":str(skill["_id"])
            })

    def get_skill_id_callback(self, message):
        if self.logger:
            self.logger.debug("GET_ID")
            self.logger.debug(message)
            
        try:
            skill_name = message["skill_name"]
        except KeyError:
            self.send_response(message["message_id"],{
                "error":"Message must contain a 'skill_name'",      
            })
            return
            
        skill = self.db.find_one({"skill_name":skill_name})
        if not skill:
            skill_id = self.db.insert({"skill_name":skill_name})
            self.send_response(message["message_id"],{
                "skill_name": skill_name,
                "skill_id": str(skill_id),
            })
        else:
            self.send_response(message["message_id"],{
                "skill_name": skill_name,
                "skill_id": str(skill["_id"]),
            })
            
            
            
