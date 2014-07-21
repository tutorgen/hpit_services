import json
from json import JSONEncoder, JSONDecoder

class HintFactoryStateEncoder(JSONEncoder):
    def default(self,o):
        return {"steps": o.steps, "problem_state": o.problem_state, "last_problem_state": o.last_problem_state,"problem":o.problem}
        
class HintFactoryStateDecoder():
    def decode(self, json):
        state_object = JSONDecoder(object_hook = self.decode_hook).decode(json)
        return state_object
        
    def decode_hook(self,json):
        new_state  = HintFactoryState()
        try:
            new_state.steps = json["steps"]
            new_state.problem_state = json["problem_state"]
            new_state.last_problem_state = json["last_problem_state"]
            new_state.problem = json["problem"]
        except KeyError:
            print("The json object does not conform to expected HintFactoryState format")
            raise
            
        return new_state

class HintFactoryState(object):
    def __init__(self,problem = ""):
        self.steps = []
        self.problem_state = problem #the current state (look) of the problem
        self.last_problem_state = "" #the last state (look) of the problem
        self.problem = problem #the problem this state is for (start state of graph)
    
    def __str__(self):
        return "HintFactoryState: " + str(self.steps) + " " + str(self.problem_state)

    def append_step(self,step,problem):
        self.steps.append(step)
        self.last_problem_state = self.problem_state
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
