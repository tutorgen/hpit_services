import hashlib
from itertools import groupby
import sys

from hpitclient import Plugin
from utils.hint_factory_state import *

from py2neo import neo4j


class SimpleHintFactory(object):
    
    def __init__(self):
        self.db = neo4j.GraphDatabaseService()
        
        self.DISCOUNT_FACTOR = .5
        self.GOAL_REWARD = 100
        self.STD_REWARD = 0
       
    def push_node(self,problem_string,from_state_string,action_string,to_state_string):
        #problem used, from_string, action_string, to_string
        problem_node = self.db.get_indexed_node("problems_index","start_string",problem_string)
        
        if not problem_node:
            raise Exception("Problem node with start_string " + problem_string + " does not exist")
        
        from_state_hash = self.hash_string(from_state_string)
        action_hash = self.hash_string(action_string)
        to_state_hash = self.hash_string(to_state_string)
    
        return_node = None
        
        from_node = self.db.get_indexed_node("problems_index","start_string",from_state_string)
        if not from_node:
            from_node = self.db.get_indexed_node("problem_states_index","state_hash",from_state_hash)
            if not from_node:
                raise Exception("From node does not exist.")
        
        existing_node = self.db.get_indexed_node("problem_states_index","state_hash",to_state_hash)
        if not existing_node:
            #make a new state
            new_node, new_rel = self.db.create({"state_string":to_state_string,"state_hash":to_state_hash,"bellman_value":0,"store_count":1,"discount_factor":self.DISCOUNT_FACTOR},(from_node,"action",0))
            new_node.add_labels("ProblemState")
            problem_states_index = self.db.get_or_create_index(neo4j.Node,"problem_states_index")
            problem_states_index.add("state_hash",to_state_hash,new_node)
            
            new_rel["action_string"] = action_string
            new_rel["action_hash"] = action_hash
            new_rel["probability"] = 0.0
            
            self.update_action_probabilities(new_rel)
            return_node = new_node
        else:
            #connect old state to new state
            existing_node["store_count"] +=1
            try:
                edge = next(from_node.match_outgoing("action",existing_node)) #if there are no edges, will raise exception.
                self.update_action_probabilities(edge)
            except StopIteration:
                new_rel, = self.db.create((from_node,"action",existing_node))
                new_rel["action_string"] = action_string
                new_rel["action_hash"] = action_hash
                new_rel["probability"] = 0.0
                self.update_action_probabilities(new_rel)
            
            return_node = existing_node
        
        self.bellman_update(problem_node["start_string"],problem_node["goal_string"])
        return return_node
    
    def hash_string(self, string):
        #hashing used for problem states and action strings
        return hashlib.sha256(bytes(string.encode('utf-8'))).hexdigest()
    
    def update_action_probabilities(self,relationship):
        #take a relationship, get parent, and update probabilities based on neighbors store_count
        parent_node = relationship.start_node
        edges = parent_node.match_outgoing("action")
        total_count = 0
        for edge in edges:
            total_count += edge.end_node["store_count"]
        if total_count<1:
            total_count= 1
        edges = parent_node.match_outgoing("action")
        for edge in edges:
            edge["probability"] = edge.end_node["store_count"] / total_count
                 
    def _do_bellman(self,node,goal_hash):
        #do a bellman update on the graph stemming from problem node
        if node["state_hash"] == goal_hash:
            node["bellman_value"] = self.GOAL_REWARD
        else:
            child_edges = node.match_outgoing("action")

            action_values = [0]
            for edge in child_edges:
                #bellman_sum = sum([e.probability * self.discount_factor * self._do_bellman(e.inV(), goal_hash) for e in edges])
                bellman_sum = edge["probability"] * node["discount_factor"] * self._do_bellman(edge.end_node,goal_hash)
                action_values.append(self.STD_REWARD + bellman_sum)
            node["bellman_value"] = max(action_values)
        
        return node["bellman_value"]
    
    def bellman_update(self,start_string,goal_string):
        problem_node = self.create_or_get_problem_node(start_string,goal_string)
        goal_hash = self.hash_string(goal_string)
        self._do_bellman(problem_node,goal_hash)
    
    def create_or_get_problem_node(self, start_string, goal_string):
        #create a new problem node in the graph, or, if exists, return problem node 

        problem_node = self.db.get_indexed_node("problems_index","start_string",start_string)
        if problem_node:
            return problem_node
        else:
            problem_node, = self.db.create({"start_string":start_string,"goal_string":goal_string,"discount_factor":self.DISCOUNT_FACTOR})
            problem_node.add_labels("Problem")
            problem_index = self.db.get_or_create_index(neo4j.Node,"problems_index")
            problem_index.add("start_string",start_string,problem_node)
            return problem_node
            
    def hint_exists(self,problem_string,state_string):
        state_hash = self.hash_string(state_string)
        node = self.db.get_indexed_node("problems_index","start_string",state_string)
        if not node:
            node = self.db.get_indexed_node("problem_states_index","state_hash",state_hash)
            if not node:
                raise Exception("Hint exist failed; state does not exist")

        child_edges = node.match_outgoing("action")
        try:
            edge = next(child_edges) #if there are no edges, will raise exception.
            return True
        except StopIteration:
            return False
                
    def get_hint(self,problem_string,state_string):
        state_hash = self.hash_string(state_string)
        if not self.hint_exists(problem_string,state_string):
            return None
        else:
            node = self.db.get_indexed_node("problems_index","start_string",state_string)
            if not node:
                node = self.db.get_indexed_node("problem_states_index","state_hash",state_hash)
                if not node:
                    raise Exception("Get hint failed; state does not exist")
            
            child_edges = node.match_outgoing("action")
            max_reward = 0
            count = 0
            hint = ""
            for edge in child_edges:
                if edge.end_node["bellman_value"] > max_reward:
                    max_reward = edge.end_node["bellman_value"]
                    hint = edge["action_string"]
                count +=1
                
            if count <=0:
                return None
            else:
                return hint


