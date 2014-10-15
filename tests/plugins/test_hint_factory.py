import unittest
from mock import *

from plugins import HintFactoryPlugin
from plugins import SimpleHintFactory
from plugins import StateDoesNotExistException
from plugins import HintDoesNotExistException

from utils.hint_factory_state import *

import hashlib

from py2neo import neo4j

class TestSimpleHintFactory(unittest.TestCase):
    def setUp(self):
        self.test_subject = SimpleHintFactory()
        self.test_subject.db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
        for node in self.test_subject.db.find("_unit_test_only"):
            node.delete_related()
            
    def tearDown(self):
        for node in self.test_subject.db.find("_unit_test_only"):
            node.delete_related()
        self.test_subject = None
        
    def test_constructor(self):
        """
        SimpleHintFactory.__init__() Test plan:
            - make sure DISCOUNT_FACTOR, GOAL_REWARD, STD_REWARD
            - make sure self.db is a graphdatabase service
        """
        test_subject = SimpleHintFactory()
        isinstance(test_subject.db,neo4j.GraphDatabaseService).should.equal(True)
        test_subject.DISCOUNT_FACTOR.should.equal(.5)
        test_subject.GOAL_REWARD.should.equal(100)
        test_subject.STD_REWARD.should.equal(0)
    
    def test_push_node(self):
        """
        SimpleHintFactory.push_node() Test plan:
            - if not problem_node, issue statedoesnotexistexception
            - if from node doesnt exist, either problem or state, should raise statedoesnotexistexception
            - it to state does not exist, new node should exist
            - if state exists and edge, taken count should be incremented
            - update action probabilities should be called
            - bellman update should be called
        """
        self.test_subject.update_action_probabilities = MagicMock()
        self.test_subject.bellman_update = MagicMock()
        self.test_subject.push_node.when.called_with("problem","2+4","add","4+4").should.throw(StateDoesNotExistException)
        
        problem_node, = self.test_subject.db.create({"start_string":"problem","goal_string":"goal","discount_factor":0.5})
        problem_index = self.test_subject.db.get_or_create_index(neo4j.Node,"problems_index")
        problem_index.add("start_string","problem",problem_node)
        problem_node.add_labels("_unit_test_only")
        
        self.test_subject.push_node.when.called_with("problem","2+4","add","4+4").should.throw(StateDoesNotExistException)
        
        self.test_subject.push_node("problem","problem","add","4+5")
        self.test_subject.update_action_probabilities.call_count.should_not.equal(0)
        self.test_subject.update_action_probabilities.reset_mock()
        
        state_hash = hashlib.sha256(bytes("problem-4+5".encode('utf-8'))).hexdigest()
        new_node = self.test_subject.db.get_indexed_node("problem_states_index","state_hash",state_hash)
        new_node.should_not.equal(None)
        
        self.test_subject.push_node("problem","problem","add","4+5")
        self.test_subject.update_action_probabilities.call_count.should_not.equal(0)
        self.test_subject.update_action_probabilities.reset_mock()
        
        edge = next(problem_node.match_outgoing("action",new_node))
        edge.should_not.equal(None)
        edge["taken_count"].should.equal(2)
        
        self.test_subject.bellman_update.call_count.should.equal(2)
        
        problem_node.delete_related()
    
    def test_hash_string(self):
        """
        SimpleHintFactory.hash_string() Test plan:
            - test with string and number, should return expected results
        """
        self.test_subject.hash_string("hello").should.equal(hashlib.sha256(bytes("hello".encode('utf-8'))).hexdigest())
        self.test_subject.hash_string(4).should.equal(hashlib.sha256(bytes("4".encode('utf-8'))).hexdigest())
    
    def test_update_action_probabilities(self):
        """
        SimpleHintFactory.update_action_probabilities() Test plan:
            - populate database with a parent with 3 children, one with transition not action
                - relationships should have counts
                - afterwards, edges should have predicted values
            - remove entry from database
        """
        
        root_node = self.test_subject.db.create({"name":"start"})[0]
        root_node.add_labels("_unit_test_only")

        node_1, rel_1 = self.test_subject.db.create({"name":"node_1"},(root_node,"action",0))
        rel_1["taken_count"] = 1
        rel_1["probability"] = 0
        
        node_2, rel_2 = self.test_subject.db.create({"name":"node_2"},(root_node,"action",0))
        rel_2["taken_count"] = 3
        rel_2["probability"] = 0
        
        node_3, rel_3 = self.test_subject.db.create({"name":"node_3"},(root_node,"bogus",0))
        rel_3["taken_count"] = 5
        rel_3["probability"] = 0
        
        self.test_subject.update_action_probabilities(rel_2)
        
        rel_1["probability"].should.equal(.25)
        rel_2["probability"].should.equal(.75)
        rel_3["probability"].should.equal(0)
        
        root_node.delete_related()
    
    def test_bellman_update(self):
        """
        SimpleHintFactory._do_bellman() Test plan:
            - add some states
            - make sure bellman values are what is expected
        """
        
        problem_node, = self.test_subject.db.create({"start_string":"state","goal_string":"state_4","discount_factor":0.5})
        problem_index = self.test_subject.db.get_or_create_index(neo4j.Node,"problems_index")
        problem_index.add("start_string","state",problem_node)
        problem_node.add_labels("_unit_test_only")
        
        state_string = "state_2"
        state_hash = hashlib.sha256(bytes('-'.join(['state', state_string]).encode('utf-8'))).hexdigest()
        new_node, new_rel = self.test_subject.db.create({"state_string":state_string,"state_hash":state_hash,"bellman_value":0,"discount_factor":0.5},(problem_node,"action",0))
        problem_states_index = self.test_subject.db.get_or_create_index(neo4j.Node,"problem_states_index")
        problem_states_index.add("state_hash",state_hash,new_node)
        new_rel["probability"] = .75
        
        state_string = "state_3"
        state_hash = hashlib.sha256(bytes('-'.join(['state', state_string]).encode('utf-8'))).hexdigest()
        another_node, another_rel = self.test_subject.db.create({"state_string":state_string,"state_hash":state_hash,"bellman_value":0,"discount_factor":0.5},(new_node,"action",0))
        problem_states_index = self.test_subject.db.get_or_create_index(neo4j.Node,"problem_states_index")
        problem_states_index.add("state_hash",state_hash,another_node)
        another_rel["probability"] = .25
        
        state_string = "state_4"
        state_hash = hashlib.sha256(bytes('-'.join(['state', state_string]).encode('utf-8'))).hexdigest()
        goal_node, goal_rel1, goal_rel2 = self.test_subject.db.create({"state_string":state_string,"state_hash":state_hash,"bellman_value":0,"discount_factor":0.5},(new_node,"action",0),(problem_node,"action",0))
        problem_states_index = self.test_subject.db.get_or_create_index(neo4j.Node,"problem_states_index")
        problem_states_index.add("state_hash",state_hash,goal_node)
        goal_rel1["probability"] = 1
        goal_rel2["probability"] = 1
        
        self.test_subject.bellman_update("state","state_4")
        goal_node["bellman_value"].should.equal(100)
        another_rel["bellman_value"] = 50
        new_rel["bellman_value"] = 50
        problem_node["bellman_value"] = 18.75
        
        problem_node.delete_related()
        
    
    def test_create_or_get_problem_node(self):
        """
        SimpleHintFactory.create_or_get_problem_node() Test plan:
            - mock get_indexed_node, if returns true, method should return true
            - if it returns false, a node should be returned
            - cleanup
        """
        self.test_subject.db.get_indexed_node = MagicMock(return_value = True)
        self.test_subject.create_or_get_problem_node("start_string","goal_string").should.equal(True)
        
        self.test_subject.db.get_indexed_node = MagicMock(return_value = None)
        cur = self.test_subject.create_or_get_problem_node("start_string","goal_string")
        isinstance(cur,neo4j.Node).should.equal(True)
        cur.get_properties()["start_string"].should.equal("start_string")
        cur.get_properties()["goal_string"].should.equal("goal_string")
        cur.get_labels().should.contain("Problem")
        
        cur.delete_related()
        
    def test_hint_exists(self):
        """
        SimpleHintFactory.hint_exists() Test plan:
            - with no states, should return false
            - with a problem_states_index
                -with an edge, should return True
                -without an edge, should return False
            - with a problems_index
                -with an edge, should return True
                -without an edge, should return False
        """
        self.test_subject.hint_exists.when.called_with("problem","state").should.throw(StateDoesNotExistException)
        
        problem_node, = self.test_subject.db.create({"start_string":"state","goal_string":"goal","discount_factor":"0.5"})
        problem_index = self.test_subject.db.get_or_create_index(neo4j.Node,"problems_index")
        problem_index.add("start_string","state",problem_node)
        problem_node.add_labels("_unit_test_only")
        
        self.test_subject.hint_exists("problem","state").should.equal(False)
        
        state_string = "state_2"
        state_hash = hashlib.sha256(bytes('-'.join(['problem', state_string]).encode('utf-8'))).hexdigest()
        new_node, new_rel = self.test_subject.db.create({"state_string":state_string,"state_hash":state_hash,"bellman_value":0,"discount_factor":"0.5"},(problem_node,"action",0))
        problem_states_index = self.test_subject.db.get_or_create_index(neo4j.Node,"problem_states_index")
        problem_states_index.add("state_hash",state_hash,new_node)
        
        self.test_subject.hint_exists("problem","state").should.equal(True)
        
        self.test_subject.hint_exists("problem","state_2").should.equal(False)
        
        state_string = "state_3"
        state_hash = hashlib.sha256(bytes('-'.join(['problem', state_string]).encode('utf-8'))).hexdigest()
        another_node, another_rel = self.test_subject.db.create({"state_string":state_string,"state_hash":state_hash,"bellman_value":0,"discount_factor":"0.5"},(new_node,"action",0))
        problem_states_index = self.test_subject.db.get_or_create_index(neo4j.Node,"problem_states_index")
        problem_states_index.add("state_hash",state_hash,another_node)
        
        self.test_subject.hint_exists("problem","state_3").should.equal(False)
        
        problem_node.delete_related()
           
    def test_get_hint(self):
        """
        SimpleHintFactory.get_hint() Test plan:
            - mock hint_exists, if false, should return None
            - if a problem node
                - if no relationships, should return none
                - with 2 relationships, should return string from largest bellman value
            - if a state node
                - if no relationships, should return none
                - with 2 relationships, should return string from largest bellman value
        """
        self.test_subject.hint_exists = MagicMock(return_value = False)
        self.test_subject.get_hint.when.called_with("problem","state").should.throw(HintDoesNotExistException)
        
        self.test_subject.hint_exists = MagicMock(return_value = True)
        
        problem_node, = self.test_subject.db.create({"start_string":"state","goal_string":"goal","discount_factor":"0.5"})
        problem_index = self.test_subject.db.get_or_create_index(neo4j.Node,"problems_index")
        problem_index.add("start_string","state",problem_node)
        problem_node.add_labels("_unit_test_only")
        
        self.test_subject.get_hint.when.called_with("problem","state").should.throw(HintDoesNotExistException)
        
        state_string = "state_2"
        state_hash = hashlib.sha256(bytes(state_string.encode('utf-8'))).hexdigest()
        new_node, new_rel = self.test_subject.db.create({"state_string":state_string,"state_hash":state_hash,"bellman_value":0,"discount_factor":"0.5"},(problem_node,"action",0))
        problem_states_index = self.test_subject.db.get_or_create_index(neo4j.Node,"problem_states_index")
        problem_states_index.add("state_hash",state_hash,new_node)
        new_rel["action_string"] = "bad hint"
        
        state_string = "state_3"
        state_hash = hashlib.sha256(bytes(state_string.encode('utf-8'))).hexdigest()
        another_node, another_rel = self.test_subject.db.create({"state_string":state_string,"state_hash":state_hash,"bellman_value":1,"discount_factor":"0.5"},(problem_node,"action",0))
        problem_states_index = self.test_subject.db.get_or_create_index(neo4j.Node,"problem_states_index")
        problem_states_index.add("state_hash",state_hash,another_node)
        another_rel["action_string"] = "good hint"
        
        self.test_subject.get_hint("problem","state").should.equal("good hint")
        
        self.test_subject.get_hint.when.called_with("problem","state_2").should.throw(HintDoesNotExistException)
        
        state_string = "state_3"
        state_hash = hashlib.sha256(bytes(state_string.encode('utf-8'))).hexdigest()
        new_node2, new_rel2 = self.test_subject.db.create({"state_string":state_string,"state_hash":state_hash,"bellman_value":0,"discount_factor":"0.5"},(new_node,"action",0))
        problem_states_index = self.test_subject.db.get_or_create_index(neo4j.Node,"problem_states_index")
        problem_states_index.add("state_hash",state_hash,new_node2)
        new_rel2["action_string"] = "bad hint"
        
        state_string = "state_5"
        state_hash = hashlib.sha256(bytes(state_string.encode('utf-8'))).hexdigest()
        another_node2, another_rel2 = self.test_subject.db.create({"state_string":state_string,"state_hash":state_hash,"bellman_value":1,"discount_factor":"0.5"},(new_node,"action",0))
        problem_states_index = self.test_subject.db.get_or_create_index(neo4j.Node,"problem_states_index")
        problem_states_index.add("state_hash",state_hash,another_node2)
        another_rel2["action_string"] = "good hint"
        
        self.test_subject.get_hint("problem","state").should.equal("good hint")
        
        problem_node.delete_related()
        
        
