import hashlib
from collections import deque
from itertools import groupby
from functools import reduce
import sys

from hpitclient import Plugin
from hpit.utils.hint_factory_state import *

from pymongo import MongoClient
from bson.objectid import ObjectId
import bson

from hpit.management.settings_manager import SettingsManager
settings = SettingsManager.get_plugin_settings()

from py2neo import neo4j

class StateDoesNotExistException(Exception):
    """
    Raised when a state cannot be found.
    """
    
class HintDoesNotExistException(Exception):
    """
    Raised when a state does not have any edges to analyze
    """

class GoalDoesNotExistException(Exception):
    """
    Raised when a problem does not have a goal set correctly
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
        
        action_hash = self.hash_string(action_string)
        from_state_hash = self.hash_string('-'.join([problem_string, from_state_string]))
        to_state_hash = self.hash_string('-'.join([problem_string, to_state_string]))
    
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
    
    def delete_node(self,problem_string,state_string):
        state_hash = self.hash_string('-'.join([problem_string, state_string]))
        node = self.db.get_indexed_node("problems_index","start_string",state_string)
        if not node:
            node = self.db.get_indexed_node("problem_states_index","state_hash",state_hash)
            if not node:
                raise StateDoesNotExistException("Problem with string " + str(problem_string) + " or state with string " + str(state_string) + " does not exist.")

        in_edges = node.match_incoming()
        for e in in_edges:
            e.delete()
        out_edges = node.match_outgoing()
        for e in out_edges:
            e.delete()
                
        node.delete()
        return True
        
    def delete_problem(self,problem_string,state_string):
        node = self.db.get_indexed_node("problems_index","start_string",state_string)
        if not node:
            return False
        
        node.delete_related()
        return True
        
    
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

        goal_hash = self.hash_string('-'.join([start_string, goal_string]))
        goal_node = self.db.get_indexed_node("problem_states_index","state_hash",goal_hash)

        if not goal_node:
            return

        node_queue = deque([problem_node])
        node_dict = {goal_node._id: 100}

        #Run with partial information
        while node_queue:
            cur_node = node_queue.popleft()

            child_edges = list(cur_node.match_outgoing("action"))

            if not child_edges:
                node_dict[cur_node._id] = self.LOOP_PENALTY
                continue;

            #Which of my children have not been calculated?
            calculated_children = []
            for edge in child_edges:
                if edge.end_node._id in node_dict:
                    calculated_children.append((edge['probability'], node_dict[edge.end_node._id]))
                else:
                    if edge.end_node not in node_queue:
                        node_queue.append(edge.end_node)

            #Of my calculated children, which one has the max
            if calculated_children:
                best_val = reduce(lambda x, y: x if x[1] > y[1] else y, calculated_children)
                node_dict[cur_node._id] = round(self.STD_REWARD + (best_val[0] * best_val[1] * self.DISCOUNT_FACTOR), 6)
            else:
                if cur_node not in node_queue:
                    node_queue.append(cur_node)

        #Run with full but possibly incorrect information until the values in the calculations converge
        run_convergence = True
        while run_convergence:
            run_convergence = False

            node_queue = deque([problem_node])
            convergence_dict = {goal_node._id: 100}

            while node_queue:
                cur_node = node_queue.popleft()

                child_edges = cur_node.match_outgoing("action")

                calculated_children = []
                for edge in child_edges:
                    if edge.end_node._id not in convergence_dict:
                        if edge.end_node not in node_queue:
                            node_queue.append(edge.end_node)

                    calculated_children.append((edge['probability'], node_dict[edge.end_node._id]))

                if calculated_children:
                    best_val = reduce(lambda x, y: x if x[1] > y[1] else y, calculated_children)
                    convergence_dict[cur_node._id] = round(self.STD_REWARD + (best_val[0] * best_val[1] * self.DISCOUNT_FACTOR), 6)
                else:
                    convergence_dict[cur_node._id] = self.LOOP_PENALTY

            #Have the values converged?
            if convergence_dict != node_dict:
                run_convergence = True

            node_dict = convergence_dict

        #Finally update the bellman values to those calculated
        for node_id, v in node_dict.items():
            self.db.node(node_id)['bellman_value'] = v


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
        state_hash = self.hash_string('-'.join([problem_string, state_string]))
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
        state_hash = self.hash_string('-'.join([problem_string, state_string]))
        try:
            if not self.hint_exists(problem_string,state_string):
                raise HintDoesNotExistException("Hint does not exist for state " + str(state_string))
            else:
                node = self.db.get_indexed_node("problems_index","start_string",state_string)
    
                if not node:
                    node = self.db.get_indexed_node("problem_states_index","state_hash",state_hash)
    
                if not node:
                    raise HintDoesNotExistException("Hint does not exist for state " + str(state_string))
                
                child_edges = node.match_outgoing("action")
                max_reward = -999999
                hint = {}
                count = 0
                for edge in child_edges:
                    if edge.end_node["bellman_value"] > max_reward:
                        max_reward = edge.end_node["bellman_value"]
                        hint["hint_text"] = edge["action_string"]
                        hint["hint_result"] = edge.end_node["state_string"]
                    count +=1
                
                if count == 0:
                    raise HintDoesNotExistException("Hint does not exist for state " + str(state_string))
                    
                return hint
        except StateDoesNotExistException:
            raise HintDoesNotExistException("Hint does not exist for state " + str(state_string))
            
            
    
        


class HintFactoryPlugin(Plugin):
    def __init__(self, entity_id, api_key, logger, args = None):
        super().__init__(entity_id, api_key)
        self.logger = logger
        self.hf = SimpleHintFactory()
        
        self.mongo = MongoClient(settings.MONGODB_URI)
        self.hint_db = self.mongo[settings.MONGO_DBNAME].hpit_hints
        

    def post_connect(self):
        super().post_connect()

        self.subscribe({
             "tutorgen.hf_init_problem":self.init_problem_callback, 
             "tutorgen.hf_push_state":self.push_state_callback,
             "tutorgen.hf_hint_exists":self.hint_exists_callback,
             "tutorgen.hf_get_hint":self.get_hint_callback,
             "tutorgen.hf_transaction":self.transaction_callback_method,
             "tutorgen.hf_delete_state":self.delete_state_callback,
             "tutorgen.hf_delete_problem":self.delete_problem_callback,
             "get_student_model_fragment":self.get_student_model_fragment_callback})

    def init_problem_callback(self, message):
        if self.logger:
            self.send_log_entry("INIT PROBLEM")
            self.send_log_entry(message)
            
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
    
    def delete_problem_callback(self,message):
        if self.logger:
            self.send_log_entry("DELETE PPROBLEMj")
            self.send_log_entry(message)
            
        try:
            state=  message["state"]
        except KeyError:
            self.send_response(message["message_id"], {
                "error": "hf_delete_problem requires a 'state'",
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
        
        if self.hf.delete_problem(incoming_state.problem,incoming_state.problem_state):
            self.send_response(message["message_id"],{
                    "status":"OK",
            })
        else:
            self.send_response(message["message_id"],{
                    "status":"NOT_OK",
                    "error":"unable to delete problem",
            })
        
        
    def delete_state_callback(self,message):
        if self.logger:
            self.send_log_entry("DELETE STATE")
            self.send_log_entry(message)
        
        try:
            state=  message["state"]
        except KeyError:
            self.send_response(message["message_id"], {
                "error": "hf_delete_state requires a 'state'",
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
            result = self.hf.delete_node(incoming_state.problem,incoming_state.problem_state)
            if result:
                self.send_response(message["message_id"],{"status":"OK"})
            else:
                self.send_response(message["message_id"],{"status":"NOT_OK"})
        except StateDoesNotExistException as e:
            self.send_response(message["message_id"],{
            "status":"NOT_OK",
            "error": str(e)
            })
        
    def push_state_callback(self, message):
        if self.logger:
            self.send_log_entry("PUSH PROBLEM STATE")
            self.send_log_entry(message)
            
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
        except GoalDoesNotExistException as e:
            self.send_response(message["message_id"], {
            "status": "NOT_OK",
            "error": str(e)
            })

    def hint_exists_callback(self, message):
        if self.logger:
            self.send_log_entry("HINT EXISTS")
            self.send_log_entry(message)
            
        try:
            state=  message["state"]
        except KeyError:
            self.send_response(message["message_id"], {
                "error": "hf_hint_exists requires a 'state'",
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
            self.send_log_entry("GET HINT")
            self.send_log_entry(message)
        
        try:
            state=  message["state"]
        except KeyError:
            self.send_response(message["message_id"], {
                "error": "hf_get_hint requires a 'state'",
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
                self.send_response(message["message_id"],{"status":"OK","exists":"YES","hint_text":hint["hint_text"],"hint_result":hint["hint_result"]})
                if "student_id" in message:
                    self.hint_db.update({"student_id":str(message["student_id"]),"state":state,"hint_text":hint["hint_text"],"hint_result":hint["hint_result"]},{"$set":{"hint_text":hint["hint_text"],"hint_result":hint["hint_result"],}},upsert=True)
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
            
    def get_student_model_fragment_callback(self,message):
        if self.logger:
            self.send_log_entry("GET STUDENT MODEL FRAGMENT" + str(message))
            
        try:
            student_id = message["student_id"]
        except KeyError:
            self.send_response(message["message_id"],{
                "error":"hint_factory get_student_model_fragment requires 'student_id'"       
            })
            return
            
        hints_received = self.hint_db.find({"student_id":student_id})
        hints = [h for h in hints_received]
        
        self.send_response(message["message_id"],{
               "name":"hint_factory",
               "fragment": hints,
        })
        
    def transaction_callback_method(self,message):
        
        hint_exists = False
        hint = ""

        if self.logger:
            self.send_log_entry("RECV: transaction with message " + str(message))
        
        if "outcome" not in message:
            self.send_response(message["message_id"],{"error": "'outcome' is not present for hint factory transaction.","responder":"hf"})
            return
        elif message["outcome"] != "hint":
            self.send_response(message["message_id"],{"error": "'outcome' is not 'hint' for hint factory transaction.","responder":"hf"})
            return
            
        try:
            state=  message["state"]
        except KeyError:
            self.send_response(message["message_id"],{"error": "'state' required for hint factory transactions.","responder":"hf"})
            return
        
        incoming_state = self.get_incoming_state(message["state"])
        if not incoming_state:
            self.send_response(message["message_id"],{"error": "'state' is invalid for hint factory transaction.","responder":"hf"})
            return
            
        try:
            new_hint = self.hf.get_hint(incoming_state.problem,incoming_state.problem_state)
            if new_hint:
                hint = new_hint
                hint_exists = True
                if "student_id" in message:
                    self.hint_db.update({"student_id":str(message["student_id"]),"state":state,"hint_text":hint},{"$set":{"hint_text":hint,}},upsert=True)
            else:
                hint = ""
                hint_exists = False       
        except HintDoesNotExistException as e:
            hint = ""
            hint_exists = False
        
        response = {}
        response["hint_text"] = hint
        response["hint_exists"] = hint_exists
        response["responder"]  = "hf"
        self.send_response(message["message_id"],response)
            
            
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

