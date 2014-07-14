import json
from json import JSONEncoder, JSONDecoder

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

    def append_step(self,step,problem):
        self.steps.append(step)
        self.problem_state = problem
        
        
if __name__ == "__main__":
    s = HintFactoryState()
    s.steps.append("step1")
    s.steps.append("step2")
    s.problem_state = "problem string"
    
    j = HintFactoryStateEncoder().encode(s)
    print(str(j))
    
    s = HintFactoryStateDecoder().decode(j)
    
    print(str(s))
