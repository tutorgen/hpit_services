import argparse
import logging
import os
import random
import uuid
from datetime import datetime
from time import sleep
import json
import sys
import threading

from hpitclient import Tutor

class Problem(object):
    
    def __init__(self,name,text):
        self.problem_name = name
        self.problem_text = text
        
        self.hpit_id = None
        
        self.steps = []
        
    def add_steps(self):
        if self.hpit_id == None:
            raise Exception("No problem ID yet")
            
        for xx in range(0,5):
            random_string = str(uuid.uuid4())
            self.steps.append(Step(random_string,self.hpit_id))
        
class Step(object):
    
    def __init__(self,text, problem_id):
        self.text = text
        self.problem_id = problem_id
        
        self.hpit_id = None
        
        self.skills = {} #mapping of skill names to ids
        
    def get_skill_list(self,correct):
        skill_list = {}
        for k,v in self.skills.items():
            skill_list[v] = correct
            
        return skill_list
        
        

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
        
        self.TOTAL_MESSAGES = 10
        self.TOTAL_PROBLEMS = 1
        self.TOTAL_SKILLS = 20
        self.SKILLS_PER_STEP = 4
        self.SEND_WAIT = 2
        
        self.run_once = run_once
        self.logger = logger

        self.students = {}
        self.current_student = None
        self.female_first_names = ["Mary", "Junell", "Elizabeth", "Ashley", "Rebecca", "Catherine", "Eris", "Fatima"]
        self.male_first_names = ["Raymond", "Robert", "Ted", "John", "Jeff", "Josh", "Joe", "Chris", "Matthew", "Mark", "Luke"]
        self.last_names = ["Smith", "Barry", "Chandler", "Carmichael", "Nguyen", "Blink", "Sauer", "Slavins", "O'Reilly", "Ledermann"]
        self.genders = ["Male", "Female", "Other"]
        self.address_names = ["Hague", "Forest Green", "Carothers", "Deerpark", "Warren", "Ogden", "Pearl", "Park"]
        self.address_suffix = ["Avenue", "Drive", "Street", "Boulevard", "Lane"]
        self.cities = ["Columbus", "Covington", "Richmond", "Lexington", "Louisville", "Vaudeville", "Lewisburg", "Leesville"]
        self.states = ["Alaska", "California", "Florida", "Ohio", "Indiana", "Nevada", "Virgina", "Pennsylvania"]

        self.problem_library = []

        self.actions = [
            self.create_student, 
            self.student_solve,
            self.student_information
        ]
        
        self.times = {}
        
        self.skills = {}
        
        self.message_count = 0
        self.response_count = 0
        
    def post_connect(self):
        print("problems")
        #create problems
        for xx in range(0,self.TOTAL_PROBLEMS):
            random_string = str(uuid.uuid4())
            p = Problem("Test Problem " + random_string,random_string)
            start = datetime.now()
            response = self.send_blocking("tutorgen.add_problem",{"problem_name":p.problem_name,"problem_text":p.problem_text})
            now = datetime.now()
            self.send_log_entry("RECV: add_problem response recieved. " + str(response) + " " + str(now-start) + " tutorgen.add_step")
            if response["success"] == False:
                continue
            else:
                p.hpit_id = response["problem_id"]
                p.add_steps()
                for step in p.steps:
                    step.problem_id = p.hpit_id
                    start = datetime.now()
                    response = self.send_blocking("tutorgen.add_step",{"problem_id":p.hpit_id,"step_text":step.text})
                    now = datetime.now()
                    self.send_log_entry("RECV: add_step response recieved. " + str(response) + " " + str(now-start) + " tutorgen.add_step")
            self.problem_library.append(p)
            
        print("skills") 
        #create skills
        batch_skills = []
        for xx in range(0,self.TOTAL_SKILLS):
            random_string = str(uuid.uuid4())
            self.skills[random_string] = None
            batch_skills.append(random_string)
        
        start = datetime.now()
        response = self.send_blocking("tutorgen.batch_get_skill_ids",{"skill_names":batch_skills})
        now = datetime.now()
        self.send_log_entry("RECV: batch_get_skills response recieved. " + str(response) + " " + str(now-start) + " tutorgen.batch_get_skill_ids")
        
        for k,v in response["skill_ids"].items():
            self.skills[k] = v
        
        for problem in self.problem_library:
            for step in problem.steps:
                for xx in range(0,self.SKILLS_PER_STEP):
                    sk = self.get_random_skill()
                    step.skills[sk[0]] = sk[1]
        
        print("student")
        #create a student
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
        
        start = datetime.now()
        response = self.send_blocking("tutorgen.add_student", {'attributes': student_info})
        now = datetime.now()
        
        self.send_log_entry("RECV: add student response recieved. " + str(response) + " " + str(now-start) + " tutorgen.add_student")
        self.current_student = response["student_id"]
        
        
        
        print("commence")

    def get_random_problem_step(self):
        random_problem = random.choice(self.problem_library)
        random_step = random.choice(random_problem.steps)
        return random_step
        
    def get_random_skill(self):
        skill_list = [(k,v) for k,v in self.skills.items()]
        return random.choice(skill_list)
    
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

        response = self.send("tutorgen.add_student", {'attributes': student_info}, self.create_student_callback)
        mid = response["message_id"]
        self.times[mid] = datetime.now()

    def student_solve(self):
        """
        Emulate a student solving a problem.
        """
        if not self.current_student:
            return

        random_step = self.get_random_problem_step()

        response = self.send('tutorgen.add_problem_worked', {
            'student_id': self.current_student,
            'problem_id': random_step.problem_id
        }, self.add_problem_worked_callback)
        
        mid = response["message_id"]
        self.times[mid] = datetime.now()

        correct = random.choice([True,False])
        skill_list = random_step.get_skill_list(correct)
        response = self.send('tutorgen.kt_batch_trace', {
            'student_id': self.current_student,
            'skill_list': skill_list,
        }, self.kt_trace_callback)
        
        mid = response["message_id"]
        self.times[mid] = datetime.now()


    def student_information(self):
        """
        Emulate a student requesting information about his student model.
        """
        if not self.current_student:
            return
        
        response = self.send('tutorgen.get_student', {
            'student_id': self.current_student,
        }, self.student_information_callback)
        
        mid = response["message_id"]
        self.times[mid] = datetime.now()

    def create_student_callback(self, response):
        """
        Callback for the create student event.
        """
        self.response_count+=1
        now = datetime.now()
        self.send_log_entry("RECV: add_student response recieved. " + str(response) + " " + str(now-self.times[response["message_id"]]) + " tutorgen.add_student" )

        self.students[response["student_id"]] = response["attributes"]
        self.current_student = response["student_id"]

    def add_problem_worked_callback(self, response):
        self.response_count +=1
        now = datetime.now()
        self.send_log_entry("RECV: add_problem_worked response recieved. " + str(response) + " " + str(now-self.times[response["message_id"]]) + " tutorgen.add_problem_worked")


    def kt_trace_callback(self, response):
        self.response_count +=1
        now = datetime.now()
        self.send_log_entry("RECV: kt_trace response recieved. " + str(response) + " " + str(now-self.times[response["message_id"]]) + " tutorgen.kt_batch_trace")

    def student_information_callback(self,response):
        self.response_count+=1
        now = datetime.now()
        self.send_log_entry("RECV: student_information response recieved. " + str(response) + " " + str(now-self.times[response["message_id"]]) + " tutorgen.get_student")

    def main_callback(self):
        if self.message_count < self.TOTAL_MESSAGES:
            action = random.choice(self.actions)
            action()
            self.message_count +=1
        
        if self.response_count < self.TOTAL_MESSAGES:
            return True
        else:
            return False

