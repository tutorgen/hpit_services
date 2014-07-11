#from client import Plugin
import hashlib
from itertools import groupby

from bulbs.model import Node, Relationship
from bulbs.neo4jserver import Graph
from bulbs import property as prop
from bulbs.utils import current_datetime

#from client.hint_factory_state import *

class StateFinderMixin:

    def hash_string(self, string):
        return hashlib.sha256(bytes(string.encode('utf-8'))).hexdigest()


    def push_state(self, graph, action_string, problem_string):
        """
            graph - the graph that this node is part of
            action_string - a string representation of the action taken
            problem_string - a string representation of the problem at it's current state
        """
        #Check if this state exists directly off this node
        problem_hash = self.hash_string(problem_string)
        action_hash = self.hash_string(action_string)

        #Does a direct decendent match the state and action?
        state, action = self.direct_decendent_matches_state_action(problem_hash, action_hash)

        if state:
            state.store_count = state.store_count + 1
            state.save()
            self.update_action_probabilites(action)
            return state

        #Does a direct decendent match the state but not the action?
        state = self.direct_decendent_matches_state(problem_hash)

        if state:
            new_action = graph.actions.create(self, state)
            new_action.action_string = action_string
            new_action.action_hash = action_hash
            new_action.save()
            self.update_action_probabilites(new_action)
            return state

        #No decendent state - Add new state and action to connect it.
        new_state = graph.states.create(state_string=problem_string, state_hash=problem_hash)

        new_action = graph.actions.create(self, new_state)
        new_action.action_string = action_string
        new_action.action_hash = action_hash
        new_action.save()

        self.update_action_probabilites(new_action)

        return new_state


    def direct_decendent_matches_state_action(self, state_hash, action_hash):
        edges = self.outE()
        
        for e in edges:
            if e.action_hash == action_hash:
                node = e.outV()
                if node.state_hash == state_hash:
                    return (node, e)

        return None


    def direct_decendent_matches_state(self, state_hash):
        nodes = self.outV()

        for node in nodes:
            if node.state_hash == state_hash:
                return node

        return None

        
    def update_action_probabilites(self, action):
        siblings = [(s.outV().store_count, s) for s in action.inV().outE() if s.action_hash == action.action_hash]
        total_store_count = sum(map(lambda s: s[0], siblings))

        if total_store_count <= 0:
            total_store_count = 1

        for store_count, s in siblings:
            s.probability = store_count / total_store_count
            s.save()


    #We could speed this up by doing a probabilistic search.
    #For now it is a naive bredth first search. - Ray
    def find_state_by_hash(self, state_hash, visited=None):
        search_states = set(self.outV())

        if not visited:
            visited = set()

        search_states = search_states - visited

        #Breadth first
        for s in search_states:
            if s.state_hash == state_hash:
                return s

        #Don't search me again
        visited = search_states + visited

        for s in search_states:
            found = s.find_state_by_hash(state_hash, visited)

            if found:
                return found

        return None


    def find_state_by_string(self, state_string):
        return self.find_state_by_hash(self.hash_string(state_string))


class MDPProblemNode(Node, StateFinderMixin):
    element_type = "mdp_problem"

    created = prop.DateTime(default=current_datetime, nullable=False)
    start_text = prop.String()
    goal_text = prop.String()
    discount_factor = prop.Float(default=0.5)

    def find_goal_state(self):
        self.find_state_by_string(self.goal_text)


    def _do_bellman(self, state, goal_hash):
        GOAL_REWARD = 100
        STD_REWARD = 10

        if state.state_hash == goal_hash:
            state.bellman_value = GOAL_REWARD
        else:
            child_edges = state.outE()

            action_values = []
            for action, edges in groupby(child_edges, lambda x: x.action_hash):
                bellman_sum = sum([e.probability * self.discount_factor * self._do_bellman(e.outV(), goal_hash) for e in edges])
                action_values.append(STD_REWARD + bellman_sum)

            state.bellman_value = max(action_values)

        state.save()
        return state.bellman_value


    def do_bellman_update(self):
        """
        Perform Bellman value iteration upon the whole graph to assign
        reward values.
        """

        self._do_bellman(self, self.hash_string(self.goal_text))


class MDPStateNode(Node, StateFinderMixin):
    element_type = "mdp_state"

    created = prop.DateTime(default=current_datetime, nullable=False)
    state_hash = prop.String()
    state_string = prop.String()
    store_count = prop.Integer(default=1)
    bellman_value = prop.Float(default=0.0)


class MDPAction(Relationship):
    label = "action"

    created = prop.DateTime(default=current_datetime, nullable=False)
    action_hash = prop.String()
    action_string = prop.String()
    probability = prop.Float(default=0.0)


class MasterGraph(Graph):

    def __init__(self):
        super().__init__()
        self.add_proxy("problems", MDPProblemNode)
        self.add_proxy("states", MDPStateNode)
        self.add_proxy("actions", MDPAction)


    def create_problem(self, start_text, goal_text):

        exists = self.find_problem(start_text, goal_text)
        if exists:
            return exists
        
        print("here")
        #Create the problem
        new_problem = self.problems.create(start_text=start_text, goal_text=goal_text)

        return new_problem


    def find_problem(self, start_text, goal_text):
        nodes = self.problems.index.lookup(start_text=start_text, goal_text=goal_text)
        #Only one should exists
        return next(nodes) if nodes else None


"""
class HintFactoryPlugin(Plugin):

    def __init__(self, entity_id, api_key, logger, args = None):
        super().__init__(entity_id, api_key)
        self.logger = logger
        self.db = MasterGraph()
        self.state = None


    def post_connect(self):
        super().post_connect()

        self.subscribe(
             hf_init_problem=self.init_problem_callback, 
             hf_push_state=self.push_state_callback,
             hf_hint_exists=self.hint_exists_callback,
             hf_get_hint=self.get_hint_callback)

    #Hint Factory Plugin
    def init_problem_callback(self, message):
        #""
        #    problem_text - The text of the problem
        #    problem_goal_text - The goal of the problem
        #""
        self.db.create_problem(message["start_state"],message["goal_problem"])
        self.send_response(message["message_id"],{"status":"OK"})
        
        self.logger.debug("INIT PROBLEM")
        self.logger.debug(message)

    def push_state_callback(self, message):
         
        #incoming_state = message["state"]
         
        self.logger.debug("PUSH PROBLEM STATE")
        self.logger.debug(message)

    def hint_exists_callback(self, message):
        self.logger.debug("HINT EXISTS")
        self.logger.debug(message)

    def get_hint_callback(self, message):
        self.logger.debug("GET HINT")
        self.logger.debug(message)
"""

if __name__ == '__main__':
    db = MasterGraph()
    #import pdb; pdb.set_trace()
    problem = db.create_problem('4x-6=10', 'x=4')
    print(str(problem))
    state = problem.push_state(db, 'addition', '4x-6+6=10+6')
    state = state.push_state(db, 'simplification', '4x=16')
    state = state.push_state(db, 'division', '4x/4=16/4')
    state = state.push_state(db, 'simplification', 'x=4')
    x = 5
    print("done")
    

