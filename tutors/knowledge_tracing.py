import argparse
import logging
import os
import random
import uuid
from datetime import datetime
from time import sleep
import json
import sys

from hpitclient import Tutor

class KnowledgeTracingTutor(Tutor):
    def __init__(self, entity_id, api_key, logger, run_once=None, args = None):
        super().__init__(entity_id, api_key, self.main_callback, run_once=run_once)
        self.run_once = run_once
        self.logger = logger
        self.skills = ['addition', 'subtraction', 'multiplication', 'division']
        self.skill_ids = {}
        for sk in self.skills:
            self.skill_ids[sk] = None
        
        self.student_id = None
      
        if args: 
            self.args = json.loads(args[1:-1])
        else:
            self.args = None
            
        random.seed()
        
    def post_connect(self):
        self.send("add_student",{},self.new_student_callback)
        
        
    def pre_disconnect(self):
        for sk in self.skills:
            self.send('kt_reset', {
                'skill': self.skill_ids[sk],
                'student_id':self.student_id,
                })

    def main_callback(self):
        if self.student_id == None:
            return True
        for k,v in self.skill_ids.items():
            if v == None:
                return True
   
        for sk in self.skills:
            if 90 < random.randint(0, 100):
                correct = random.randint(0, 100)
                self.send('kt_trace', {
                    'skill': self.skill_ids[sk],
                    'student_id':self.student_id,
                    'correct': True if 50 < random.randint(0, 100) else False
                    }, self.trace_response_callback)

        sleep(.1)

        return True

    def trace_response_callback(self, response):
        self.send_log_entry("RECV: kt_trace response recieved. " + str(response))
        self.logger.debug("RECV: kt_trace response recieved. " + str(response))

    def initial_response_callback(self, response):
        self.send_log_entry("RECV: kt_set_initial response recieved. " + str(response))
        self.logger.debug("RECV: kt_set_initial response recieved. " + str(response))
        
    def new_student_callback(self,response):
        self.student_id = response["student_id"]
        for sk in self.skills:
            self.send("get_skill_id",{"skill_name":sk},self.get_skills_callback)
            
    def get_skills_callback(self,response):
        self.skill_ids[response["skill_name"]] = response["skill_id"]
        self.send('kt_set_initial', {
                'skill': response["skill_id"],
                'probability_known': random.randint(0, 1000) / 1000.0,
                'probability_learned': random.randint(0, 1000) / 1000.0,
                'probability_guess': random.randint(0, 1000) / 1000.0,
                'probability_mistake': random.randint(0, 1000) / 1000.0,
                'student_id':self.student_id
                }, self.initial_response_callback)
