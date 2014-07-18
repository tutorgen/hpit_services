import logging
import json
from json import JSONEncoder, JSONDecoder
import time

from client import Tutor
from client.exceptions import ConnectionError
from client.hint_factory_state import *

class HintFactoryBaseTutor(Tutor):
    
    def __init__(self, entity_id, api_key, logger, run_once=None, args = None):
        super().__init__(entity_id, api_key, self.main_callback, run_once=run_once)
        self.run_once = run_once
        self.logger = logger
        
        if args: 
            self.args = json.loads(args[1:-1])
        else:
            self.args = None
            
        self.hint_factory_state_encoder = HintFactoryStateEncoder()
            
    def post_state(self,hint_factory_state):
        self.send("hf_push_state",{"state":self.hint_factory_state_encoder.encode(hint_factory_state)},self.post_state_callback)
        #self.post_state_callback({"status":"OK"})
        
    def hint_exists(self,hint_factory_state):
        self.send("hf_hint_exists",{"state":self.hint_factory_state_encoder.encode(hint_factory_state)},self.hint_exists_callback)
        #self.hint_exists_callback({"status":"OK","exists":"YES"})
    
    def get_hint(self,hint_factory_state):
        self.send("hf_get_hint",{"state":self.hint_factory_state_encoder.encode(hint_factory_state)},self.get_hint_callback)
        #time.sleep(3)
        #self.get_hint_callback({"status":"OK","exists":"YES","hint_text":"This is a hint."})
    
    def init_problem(self,start_problem_string, goal_problem_string):
        self.send("hf_init_problem",{"start_state":start_problem_string,"goal_problem":goal_problem_string},self.init_problem_callback)
        #self.init_problem_callback({"status":"OK"})
    
    def main_callback(self):
        raise NotImplementedError("Please implement a main_callback for your tutor.")
        
    def post_state_callback(self,response):
        pass
    
    def hint_exists_callback(self,response):
        pass
    
    def get_hint_callback(self,response):
        pass
    
    def init_problem_callback(self,response):
        pass    
        
class BadHintFactoryResponseError(Exception):
    """
    Raised when a response is invalid or bad.
    """
 
 
#------------------------------------------------------------------------------
#  HINT FACTORY TUTOR
#------------------------------------------------------------------------------

class HintFactoryTutor(HintFactoryBaseTutor):
        
    class GameState(object):
        def __init__(self,problem_text,transition_list):
            self.possible_transitions = transition_list
            self.problem = problem_text
           
        def __str__(self):
            output = "\n\n"+self.problem + "\n----------------------\n"
            count = 1
            for transition in self.possible_transitions:
                output += str(count) + ". " + transition[0] + "\n\n"
                count+=1
            return output
            
            

    def __init__(self, entity_id, api_key, logger, run_once = None, args = None):
        super().__init__(entity_id,api_key,logger,run_once,args)
        
        self.game_states = {
            "2x + 4 = 12" : HintFactoryTutor.GameState("2x + 4 = 12", [("Subtract 4","2x = 8"),("Subtract 12","2x - 8 = 0"),("Divide 2","(2x + 4) / 2 = 6")]),
            "2x = 8" : HintFactoryTutor.GameState("2x = 8",[("Add 4","2x + 4 = 12"),("Subtract 8","2x - 8 = 0"),("Divide 2","x = 4")]),
            "2x - 8 = 0" : HintFactoryTutor.GameState("2x - 8 = 0",[("Divide 2","(2x + 8) / 2 = 0"),("Add 8","2x = 8")]),
            "(2x + 8) / 2 = 0" : HintFactoryTutor.GameState("(2x + 8) / 2 = 0",[("Multiply 2","2x - 8 = 0")]),   #-8 error
            "x = 4" : HintFactoryTutor.GameState("x = 4",[]),
            "(2x + 4) / 2 = 6" : HintFactoryTutor.GameState("(2x + 4) / 2 = 6",[("Multiply 2","2x + 4 = 12"),("Subtract 6","(2x + 4) / 2 - 6 = 0")]),   #-4 error
            "(2x + 4) / 2 - 6 = 0" : HintFactoryTutor.GameState("(2x + 4) / 2 - 6 = 0",[("Multiply 2","2x - 8 = 0"),("Add 6","(2x + 4) / 2 = 6")]),
        }
        
        self.cur_state = self.game_states["2x + 4 = 12"]
        
        self.hf_state = HintFactoryState("2x + 4 = 12")
        
        self.goal = "x = 4"
        self.hint = None
        self.waiting_for_hint = False
        self.exists = False
        
    def post_connect(self):
        self.init_problem("2x + 4 = 12","x = 4")
        
    def init_problem_callback(self,response):
        try:
            if response['status'] != "OK":
                raise ConnectionError("Failure to post state to HPIT server.")
        except KeyError as e:
            print("The response does not contain a status code. "+ str(type(e))+str(e.args))
        
    def post_state_callback(self,response):
        try:
            if response['status'] != "OK":
                raise ConnectionError("Failure to post state to HPIT server.")
        except KeyError as e:
            print("The response does not contain a status code. "+ str(type(e))+str(e.args))
            
    def hint_exists_callback(self,response):
        try:
            if response['status'] != "OK":
                raise ConnectionError("Failure to post state to HPIT server.")
        except KeyError as e:
            print("The response does not contain a status code. "+ str(type(e))+str(e.args))
            
        if response['exists'] == "YES":
            self.exists = True
        elif response['exists'] == "NO":
            self.exists = False
            
    def get_hint_callback(self,response):
        try:
            if response['status'] != "OK":
                raise ConnectionError("Failure to post state to HPIT server.")

            if response['exists'] == "YES":
                self.hint = response["hint_text"]
            elif response['exists'] == "NO":
                self.hint = "No hint available."
                
        except KeyError as e:
            print("The response does not contain the proper fields. "+ str(type(e))+str(e.args))
    
    def main_callback(self):
        
        if self.cur_state.problem == self.goal:
            print(self.goal)
            print("You solved the problem!")
            return False
        
        if self.waiting_for_hint == True:
            if self.hint!=None:
                print(self.hint)
                self.hint = None
                self.waiting_for_hint = False
            else:
                return True
        
        else:
            print(str(self.cur_state))
            choice = input("Operation: (0 to quit, h for hint) ")
            
            if choice == "0":
                return False
            elif choice == "h":
                self.waiting_for_hint = True
                print("Waiting for hint...")
                self.get_hint(self.hf_state)
                return True
            else:
                step = self.cur_state.possible_transitions[int(choice)-1][0]
                self.cur_state = self.game_states[self.cur_state.possible_transitions[int(choice)-1][1]]
                self.hf_state.append_step(step,self.cur_state.problem)
                self.post_state(self.hf_state)
                self.exists = False
                
            print ("=======================================")
        
        return True
        
    
    
    
    
    
        
    
