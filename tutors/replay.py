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

from hpitclient import Tutor

class ReplayTutor(Tutor):
    def __init__(self, entity_id, api_key, logger, run_once=None, args=None):
        """
        Constructor: takes entity, api_key, logger, and run_once, like other tutors,
        but in addition, a JSON string of arguments.  These arguments are:
            beforeTime: a date in the form of 02-11-2020 14:03:09 that indicates only messages
                should be replayed that happened before this date.
            afterTime:  like before time, but specifies the date that only messages created after
                should be replayed
            filter:  (required) a JSON object that serves as the custom filter for the MongoDB messages
            db_name: (required)  The name of the database to look in
        """
        super().__init__(entity_id, api_key, self.main_callback, run_once=run_once)
        self.run_once = run_once
        self.logger = logger
        
        if args: 
            self.args = json.loads(args[1:-1])
        else:
            raise NoArgumentsException("A JSON string of arguments should be passed to the tutor.")
        
        try:
            self.db_name = self.args["db_name"]
        except KeyError:
            raise InvalidArgumentsException("Args need to at least contain db_name")
            
        try:
            filter = self.args["filter"]
        except KeyError:
            raise InvalidArgumentsException("Args need to at least contain filter")
        
    def main_callback(self):
        client = MongoClient()
        messages = client[self.db_name].messages
        if self.logger:
            self.logger.debug("filter is: " + str(self.args["filter"]))

        for message in messages.find(self.args["filter"]):
            
            criteriaFlag = 0
            successFlag = 0
            documentTime = datetime.strptime(message["time_created"], "%m-%d-%Y %H:%M:%S")
            documentTime = documentTime.replace(tzinfo=pytz.utc)
            
            if "afterTime" in self.args:
                criteriaFlag = criteriaFlag | 1 
                afterTime  = datetime.strptime(self.args["afterTime"], "%m-%d-%Y %H:%M:%S")
                afterTime = afterTime.replace(tzinfo=pytz.utc)
                if afterTime <= documentTime:
                    successFlag  = successFlag | 1
                    
            if "beforeTime" in self.args:
                criteriaFlag = criteriaFlag | 2
                beforeTime = datetime.strptime(self.args["beforeTime"], "%m-%d-%Y %H:%M:%S")
                beforeTime = beforeTime.replace(tzinfo=pytz.utc)
                if beforeTime >= documentTime:
                    successFlag = successFlag | 2
            
            if criteriaFlag == successFlag:
                self.send(message["event"],message["payload"])
                if self.logger:
                    self.logger.debug("REPLAYED: "+str(message))
            
        
        if self.run_once:
            return False
        else:
            return True
