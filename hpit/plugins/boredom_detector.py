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

class BoredomParameterException(Exception):
    #thrown when a message does not have the required parameters for a boredom model 
    pass

class BoredomDetectorPlugin(Plugin):
    
    def __init__(self, entity_id, api_key, logger, args = None):
        super().__init__(entity_id, api_key)
        self.logger = logger
        self.mongo = MongoClient(settings.MONGODB_URI)
        self.db = self.mongo[settings.MONGO_DBNAME].hpit_boredom_detection
        
        self.RECORD_THRESHOLD = 5
        self.threshold = .75 #this is the value the probability must be above to return "true"
        
        self.boredom_models = {
            "simple":self._simple_boredom_calculation,
            "complex":self._complex_boredom_calculation
        }
        self.boredom_calculation = self._simple_boredom_calculation
        
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
            "tutorgen.set_boredom_threshold":self.set_boredom_threshold,
            "tutorgen.set_boredom_model":self.set_boredom_model,
            "tutorgen.update_boredom":self.update_boredom_callback,
            "tutorgen.boredom_transaction":self.transaction_callback_method
        })
        
    def _simple_boredom_calculation(self,message):
        
        try:
            student_id = str(message["student_id"])
        except KeyError:
            raise BoredomParameterException("Simple boredom model requires a 'student_id'")
        
        
        #this is an example of a boredom model.  it should take a message as its params, and return a float
        bored = False

        student_id = message["student_id"]
        time = message["time_created"]
        
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
        
        if bored == True:
            return 1.0
        else:
            return 0.0
            
    def _complex_boredom_calculation(self,message):
        """
        TODO: put the more complex boredom calculation here"
        """
        return 1.0
    
    def set_boredom_threshold(self,message):
        if self.logger:
            self.send_log_entry("RECV: set_boredom_threshold with message: " + str(message))
            
        try:
            threshold = message["threshold"]
        except KeyError:
            self.send_response(message["message_id"],{
               "error":"set_boredom_threshold requires a 'threshold'",
            })
            return
            
        if threshold < 0 or threshold >1:
            self.send_response(message["message_id"],{
               "error":"threshold must be decimal value between 0 and 1.",
            })
            return
            
            
        self.threshold = threshold
        
        self.send_response(message["message_id"],{
            "status":"OK",
        })
        
    def set_boredom_model(self,message):
        if self.logger:
            self.send_log_entry("RECV: set_boredom_threshold with message: " + str(message))
            
        try:
            model_name = message["model_name"]
        except KeyError:
            self.send_response(message["message_id"],{
               "error":"set_boredom_model requires a 'model_name'",
            })
            return
        if model_name in self.boredom_models:
            self.boredom_calculation = self.boredom_models[model_name]
        else:
            self.send_response(message["message_id"],{
               "error":"set_boredom_model unknown 'model_name'",
            })
            return
        
        self.send_response(message["message_id"],{
            "status":"OK",
        })
    
        
    def update_boredom_callback(self,message):
        if self.logger:
            self.send_log_entry("RECV: update_boredom with message: " + str(message))
        
        return_type = "bool"
        if "return_type" in message:
            return_type = message["return_type"]
        
        if return_type not in ["bool","decimal"]:
            self.send_response(message["message_id"],{
               "error":"update_boredom 'return_type' must be 'bool' or 'decimal'",
            })
            return
        
        bored = None
        try:
            bored_prob = self.boredom_calculation(message)
        except BoredomParameterException as e:
            self.send_response(message["message_id"],{
                    "error":str(e)
                })
            return

        if return_type == "bool":
            if bored_prob >= self.threshold:
                bored = True
            else:
                bored = False
        else:
            bored = bored_prob
        
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
        response["threshold"] = self.threshold
        response["responder"] = "boredom"
        self.send_response(message["message_id"],response)
        
