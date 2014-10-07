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

class LoadTestingTutor(Tutor):
    """
    This tutor runs an integration test agains the following plugins:
        - problem generator
        - problem manager
        - student model manager
        - knowledge tracer
        - skill manager
    """
    
    def __init__(self, entity_id, api_key, logger, run_once=None, args = None):
        super().__init__(entity_id, api_key, self.main_callback, run_once=run_once)
        self.run_once = run_once
        self.logger = logger

        self.students = []
        self.female_first_names = ["Mary", "Junell", "Elizabeth", "Ashley", "Rebecca", "Catherine", "Eris", "Fatima"]
        self.male_first_names = ["Raymond", "Robert", "Ted", "John", "Jeff", "Josh", "Joe", "Chris", "Matthew", "Mark", "Luke"]
        self.last_names = ["Smith", "Barry", "Chandler", "Carmichael", "Nguyen", "Blink", "Sauer", "Slavins", "O'Reilly", "Ledermann"]
        self.genders = ["Male", "Female", "Other"]
        self.address_names = ["Hague", "Forest Green", "Carothers", "Deerpark", "Warren", "Ogden", "Pearl", "Park"]
        self.address_suffix = ["Avenue", "Drive", "Street", "Boulevard", "Lane"]
        self.cities = ["Columbus", "Covington", "Richmond", "Lexington", "Louisville", "Vaudeville", "Lewisburg", "Leesville"]
        self.states = ["Alaska", "California", "Florida", "Ohio", "Indiana", "Nevada", "Virgina", "Pennsylvania"]

        self.problem_library = {}

        self.actions = [
            self.create_student, 
            self.create_problem, 
            self.create_skill,
            self.student_solve,
            self.student_failure,
            self.student_information
        ]


    def post_connect(self):
        self.send('pg_list_problems', {}, self.list_problems_callback)

        
    def pre_disconnect(self):
        for sk in self.skills:
            self.send('kt_reset', {
                'skill_id': self.skill_ids[sk],
                'student_id':self.student_id,
                })


    def create_student(self):
        """
        Emulate a student logging onto the tutor.
        """
        if len(self.students) >= 1000:
            del self.actions[self.create_student]
            return

        student_info = {
            'last_name': random.choice(self.last_names),
            'address': ' '.join([
                str(random.randint(100, 100000)), 
                random.choice(self.address_names), 
                random.choice(self.address_suffix)]),
            'city': random.choice(self.cities),
            'states': random.choice(self.states),
            'zip': '-'.join([
                str(random.randint(10000, 100000)),
                str(random.randint(1000, 10000))]),
            'country': "United States",
            'gender': random.choice(self.genders),
        }

        if student_info['gender'] == "Male":
            student_info['first_name'] = random.choice(self.male_first_names)
        elif student_info['gender'] == "Female":
            student_info['first_name'] = random.choice(self.female_first_names)
        else:
            student_info['first_name'] = random.choice(self.male_first_names + self.female_first_names)

        student_info['full_name'] = ' '.join([student_info['first_name'], student_info['last_name']])

        self.send("add_student", student_info, self.create_student_callback)


    def create_problem(self):
        """
        Emulate a student asking for a problem.
        """
        pass

    def create_skill(self):
        """
        Emulate a tutor finding an existing problem for a student to solve.
        """

    def student_solve(self):
        """
        Emulate a student solving a problem.
        """
        pass

    def student_failure(self):
        """
        Emulate a student failing to solve a problem.
        """
        pass

    def student_information(self):
        """
        Emulate a student requesting information about his student model.
        """
        pass


    def list_problems_callback(self, response):
        """
        Callback for listing the problems available in the problem generator.
        """
        self.send_log_entry("RECV: pg_list_problems response recieved. " + str(response))
        self.logger.debug("RECV: pg_list_problems response recieved. " + str(response))

        for subject_name, categories in response.items():
            for category_name, skills in categories.items():
                for skill_name in skills:
                    sm_skill_name = '_'.join([subject_name, category_name, skill_name])

                    self.problem_library[sm_skill_name] = {
                        'subject': subject_name,
                        'category': category_name,
                        'skill_name': skill_name,
                        'skill_id': None
                    }

                    self.send('get_skill_id', {'skill_name': sm_skill_name}, self.get_skill_id_callback)


    def get_skill_id_callback(self, response):
        """
        Callback for getting the assigned skill id for a particular skill from this tutor.
        """
        problem_skill = self.problem_library[response['skill_name']]
        problem_skill['skill_id'] = response['skill_id']


    def create_student_callback(self):
        """
        Callback for the create student event.
        """
        self.send_log_entry("RECV: add_student response recieved. " + str(response))
        self.logger.debug("RECV: add_student response recieved. " + str(response))
        self.students[response["student_id"]] = response["attributes"]


    def main_callback(self):
        if self.problem_library:
            action = random.choice(self.actions)
            action()

        return True

        if self.student_id == None:
            return True
        for k,v in self.skill_ids.items():
            if v == None:
                return True
   
        for sk in self.skills:
            if 90 < random.randint(0, 100):
                correct = random.randint(0, 100)
                self.send('kt_trace', {
                    'skill_id': self.skill_ids[sk],
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

        
    def get_skills_callback(self,response):
        self.skill_ids[response["skill_name"]] = response["skill_id"]
        self.send('kt_set_initial', {
                'skill_id': response["skill_id"],
                'probability_known': random.randint(0, 1000) / 1000.0,
                'probability_learned': random.randint(0, 1000) / 1000.0,
                'probability_guess': random.randint(0, 1000) / 1000.0,
                'probability_mistake': random.randint(0, 1000) / 1000.0,
                'student_id':self.student_id
                }, self.initial_response_callback)
