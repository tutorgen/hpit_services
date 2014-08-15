import unittest
from mock import *

from plugins import HintFactoryPlugin
from plugins import SimpleHintFactory
from utils.hint_factory_state import *

class TestSimpleHintFactory(unittest.TestCase):
    def test(self):
        pass
    
    
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
                "success":False
            })
        msg["start_state"] = "2 + 2 = 4"
        self.test_subject.init_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "error": "hf_init_problem requires a 'start_state' and 'goal_problem'",
                "success":False
            })
        
        msg["goal_problem"] = "4 = 4"
        self.test_subject.init_problem_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "status": "NOT_OK",
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
                "success":False
            })
        self.test_subject.send_response.reset_mock()
        
        msg["state"] = 4
        self.test_subject.push_state_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "status":"NOT_OK",
            })
        self.test_subject.send_response.reset_mock()
        
        msg["state"] = HintFactoryState("2 + 2 = 4")
        self.test_subject.push_state_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "status":"NOT_OK",
            })
        self.test_subject.send_response.reset_mock()
        
        msg["state"] = HintFactoryStateEncoder().encode(HintFactoryState("2 + 2 = 4"))
        self.test_subject.push_state_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "status":"NOT_OK",
            })
        self.test_subject.send_response.reset_mock()
        
        hf = HintFactoryState("2 + 2 = 4")
        hf.append_step("simplify","4=4")
        msg["state"]=  HintFactoryStateEncoder().encode(hf)
        self.test_subject.push_state_callback(msg)
        self.test_subject.send_response.assert_called_with("1", {
                "status":"OK",
            })
        self.test_subject.send_response.reset_mock()
        
    def test_hint_exists_callback(self):
        """
        HintFactoryPlugin.hint_exists_callback() Test plan:
        """
    
    def test_get_hint_callbackl(self):
        """
        HintFactoryPlugin.get_hint_callback() Test plan:
        """
        
    
