from hpitclient import Plugin

from pymongo import MongoClient
from bson.objectid import ObjectId
import bson

from threading import Timer

from datetime import datetime

import time

from hpit.management.settings_manager import SettingsManager
settings = SettingsManager.get_plugin_settings()

import requests

class TransactionManagementPlugin(Plugin):
    def __init__(self, entity_id, api_key, logger, args = None):
        super().__init__(entity_id, api_key) 
        self.logger = logger
    
        self.tracker = {}
    
    def post_connect(self):
        self.register_transaction_callback(self.transaction_callback_method)
        
    
    def transaction_callback_method(self, message):
        try:
            #collects the four responses sent concurrently
            def collect_remaining_callback(response):
                if "responder" not in response:
                    return 
                
                if self.logger:
                    self.send_log_entry("INFO: Got response from " + response["responder"])
                
                self.tracker[message["message_id"]][response["responder"] + "_response"] = response
                l = ["problem_response" in self.tracker[message["message_id"]],
                     "kt_response" in self.tracker[message["message_id"]],
                     "boredom_response" in self.tracker[message["message_id"]],
                     "hf_response" in self.tracker[message["message_id"]]
                ]
    
                if all(l):
                    self.send_response(message["message_id"], self.tracker[message["message_id"]])
                    del self.tracker[message["message_id"]]
            
            #sends the rest of the messages
            def send_rest_of_messages(student_id,session_id,skill_ids):
                if self.logger:
                    self.send_log_entry("INFO: Sending other messages...")
                message["student_id"] = student_id
                message["session_id"] = session_id
                message["skill_ids"] = skill_ids
                
                self.send("tutorgen.kt_transaction",message,collect_remaining_callback)
                self.send("tutorgen.hf_transaction",message,collect_remaining_callback)
                self.send("tutorgen.boredom_transaction",message,collect_remaining_callback)
                self.send("tutorgen.problem_transaction",message,collect_remaining_callback)
            
            #records the student_id, sets value in tracker
            def student_callback(response):
                if self.logger:
                    self.send_log_entry("RECV: student response with message: " + str(response))
                if "error" in response:
                    if "already_errored" not in self.tracker[message["message_id"]]:
                        self.send_response(message["message_id"],{
                            "error":response["error"]
                        })
                        self.tracker[message["message_id"]]["already_errored"] = True
                        return
                else:
                    self.tracker[message["message_id"]]["student_id"] = response["student_id"]
                    self.tracker[message["message_id"]]["session_id"] = response["session_id"]
                    self.tracker[message["message_id"]]["student_response"] = response
                    if "skill_response" in self.tracker[message["message_id"]]:
                        send_rest_of_messages(
                            self.tracker[message["message_id"]]["student_id"],
                            self.tracker[message["message_id"]]["session_id"],
                            self.tracker[message["message_id"]]["skill_ids"]
                        )
                        
            
            #records the skill_ids, sets value in tracker.
            def skill_callback(response):
                if self.logger:
                    self.send_log_entry("RECV: skill response with message: " + str(response))
                    
                if "error" in response:
                    if "already_errored" not in self.tracker[message["message_id"]]:
                        self.send_response(message["message_id"],{
                            "error":response["error"]
                        })
                        self.tracker[message["message_id"]]["already_errored"] = True
                        return
                else:
                    self.tracker[message["message_id"]]["skill_ids"] = response["skill_ids"]
                    self.tracker[message["message_id"]]["skill_response"] = response
                    if "student_response" in self.tracker[message["message_id"]]:
                        send_rest_of_messages(
                            self.tracker[message["message_id"]]["student_id"],
                            self.tracker[message["message_id"]]["session_id"],
                            self.tracker[message["message_id"]]["skill_ids"]
                        )
                        
    
            #this executes first
            if self.logger:
                self.send_log_entry("RECV: transaction with message: " + str(message))
            
            message["orig_sender_id"] = message["sender_entity_id"]
            self.tracker[message["message_id"]] = {}
            
            student_id = None
            session_id = None
            skill_ids = None
            
            self.send("tutorgen.skill_transaction",message, skill_callback)
            self.send("tutorgen.student_transaction",message, student_callback)
        
        except Exception as e:
            self.send_response(message["message_id"],{
                "error":"Unexpected error; please consult the docs. " + str(e)      
            })
        
        
        
    
    

