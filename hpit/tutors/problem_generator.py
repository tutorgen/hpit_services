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

class ProblemGeneratorTutor(Tutor):
    def __init__(self, entity_id, api_key, logger, run_once=None, args = None):
        super().__init__(entity_id, api_key, self.main_callback, run_once=run_once)
        self.logger = logger
        self.problem_list = None
       

    def post_connect(self):
        self.send("pg_list_problems",{},self.list_problems_callback)


    def request_new_problem(self):
        if not self.problem_list:
            return None

        subject = random.choice(list(self.problem_list.keys()))
        category = random.choice(list(self.problem_list[subject].keys()))
        skill = random.choice(list(self.problem_list[subject][category]))
        count = random.choice(range(0, 10))

        self.send("pg_generate_problem", {
            'subject': subject,
            'category': category,
            'skill': skill,
            'count': count
        }, self.generate_problem_callback)


    def list_problems_callback(self, response):
        self.send_log_entry("RECV: pg_list_problems response recieved. " + str(response))

        self.problem_list = response
        self.request_new_problem()


    def generate_problem_callback(self, response):
        self.send_log_entry("RECV: pg_generate_problem response recieved. " + str(response))
        print("NEW PROBLEMS RECIEVED")
        try:
            for p in response['problems']:
                print(p['problem_text'])
        except Exception as e:
            import pdb; pdb.set_trace()

        self.request_new_problem()

    def main_callback(self):
        return True