class HintFactoryPlugin(Plugin):
    def __init__(self, entity_id, api_key, logger, args = None):
        super().__init__(entity_id, api_key)
        self.logger = logger
        self.hf = SimpleHintFactory()

    def post_connect(self):
        super().post_connect()

        self.subscribe(
             hf_init_problem=self.init_problem_callback, 
             hf_push_state=self.push_state_callback,
             hf_hint_exists=self.hint_exists_callback,
             hf_get_hint=self.get_hint_callback)

    def init_problem_callback(self, message):
        self.logger.debug("INIT PROBLEM")
        self.logger.debug(message)
        
        if self.hf.create_or_get_problem_node(message["start_state"],message["goal_problem"]):
            self.send_response(message["message_id"],{"status":"OK"})
        else:
            self.send_response(message["message_id"],{"status":"NOT_OK"})
        
    def push_state_callback(self, message):
        self.logger.debug("PUSH PROBLEM STATE")
        self.logger.debug(message)
            
        incoming_state = HintFactoryStateDecoder().decode(message["state"])
        self.hf.push_node(incoming_state.problem,incoming_state.last_problem_state,incoming_state.steps[-1],incoming_state.problem_state)
        self.send_response(message["message_id"],{"status":"OK"})

    def hint_exists_callback(self, message):
        self.logger.debug("HINT EXISTS")
        self.logger.debug(message)
        
        incoming_state = HintFactoryStateDecoder().decode(message["state"])
        if self.hf.hint_exists(incoming_state.problem,incoming_state.problem_state):
            self.send_response(message["message_id"],{"status":"OK","exists":"YES"})
        else:
            self.send_response(message["message_id"],{"status":"OK","exists":"NO"})
        
    def get_hint_callback(self, message):
        self.logger.debug("GET HINT")
        self.logger.debug(message)

        incoming_state = HintFactoryStateDecoder().decode(message["state"])
        hint = self.hf.get_hint(incoming_state.problem,incoming_state.problem_state)
        sys.stdout.flush()
        if hint:
            self.send_response(message["message_id"],{"status":"OK","exists":"YES","hint_text":hint})
        else:
            self.send_response(message["message_id"],{"status":"OK","exists":"NO"})
           

if __name__ == '__main__':
    hf = SimpleHintFactory()
    hf.db.clear()
    hf.create_or_get_problem_node("2 + 4 = 6", "1 = 1")
    hf.push_node("2 + 4 = 6","2 + 4 = 6", "Simplify", "6 = 6")
    hf.push_node("2 + 4 = 6","6 = 6", "Subtract", "1 = 1")
    hf.push_node("2 + 4 = 6","2 + 4 = 6", "Skip", "1 = 1")
    print (hf.hint_exists("2 + 4 = 6","1 = 1"))
    print (hf.hint_exists("2 + 4 = 6","6 = 6"))
    print (hf.get_hint("2 + 4 = 6","1 = 1"))
    print (hf.get_hint("2 + 4 = 6","6 = 6"))
    print("done")

