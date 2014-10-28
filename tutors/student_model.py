import logging
import random
from time import sleep
import json

from pymongo import MongoClient
from bson.objectid import ObjectId

from hpitclient import Tutor

from environment.settings_manager import SettingsManager
settings = SettingsManager.get_plugin_settings()


class StudentModelTutor(Tutor):
    def __init__(self, entity_id, api_key, logger, run_once=None, args = None):
        super().__init__(entity_id, api_key, self.main_callback, run_once=run_once)
        self.run_once = run_once
        self.logger = logger
        
        self.student_id = None
      
        if args: 
            self.args = json.loads(args[1:-1])
        else:
            self.args = None
            
        
        random.seed()
        
    def post_connect(self):
        sleep(5)

        self.student_id = "542d89b6cc48d1042416cb91"
        
    def pre_disconnect(self):
        pass

    def main_callback(self):
        self.send_log_entry("LOG")
        return False

        if self.student_id:
            self.send("tutorgen.get_student_model",{"student_id":str(self.student_id)},self.get_student_model_callback)
            self.student_id = None
        
        if self.run_once:
            return False
        else:
            return True

    def get_student_model_callback(self,response):
        self.send_log_entry("RECV: student_model response recieved. " + str(response))
