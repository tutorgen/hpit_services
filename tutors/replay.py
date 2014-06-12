import argparse
import logging
import os
import random
import uuid
from datetime import datetime
from time import sleep
import json
import sys
from pymongo import MongoClient
from bson.objectid import ObjectId
import pytz

from client import Tutor

class ReplayTutor(Tutor):
    def __init__(self, name, logger, run_once=None, args = None):
        super().__init__(name, self.main_callback, run_once=run_once)
        self.run_once = run_once
        self.logger = logger
        self.args = json.loads(args[1:-1]) #trim off the quotes
        
    def main_callback(self):
        client = MongoClient()
        messages = client.hpit_development.messages
        self.logger.debug("filter is: " + str(self.args["filter"]))
        for message in messages.find(self.args["filter"]):
            
            criteriaFlag = 0
            successFlag = 0
            documentTime = ObjectId(message["_id"]).generation_time
            documentTime = documentTime.replace(tzinfo=pytz.utc)
            if "afterTime" in self.args:
                criteriaFlag = criteriaFlag | 1 
                afterTime  = datetime.strptime(self.args["afterTime"], "%m-%d-%Y %H:%M:%S")
                afterTime = afterTime.replace(tzinfo=pytz.utc)
                if afterTime <= documentTime:
                    successFlag  = criteriaFlag | 1
                    
            if "beforeTime" in self.args:
                criteriaFlag = criteriaFlag | 2
                beforeTime = datetime.strptime(self.args["beforeTime"], "%m-%d-%Y %H:%M:%S")
                beforeTime = beforeTime.replace(tzinfo=pytz.utc)
                if beforeTime >= documentTime:
                    successFlag = criteriaFlag | 2
                    
            if criteriaFlag == successFlag:
                #self.send(message["event"],message["payload"])
                self.logger.debug("REPLAYED: "+str(message))
            
        
        if self.run_once:
            return False
        else:
            return True
   
        
    def run(self):
        self.connect()
        
        self.start()
        
        self.disconnect()
        
    
