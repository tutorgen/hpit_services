import hashlib
from collections import deque
from itertools import groupby
import sys

from hpitclient import Plugin
from utils.hint_factory_state import *

from py2neo import neo4j

class StateDoesNotExistException(Exception):
    """
    Raised when a state cannot be found.
    """
    
class HintDoesNotExistException(Exception):
    """
    Raised when a state does not have any edges to analyze
    """
    

class SimpleHintFactory(object):
    
    def __init__(self):
        self.db = neo4j.GraphDatabaseService()
        
        self.DISCOUNT_FACTOR = .5
        self.GOAL_REWARD = 100
        self.STD_REWARD = 0
        self.LOOP_PENALTY = -10
       
    def push_node(self,problem_string,from_state_string,action_string,to_state_string):
        #problem used, from_string, action_string, to_string
        problem_node = self.db.get_indexed_node("problems_index","start_string",problem_string)
        
        if not problem_node:
            raise StateDoesNotExistException("Problem with string " + str(problem_string) + " does not exist.")
        
        from_state_hash = self.hash_string(from_state_string)
        action_hash = self.hash_string(action_string)
        to_state_hash = self.hash_string(to_state_string)
    
        return_node = None
        
        from_node = self.db.get_indexed_node("problems_index","start_string",from_state_string)
        if not from_node:
            from_node = self.db.get_indexed_node("problem_states_index","state_hash",from_state_hash)
            if not from_node:
                raise StateDoesNotExistException("Cannot find 'from_state' with string " + str(from_state_string) + ".")
        
        existing_node = self.db.get_indexed_node("problem_states_index","state_hash",to_state_hash)
        if not existing_node:
            existing_node = self.db.get_indexed_node("problems_index","start_string",to_state_string)
            
        if not existing_node:
            #make a new state
            new_node, new_rel = self.db.create({"state_string":to_state_string,"state_hash":to_state_hash,"bellman_value":0,"discount_factor":self.DISCOUNT_FACTOR},(from_node,"action",0))
            new_node.add_labels("ProblemState")
            problem_states_index = self.db.get_or_create_index(neo4j.Node,"problem_states_index")
            problem_states_index.add("state_hash",to_state_hash,new_node)
            
            new_rel["action_string"] = action_string
            new_rel["action_hash"] = action_hash
            new_rel["probability"] = 0.0
            new_rel["taken_count"] = 1
            
            self.update_action_probabilities(new_rel)
            return_node = new_node
        else:
            #connect old state to new state
            try:
                edge = next(from_node.match_outgoing("action",existing_node)) #if there are no edges, will raise exception.
                edge["taken_count"]+=1
                self.update_action_probabilities(edge)
            except StopIteration:
                new_rel, = self.db.create((from_node,"action",existing_node))
                new_rel["action_string"] = action_string
                new_rel["action_hash"] = action_hash
                new_rel["probability"] = 0.0
                new_rel["taken_count"] = 1
                self.update_action_probabilities(new_rel)
            
            return_node = existing_node
        
        self.bellman_update(problem_node["start_string"],problem_node["goal_string"])
        return return_node
    
    def hash_string(self, string):
        #hashing used for problem states and action strings
        return hashlib.sha256(bytes(str(string).encode('utf-8'))).hexdigest()
    
    def update_action_probabilities(self,relationship):
        #take a relationship, get parent, and update probabilities based on neighbors store_count
        parent_node = relationship.start_node
        edges = parent_node.match_outgoing("action")
        total_count = 0
        for edge in edges:
            total_count += edge["taken_count"]
        if total_count<1:
            total_count= 1
        edges = parent_node.match_outgoing("action")
        for edge in edges:
            edge["probability"] = edge["taken_count"] / total_count
                 
    def _trim_nodes(self, cur_node, end_nodes):
        """
        Checks if this node has any children that loops back to this node.
        """
        bad_nodes = set()
        for node in end_nodes:
            end_edges = node.match_outgoing("action")
            for end in end_edges:
                if end.end_node == cur_node:
                    bad_nodes.add(node)

        return end_nodes - bad_nodes
    
    def bellman_update(self,start_string,goal_string):
        problem_node = self.create_or_get_problem_node(start_string,goal_string)
        goal_hash = self.hash_string(goal_string)
        goal_node = self.db.get_indexed_node("problem_states_index","state_hash",goal_hash)

        node_queue = deque([problem_node])
        node_dict = {
            problem_node._id: (False, 0),
            goal_node._id: (True, 100)
        }

        while node_queue:
            cur_node = node_queue.popleft()

            child_edges = list(cur_node.match_outgoing("action")) #match_outgoing is a generator (we need this twice)
            end_nodes = {edge.end_node for edge in child_edges}

            #Have these entered the node dictionary?
            for node in end_nodes:
                if node._id not in node_dict.keys():
                    node_dict[node._id] = (False, 0)

            #Check these end nodes to see if they loop back to me
            end_nodes = self._trim_nodes(cur_node, end_nodes)

            #Have all my children been calculated
            if not all([node_dict[node._id][0] for node in end_nodes]): #No they haven't. Add them to the queue.
                for node in end_nodes:
                    if not node_dict[node._id][0]:
                        if node not in node_queue:
                            node_queue.append(node)
                if cur_node not in node_queue:
                    node_queue.append(cur_node)
            else: #Yes they have. Then calclulate my value.
                action_values = [0]
                for edge in child_edges:
                    if edge.end_node._id == cur_node._id:
                        action_values.append(self.LOOP_PENALTY)
                    else:
                        end_node_bellman_value = node_dict[edge.end_node._id][1]
                        action_values.append(self.STD_REWARD + (edge["probability"] * self.DISCOUNT_FACTOR * end_node_bellman_value))
                node_dict[cur_node._id] = (True, max(action_values))

        for node_id, v in node_dict.items():
            self.db.node(node_id)['bellman_value'] = v[1]

    
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
                raise StateDoesNotExistException("Problem with string " + str(problem_string) + " or state with string " + str(state_string) + " does not exist.")

        child_edges = node.match_outgoing("action")
        try:
            edge = next(child_edges) #if there are no edges, will raise exception.
            return True
        except StopIteration:
            return False
                
    def get_hint(self,problem_string,state_string):
        state_hash = self.hash_string(state_string)
        if not self.hint_exists(problem_string,state_string):
            raise HintDoesNotExistException("Hint does not exist for state " + str(state_string))
        else:
            node = self.db.get_indexed_node("problems_index","start_string",state_string)
            if not node:
                node = self.db.get_indexed_node("problem_states_index","state_hash",state_hash)
            
            child_edges = node.match_outgoing("action")
            max_reward = -999999
            hint = ""
            count = 0
            for edge in child_edges:
                if edge.end_node["bellman_value"] > max_reward:
                    max_reward = edge.end_node["bellman_value"]
                    hint = edge["action_string"]
                count +=1
            
            if count == 0:
                raise HintDoesNotExistException("Hint does not exist for state " + str(state_string))
                
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
        if self.logger:
            self.logger.debug("INIT PROBLEM")
            self.logger.debug(message)
            
        try:
            start_state = message["start_state"]
            goal_problem = message["goal_problem"]
        except KeyError:
            self.send_response(message["message_id"], {
                "error": "hf_init_problem requires a 'start_state' and 'goal_problem'",
                "status":"NOT_OK"
            })
            return
        
        if self.hf.create_or_get_problem_node(message["start_state"],message["goal_problem"]):
            self.send_response(message["message_id"],{"status":"OK"})
        else:
            self.send_response(message["message_id"],{
            "status":"NOT_OK",
            "error":"Unknown error when attempting to create or get problem state",
            })
            
    
        
    def push_state_callback(self, message):
        if self.logger:
            self.logger.debug("PUSH PROBLEM STATE")
            self.logger.debug(message)
            
        try:
            state=  message["state"]
        except KeyError:
            self.send_response(message["message_id"], {
                "error": "hf_push_state requires a 'state'",
                "status":"NOT_OK"
            })
            return

        incoming_state = self.get_incoming_state(message["state"])
        if not incoming_state:
            self.send_response(message["message_id"],{
            "status":"NOT_OK",
            "error":"message's 'state' parameter should be a dict",
            })
            return
            
        try:
            success = self.hf.push_node(incoming_state.problem,incoming_state.last_problem_state,incoming_state.steps[-1],incoming_state.problem_state)
            if success:
                self.send_response(message["message_id"],{"status":"OK"})
            else:
                self.send_response(message["message_id"],{
                "status":"NOT_OK",
                "error":"Unknown error when pushing state"
                })
        except IndexError:
            self.send_response(message["message_id"],{
            "status":"NOT_OK",
            "error":"State must have at least one step"
            })
        except StateDoesNotExistException as e:
            self.send_response(message["message_id"],{
            "status":"NOT_OK",
            "error": str(e)
            })

    def hint_exists_callback(self, message):
        if self.logger:
            self.logger.debug("HINT EXISTS")
            self.logger.debug(message)
            
        try:
            state=  message["state"]
        except KeyError:
            self.send_response(message["message_id"], {
                "error": "hf_push_state requires a 'state'",
                "status":"NOT_OK"
            })
            return
        
        incoming_state = self.get_incoming_state(message["state"])
        if not incoming_state:
            self.send_response(message["message_id"],{
            "status":"NOT_OK",
            "error":"message's 'state' parameter should be a dict",
            })
            return
        try:
            if self.hf.hint_exists(incoming_state.problem,incoming_state.problem_state):
                self.send_response(message["message_id"],{"status":"OK","exists":"YES"})
            else:
                self.send_response(message["message_id"],{"status":"OK","exists":"NO"})
        except StateDoesNotExistException as e:
            self.send_response(message["message_id"],{
            "status":"NOT_OK",
            "error": str(e)
            })
        
    def get_hint_callback(self, message):
        if self.logger:
            self.logger.debug("GET HINT")
            self.logger.debug(message)
        
        try:
            state=  message["state"]
        except KeyError:
            self.send_response(message["message_id"], {
                "error": "hf_push_state requires a 'state'",
                "status":"NOT_OK"
            })
            return
        
        incoming_state = self.get_incoming_state(message["state"])
        if not incoming_state:
            self.send_response(message["message_id"],{
            "status":"NOT_OK",
            "error":"message's 'state' parameter should be a dict",
            })
            return
            
        try:
            hint = self.hf.get_hint(incoming_state.problem,incoming_state.problem_state)
            if hint:
                self.send_response(message["message_id"],{"status":"OK","exists":"YES","hint_text":hint})
            else:
                self.send_response(message["message_id"],{"status":"OK","exists":"NO"})
        except HintDoesNotExistException as e:
            self.send_response(message["message_id"],{
            "status":"NOT_OK",
            "error": str(e)
            })
           
    def get_incoming_state(self, state):
        if isinstance(state,dict):
            return HintFactoryState(**state)
        else:
            return False
            
            
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

