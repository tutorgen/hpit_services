from hpitclient import Plugin

from pymongo import MongoClient
import pymongo

from bson import ObjectId
import bson

import time
import json

from hpit.management.settings_manager import SettingsManager
settings = SettingsManager.get_plugin_settings()

from datetime import datetime

import math

class BoredomDetectorPlugin(Plugin):
    
    def __init__(self, entity_id, api_key, logger, args = None):
        super().__init__(entity_id, api_key)
        self.logger = logger
        self.mongo = MongoClient(settings.MONGODB_URI)
        self.db = self.mongo[settings.MONGO_DBNAME].hpit_boredom_detection
        
        self.RECORD_THRESHOLD = 5
        
        if args:
            try:
                self.args = json.loads(args[1:-1])
                self.transaction_manager_id = self.args["transaction_management"]
            except KeyError:
                raise Exception("Failed to initialize; invalid transaction_management not in args")
        else:
            raise Exception("Failed to initialize; no args")
        
    def post_connect(self):
        super().post_connect()
        
        self.subscribe({
            "tutorgen.update_boredom":self.update_boredom_callback,
            "tutorgen.boredom_transaction":self.transaction_callback_method
        })
        
    def boredom_calculation(self,student_id,time):
            
        bored = False


        #"Thu, 28 Nov 2013 22:28:43 GMT"
        insert_time = datetime.strptime(time, "%a, %d %b %Y %H:%M:%S GMT")

        self.db.insert({
            "student_id":student_id,
            "time": insert_time,
        })
        
        dt_sum = 0
        dt_mean = 0
        dt_std_dev = 0
        dts = []
        
        records = list(self.db.find({"student_id":student_id},limit=1000).sort("time",pymongo.DESCENDING))
        if len(records) > 1:
            for xx in range(0,len(records)-1):
                dt = (records[xx]["time"] - records[xx+1]["time"]).total_seconds();
                dt_sum += dt
                dts.append(dt)
  
            dt_mean = float(dt_sum) / (len(records)-1)
            var_squared = 0
            var_squared_sum =0
            
            for xx in dts:
                var_squared = abs((xx-dt_mean))**2
                var_squared_sum += var_squared
                
            dt_std_dev = math.sqrt(float(var_squared_sum) / (len(records)-1))
            
            
            if abs(dt_mean - ((records[0]["time"] - records[1]["time"]).total_seconds())) > abs(dt_mean - dt_std_dev):
                bored = True
        
        return bored
        
        
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
            
        bored = self.boredom_calculation(student_id,message["time_created"])
        
        self.send_response(message["message_id"],{
            "bored":bored,
        })
        
    def transaction_callback_method(self,message):
        if self.logger:
            self.send_log_entry("RECV: update_boredom with message: " + str(message))
            
        if message["sender_entity_id"] != self.transaction_manager_id:
            self.send_response(message["message_id"],{
                    "error" : "Access denied",
                    "responder":"boredom",
            })
            return 
        
        bored = False
        
        try:
            student_id = str(message["student_id"])
        except KeyError:
            self.send_response(message["message_id"],{
                "error":"boredom detector requires a 'student_id'",
                "responder":"boredom"}
            )
        
        bored = self.boredom_calculation(student_id,message["time_created"])
        
        response = {}
        response["bored"] = bored
        response["responder"] = "boredom"
        self.send_response(message["message_id"],response)
        