def worker():
    print("starting thread " + threading.currentThread().getName())
    #localhost
    entity_id = "ed188aa3-a673-4482-9475-aedd981ff360"
    app_secret = "e992a697f396a2fd99ef9910cb040fa9"
    url_root = "http://localhost:8000"
    
    #production (tres)
    #entity_id = "e7e43470-5031-496c-9972-cbb809455333"
    #app_secret = "1aadb263acec65c24b683976643516ce"
    #url_root = "http://www.hpit-project.org"
    
    #production (prod)
    #entity_id = "35f8fdda-7f4e-4b48-86ab-eda038186183"
    #app_secret = "d5f1723260ec88293f4fc79f0f7e4572"
    #url_root = "http://production.hpit-project.org"
    
    logging.basicConfig(
            filename="log/load_testing.log",
            level=logging.DEBUG,
            propagate=False,
            format='%(asctime)s %(levelname)s %(threadName)s :----: %(message)s', 
            datefmt='%m/%d/%Y %I:%M:%S %p')
    
    logger = logging.getLogger(__name__)
    
    logger.debug("start")
    
    t = LoadTestingTutor(entity_id, app_secret, logger)
    t.set_hpit_root_url(url_root)
    t.start()
    
    print("finishing thread " + threading.currentThread().getName())

if __name__ == "__main__":
    #threaded
    for xx in range(0,50):
        thread = threading.Thread(target=worker)
        thread.start()
    
    #non threaded
    #worker()
