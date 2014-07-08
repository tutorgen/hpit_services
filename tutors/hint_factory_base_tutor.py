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
        self.send("hf_get_hint",{"start_state":hint_factory_start_state,"goal_state":hint_factory_goal_state},self.init_problem_callback)
        
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
        
    
    
if __name__== "__main__":
    s = HintFactoryState()
    print(json.dumps(s))
    
    
    
    
    
        
    
