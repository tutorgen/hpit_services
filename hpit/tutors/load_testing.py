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
        self.poll_wait = 100

        self.students = {}
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
            self.student_solve,
            self.student_failure,
            self.student_information
        ]

    def post_connect(self):
        self.send('pg_list_problems', {}, self.list_problems_callback)

    def get_skill_name_for_problem(self, problem):
        return '_'.join([
            problem['subject'], 
            problem['category'],
            problem['skill']
        ])


    def get_random_problem(self):
        """
        Gets a random problem_definition and problem
        """
        sm_skill_name, problem_def = random.choice(list(self.problem_library.items()))

        #May not have generated any problems yet.
        if 'problems' not in problem_def:
            return None;

        #May not have generated any problems yet.
        if not problem_def['problems']:
            return None;

        problem = random.choice(problem_def['problems'])

        return (sm_skill_name, problem_def, problem)


    def create_student(self):
        """
        Emulate a student logging onto the tutor.
        """
        if len(self.students) >= 1000:
            self.actions.remove(self.create_student)
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

        self.send("add_student", {'attributes': student_info}, self.create_student_callback)


    def create_problem(self):
        """
        Emulate a student asking for a problem.
        """
        self.send('pg_generate_problem', {'count': 3}, self.create_problem_callback)


    def student_solve(self):
        """
        Emulate a student solving a problem.
        """
        if not self.students:
            return

        random_problem = self.get_random_problem()

        if not random_problem:
            return

        sm_skill_name, problem_def, problem = random_problem

        student_id = random.choice(list(self.students.keys()))

        self.send('add_problem_worked', {
            'student_id': student_id,
        }, self.add_problem_worked_callback)

        self.send('kt_trace', {
            'student_id': student_id,
            'skill_id': problem_def['skill_id'],
            'correct': True
        }, self.kt_trace_callback)


    def student_failure(self):
        """
        Emulate a student failing to solve a problem.
        """
        if not self.students:
            return

        random_problem = self.get_random_problem()

        if not random_problem:
            return

        sm_skill_name, problem_def, problem = random_problem

        student_id = random.choice(list(self.students.keys()))

        self.send('add_problem_worked', {
            'student_id': student_id,
        }, self.add_problem_worked_callback)

        self.send('kt_trace', {
            'student_id': student_id,
            'skill_id': problem_def['skill_id'],
            'correct': False
        }, self.kt_trace_callback)


    def student_information(self):
        """
        Emulate a student requesting information about his student model.
        """
        if not self.students:
            return

        student_id = random.choice(list(self.students.keys()))

        self.send('get_student_model', {'student_id': student_id}, self.get_student_model_callback)


    def list_problems_callback(self, response):
        """
        Callback for listing the problems available in the problem generator.
        """
        self.send_log_entry("RECV: pg_list_problems response recieved. " + str(response))
        self.logger.debug("RECV: pg_list_problems response recieved. " + str(response))

        for subject_name, categories in response.items():
            for category_name, skills in categories.items():
                for skill_name in skills:
                    new_problem_def = {
                        'subject': subject_name,
                        'category': category_name,
                        'skill': skill_name,
                        'skill_id': None
                    }

                    sm_skill_name = self.get_skill_name_for_problem(new_problem_def)
                    self.problem_library[sm_skill_name] = new_problem_def

                    self.send('get_skill_id', {'skill_name': sm_skill_name}, self.get_skill_id_callback)


    def get_skill_id_callback(self, response):
        """
        Callback for getting the assigned skill id for a particular skill from this tutor.
        """
        self.send_log_entry("RECV: get_skill_id response recieved. " + str(response))
        self.logger.debug("RECV: get_skill_id response recieved. " + str(response))

        problem_skill = self.problem_library[response['skill_name']]
        problem_skill['skill_id'] = response['skill_id']


    def create_student_callback(self, response):
        """
        Callback for the create student event.
        """
        self.send_log_entry("RECV: add_student response recieved. " + str(response))
        self.logger.debug("RECV: add_student response recieved. " + str(response))

        self.students[response["student_id"]] = response["attributes"]


    def create_problem_callback(self, response):
        """
        Callback for generating problems.
        """
        self.send_log_entry("RECV: pg_generate_problem response recieved. " + str(response))
        self.logger.debug("RECV: pg_generate_problem response recieved. " + str(response))

        problems = response['problems']
        for p in problems:
            sm_skill_name = self.get_skill_name_for_problem(p)

            problem_def = self.problem_library[sm_skill_name]
            if 'problems' not in problem_def:
                problem_def['problems'] = []

            problem_name = '/'.join([sm_skill_name, str(uuid.uuid4())])
            problem_def['problems'].append({
                'problem_name': problem_name,
                'problem_text': p['problem_text'],
                'answer_text': p['answer_text']
                })

            self.send('add_problem', {
                'problem_name': problem_name,
                'problem_text': p['problem_text']
                }, self.add_problem_callback)


    def add_problem_callback(self, response):
        self.send_log_entry("RECV: add_problem_callback response recieved. " + str(response))
        self.logger.debug("RECV: add_problem_callback response recieved. " + str(response))

        if not response['success']:
            raise Exception("Could not add problem to problem manager.")

        sm_skill_name, unique_id = response['problem_name'].split('/')

        problem_def = self.problem_library[sm_skill_name]

        problem_match = list(
            filter(
                lambda x: x['problem_name'] == response['problem_name'], 
                problem_def['problems']
            )
        )

        if len(problem_match) == 0:
            raise Exception("Rouge Add Problem Callback")
        elif len(problem_match) != 1:
            raise Exception("More than 1 problem match found against uuid generated.")
        else:
            problem_match[0]['problem_id'] = response['problem_id']


    def get_student_model_callback(self, response):
        self.send_log_entry("RECV: get_student_model response recieved. " + str(response))
        self.logger.debug("RECV: get_student_model response recieved. " + str(response))

        student_id = response['student_id']

        if student_id not in self.students:
            return

        self.students[student_id]['student_model'] = response['student_model']


    def add_problem_worked_callback(self, response):
        self.send_log_entry("RECV: add_problem_worked response recieved. " + str(response))
        self.logger.debug("RECV: add_problem_worked response recieved. " + str(response))


    def kt_trace_callback(self, response):
        self.send_log_entry("RECV: kt_trace response recieved. " + str(response))
        self.logger.debug("RECV: kt_trace response recieved. " + str(response))


    def main_callback(self):
        if self.problem_library:
            for i in range(0, 100):
                action = random.choice(self.actions)
                self.logger.debug("New Action: " + str(action))
                action()

        return True
