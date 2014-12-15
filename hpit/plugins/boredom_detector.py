from hpitclient import Plugin

from pymongo import MongoClient

from bson import ObjectId
import bson

import time
import json

from hpit.management.settings_manager import SettingsManager
settings = SettingsManager.get_plugin_settings()

from datetime import datetime

class BoredomDetectorPlugin(Plugin):
    
    def __init__(self, entity_id, api_key, logger, args = None):
        super().__init__(entity_id, api_key)
        self.logger = logger
        self.mongo = MongoClient(settings.MONGODB_URI)
        self.db = self.mongo[settings.MONGO_DBNAME].hpit_boredom_detection
        
        self.RECORD_THRESHOLD = 5
        
    def post_connect(self):
        super().post_connect()
        
        self.subscribe({
            "tutorgen.update_boredom":self.update_boredom_callback,
            "tutorgen.boredom_transaction":self.transaction_callback_method
        })
        
    def update_boredom_callback(self,message):
        if self.logger:
            self.send_log_entry("RECV: update_boredom with message: " + str(message))
        
        bored = False
        
        try:
            student_id = str(message["student_id"])
        except KeyError:
            self.send_response(message["message_id"],{
               "error":"update_boredom requires a 'student_id'",
            })
            return
            
        record = self.db.find_one({"student_id":student_id})
        if record:
            current_time = message["time_created"]
            last_reported_time = record["last_reported_time"]
            average_time_difference = record["average_time_difference"]
            sum_of_variance = record["sum_of_variance"]
            total_reports = record["total_reports"]
            
            time_difference = current_time - last_reported_time
            time_difference_microseconds = time_difference.microseconds
            import nose;nose.tools.set_trace()
            new_average = float(average_time_difference + time_difference_microseconds) / (total_reports + 1)
            new_sum_of_variance = sum_of_variance + (time_difference_microseconds - new_average)
            std_dev = float(new_sum_of_variance**2) / (total_reports + 1)
            
            if abs(time_difference_microseconds - new_average) > std_dev and total_reports > self.RECORD_THRESHOLD:
                bored = True
            
            self.db.update({"student_id":student_id},{
                    "$set": {
                        "last_reported_time": message["time_created"],
                        "average_time_difference": new_average,
                        "sum_of_variance": new_sum_of_variance,
                        "total_reports":total_reports +1,
                    }
            })
            
        else:
            self.db.insert({
                    "student_id":student_id,
                    "last_reported_time": message["time_created"],
                    "average_time_difference": 0,
                    "sum_of_variance": 0,
                    "total_reports":0,
                })
        
        self.send_response(message["message_id"],{
                    "bored":bored,
            })
        
    def transaction_callback_method(self,message):
        pass
