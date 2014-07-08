import logging
import json
from json import JSONEncoder, JSONDecoder

from client import Tutor      

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
        self.send("hf_push_state",{"state":hint_factory_state_encoder.encode(hint_factory_state)},self.post_state_callback)
        
    def hint_exists(self,hint_factory_state):
        self.send("hf_hint_exists",{"state":hint_factory_state_encoder.encode(hint_factory_state)},self.hint_exists_callback)
        
    def get_hint(self,hint_factory_state):
        self.send("hf_get_hint",{"state":hint_factory_state_encoder.encode(hint_factory_state)},self.get_hint_callback)
        
    def init_problem(self,hint_factory_start_state, hint_factory_goal_state):
        self.send("hf_get_hint",{"start_state":hint_factory_start_state,"goal_problem":goal_problem_string},self.init_problem_callback)
        
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
    
    
class HintFactoryStateEncoder(JSONEncoder):
    def default(self,o):
        return {"steps": o.steps, "problem_state": o.problem_state}
        
class HintFactoryStateDecoder():
    def decode(self, json):
        state_object = JSONDecoder(object_hook = self.decode_hook).decode(json)
        return state_object
        
    def decode_hook(self,json):
        new_state  = HintFactoryState()
        try:
            new_state.steps = json["steps"]
            new_state.problem_state = json["problem_state"]
        except KeyError:
            print("The json object does not conform to expected HintFactoryState format")
            raise
            
        return new_state

class HintFactoryState(object):
    def __init__(self):
        self.steps = []
        self.problem_state = ""
    
    def __str__(self):
        return "HintFactoryState: " + str(self.steps) + " " + str(self.problem_state)

    def append_step(self,step):
        self.steps.append(step)
        
 
 
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
            "2x + 4 = 12" : HintFactoryTutor.GameState("2x + 4 = 12", [("Subtract 4","2x = 8"),("Subtract 12","2x + 4 - 12 = 0"),("Divide 2","(2x + 4) / 2 = 6")]),
            "2x = 8" : HintFactoryTutor.GameState("2x = 8",[("Add 4","2x + 4 = 12"),("Subtract 8","2x - 8 = 0"),("Divide 2","x = 4")]),
        }
        
        self.cur_state = self.game_states["2x + 4 = 12"]
        self.goal = "x = 4"
        
    def main_callback(self):

        print(str(self.cur_state))
        choice = input("Operation: (0 to quit, h for hint) ")
        
        if choice == "0":
            return False
        elif choice == "h":
            print ("Hint")
        else:
            self.cur_state = self.game_states[self.cur_state.possible_transitions[int(choice)-1][1]]
        
        print ("=======================================")
        
        if self.cur_state.problem == self.goal:
            print("You solved the problem!")
            return false
            
        
        return True
        
    
    
    
    
    
        
    