class TestHintFactoryPlugin(unittest.TestCase):
    def setUp(self):
        self.test_subject = HintFactoryPlugin(123,456,None)
    
    def tearDown(self):
        self.test_subject = None
        
    def test_constructor(self):
        """
        HintFactoryPlugin.__init__() Test plan:
            -ensure that logger set to none
            -ensure hf is instance of SimpleHintFactory
        """
        hf = HintFactoryPlugin(1,1,None)
        hf.logger.should.equal(None)
        isinstance(hf.hf,SimpleHintFactory).should.equal(True)
    
    def test_init_problem_callback(self):
        """
        HintFactoryPlugin.init_problem_callback() Test plan:
            - try without start state or goal problem, should respond withe error
            - mock hf.create_or_get_problem_node, should be called with message values
            - if returns false, response should be not ok
            - if returns true, response should be ok
        """
        
        self.test_subject.hf.create_or_get_problem_node = MagicMock(return_value = False)
        self.test_subject.send_response = MagicMock()
        
        msg = {"message_id":"1"}
        self.test_subject.init_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "error": "hf_init_problem requires a 'start_state' and 'goal_problem'",
                "status":"NOT_OK"
            })
        msg["start_state"] = "2 + 2 = 4"
        self.test_subject.init_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "error": "hf_init_problem requires a 'start_state' and 'goal_problem'",
                "status":"NOT_OK"
            })
        
        msg["goal_problem"] = "4 = 4"
        self.test_subject.init_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "status": "NOT_OK",
                "error":"Unknown error when attempting to create or get problem state"
            })
        
        self.test_subject.hf.create_or_get_problem_node = MagicMock(return_value = True)
        self.test_subject.init_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "status": "OK",
            })
        
   
    def test_push_state_callback(self):
        """
        HintFactoryPlugin.push_state_callback() Test plan:
            - send without state, should return error
            - put in bogus state, should return error
            - if valid state, make sure push_node and send_response called correctly
        """
        
        self.test_subject.send_response = MagicMock()
        self.test_subject.hf.push_node = MagicMock()
        
        msg = {"message_id":"1"}
        self.test_subject.push_state_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "error": "hf_push_state requires a 'state'",
                "status":"NOT_OK"
            })
        self.test_subject.send_response.reset_mock()
        
        msg["state"] = 4
        self.test_subject.push_state_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "status":"NOT_OK",
                "error":"message's 'state' parameter should be a dict",
            })
        self.test_subject.send_response.reset_mock()
        
        msg["state"] = HintFactoryState(problem="2 + 2 = 4")
        self.test_subject.push_state_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "status":"NOT_OK",
                "error":"message's 'state' parameter should be a dict",
            })
        self.test_subject.send_response.reset_mock()
        
        msg["state"] = dict(HintFactoryState(problem="2 + 2 = 4"))
        self.test_subject.push_state_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "status":"NOT_OK",
                "error":"State must have at least one step"
            })
        self.test_subject.send_response.reset_mock()
        
        self.test_subject.hf.push_node = MagicMock(side_effect=StateDoesNotExistException("State does not exist"))
        hf = HintFactoryState(problem="2 + 2 = 4")
        hf.append_step("simplify","4=4")
        msg["state"]=  dict(hf)
        self.test_subject.push_state_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "status":"NOT_OK",
                "error":"State does not exist",
            })
        self.test_subject.send_response.reset_mock()
        
        self.test_subject.hf.push_node = MagicMock(return_value = 4)
        hf = HintFactoryState(problem="2 + 2 = 4")
        hf.append_step("simplify","4=4")
        msg["state"]= dict(hf)
        self.test_subject.push_state_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "status":"OK",
            })
        self.test_subject.send_response.reset_mock()
        
    def test_hint_exists_callback(self):
        """
        HintFactoryPlugin.hint_exists_callback() Test plan:
            - mock hint_exists, mock send_response
            - pass a bogus state, should respond with error
            - if hint exists, should return exists, if not, should return no
        """
        self.test_subject.send_response = MagicMock()
        self.test_subject.hf.hint_exists = MagicMock(return_value = False)
        
        msg = {"message_id":"1"}
        self.test_subject.hint_exists_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "error": "hf_push_state requires a 'state'",
            "status":"NOT_OK"      
        })
        self.test_subject.send_response.reset_mock()
        
        msg["state"] = 4
        self.test_subject.hint_exists_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "status":"NOT_OK",
            "error":"message's 'state' parameter should be a dict",
        })
        self.test_subject.send_response.reset_mock()
        
        msg["state"] = dict(HintFactoryState(problem="2 + 2 = 4"))
        self.test_subject.hint_exists_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "status":"OK",
            "exists":"NO"
        })
        self.test_subject.send_response.reset_mock()
        
        self.test_subject.hf.hint_exists = MagicMock(side_effect=StateDoesNotExistException("state does not exist"))
        msg["state"] = dict(HintFactoryState(problem="2 + 2 = 4"))
        self.test_subject.hint_exists_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "status":"NOT_OK",
            "error":"state does not exist"
        })
        self.test_subject.send_response.reset_mock()
        
        self.test_subject.hf.hint_exists = MagicMock(return_value=True)
        self.test_subject.hint_exists_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "status":"OK",
            "exists":"YES"
        })
        self.test_subject.send_response.reset_mock()
    
    def test_get_hint_callback(self):
        """
        HintFactoryPlugin.get_hint_callback() Test plan:
            - mock get_hint, send_response
            - pass a bogus state, no state, shoudl respond with error
            - if hint false, should return not exists, otherwise fine
        """
        self.test_subject.send_response = MagicMock()
        self.test_subject.hf.get_hint = MagicMock(return_value=False)
        
        msg = {"message_id":"1"}
        self.test_subject.get_hint_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "error": "hf_push_state requires a 'state'",
            "status":"NOT_OK",
        })
        self.test_subject.send_response.reset_mock()
        
        msg["state"] = 4
        self.test_subject.get_hint_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "status":"NOT_OK",
            "error":"message's 'state' parameter should be a dict",
        })
        self.test_subject.send_response.reset_mock()
        
        msg["state"] = dict(HintFactoryState(problem="2 + 2 = 4"))
        self.test_subject.get_hint_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "status":"OK",
            "exists":"NO"
        })
        self.test_subject.send_response.reset_mock()
        
        self.test_subject.hf.get_hint = MagicMock(side_effect=HintDoesNotExistException("hint does not exist"))
        self.test_subject.get_hint_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "status":"NOT_OK",
            "error":"hint does not exist"
        })
        self.test_subject.send_response.reset_mock()
        
        self.test_subject.hf.get_hint = MagicMock(return_value="hint text")
        self.test_subject.get_hint_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "status":"OK",
            "exists":"YES",
            "hint_text": "hint text"
        })
        self.test_subject.send_response.reset_mock()
        
        msg["student_id"] = "123"
        self.test_subject.hf.get_hint = MagicMock(return_value="hint text")
        self.test_subject.get_hint_callback(msg)
        self.test_subject.send_response.assert_called_with("1",{
            "status":"OK",
            "exists":"YES",
            "hint_text": "hint text"
        })
        self.test_subject.hint_db.find({"student_id":"123","hint_text":"hint text","state": dict(HintFactoryState(problem="2 + 2 = 4"))}).count().should.equal(1)
        self.test_subject.send_response.reset_mock()
    
