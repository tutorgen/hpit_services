import json
from json import JSONEncoder, JSONDecoder

class HintFactoryState(object):
    def __init__(self,*args,**kwargs):
        self.steps = []
        self.problem_state = "" #the current state (look) of the problem
        self.last_problem_state = "" #the last state (look) of the problem
        self.problem = "" #the problem this state is for (start state of graph)
        
        self.fields = ["steps","problem_state","last_problem_state","problem"]
        
        for k,v in kwargs.items():
            setattr(self,k,v)

    def __str__(self):
        return "HintFactoryState: " + str(self.steps) + " " + str(self.problem_state)

    def __setitem__(self,key,value):
        if key in self.fields:
            setattr(self,key,value)
            
    def __getitem__(self,key):
        if key in self.fields:
            return getattr(self,key)
        else:
            raise KeyError
            
    def __delitem__(self,key):
        pass
    
    def __iter__(self):
        for x in self.fields:
            yield (x, getattr(self,x))

    def append_step(self,step,problem):
        self.steps.append(step)
        self.last_problem_state = self.problem_state
        self.problem_state = problem
        
    
        
        
if __name__ == "__main__":
    s = HintFactoryState()
    s.steps.append("step1")
    s.steps.append("step2")
    s.problem_state = "problem string"
    
    print(str(s))
