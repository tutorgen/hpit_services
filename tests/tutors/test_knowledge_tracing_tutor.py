import unittest
from mock import *

import random

from tutors import KnowledgeTracingTutor

class TestKnowledgeTracingTutor(unittest.TestCase):

    def setUp(self):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.test_subject = KnowledgeTracingTutor(123,456,None)
        
    def tearDown(self):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        self.test_subject = None
        
    def test_constructor(self):
        """
        KnowledgeTracingTutor.__init__() Test plan:
            - run_once, logger, skills, student_id all set
            - random.seed() called
        """
        random.seed = MagicMock()
        
        tmp_subject = KnowledgeTracingTutor(123,456,None)
        tmp_subject.logger.should.equal(None)
        tmp_subject.run_once.should.equal(None)
        tmp_subject.skills.should.equal(['addition', 'subtraction', 'multiplication', 'division'])
        tmp_subject.student_id.should.equal(None)
        
        
    def test_post_connect(self):
        """
        KnowledgeTracingTutor.post_connect() Test plan:
            - mock send, make sure called
        """
        self.test_subject.send = MagicMock()
        self.test_subject.post_connect()
        self.test_subject.send.assert_called_with("add_student",{},self.test_subject.new_student_callback)
    
    def test_pre_disconnect(self):
        """
        KnowledgeTracingTutor.pre_disconnect() Test plan:
            - mock send, make sure called for every skill
        """
        self.test_subject.send = MagicMock()
        self.test_subject.student_id = "2"
        calls = [
            call('kt_reset',{'skill':'addition',"student_id":"2"}),
            call('kt_reset',{'skill':'subtraction',"student_id":"2"}),
            call('kt_reset',{'skill':'multiplication',"student_id":"2"}),
            call('kt_reset',{'skill':'division',"student_id":"2"}),
        ]
        self.test_subject.pre_disconnect()
        self.test_subject.send.assert_has_calls(calls)
            
    
    def test_main_callback(self):
        """
        KnowledgeTracingTutor.main_callback() Test plan:
            - call with student_id none, should return true, send should not be called
            - call with student_id not_none
            - Mock randint to return 91, send called with each skill, correct true
            - mock randint to return 90, send not called
            - should return true
        """
        self.test_subject.student_id = None
        self.test_subject.send = MagicMock()
        
        self.test_subject.main_callback().should.equal(True)
        self.test_subject.send.call_count.should.equal(0)
        
        self.test_subject.student_id = "2"
        random.randint = MagicMock(return_value = 91)
        calls = []
        for sk in ["addition","subtraction","multiplication","division"]:
            calls.append(
                call('kt_trace', {
                    'skill': sk,
                    'student_id':"2",
                    'correct': True
                    }, self.test_subject.trace_response_callback
                )
            )
            
        self.test_subject.main_callback().should.equal(True)
        self.test_subject.send.assert_has_calls(calls)
        self.test_subject.send.reset_mock()
        
        random.randint = MagicMock(return_value = 90)
        self.test_subject.main_callback().should.equal(True)
        self.test_subject.send.call_count.should.equal(0)
        
        
    
    def test_trace_response_callback(self):
        """
        KnowledgeTracingTutor.trace_response_callback() Test plan:
            -mock logger, should be called
            -mock send_log_entry, should be called
        """
        self.test_subject.logger= MagicMock()
        self.test_subject.send_log_entry = MagicMock()
        self.test_subject.trace_response_callback("this is a response")
        self.test_subject.logger.debug.assert_called_with("RECV: kt_trace response recieved. this is a response")
        self.test_subject.send_log_entry.assert_called_with("RECV: kt_trace response recieved. this is a response")
    
    def test_initial_response_callback(self):
        """
        KnowledgeTracingTutor.initial_response_callback() Test plan:
            -mock logger, should be called
            -mock send_log_entry, should be called
        """
        self.test_subject.logger= MagicMock()
        self.test_subject.send_log_entry = MagicMock()
        self.test_subject.initial_response_callback("this is a response")
        self.test_subject.logger.debug.assert_called_with("RECV: kt_set_initial response recieved. this is a response")
        self.test_subject.send_log_entry.assert_called_with("RECV: kt_set_initial response recieved. this is a response")
    
    def test_new_student_callback(self):
        """
        KnowledgeTracingTutor.new_student_callback() Test plan:
            - student id should be set to response student id
            - mock send, should be called for each skill with kt_set_initial
        """
        self.test_subject.send = MagicMock()
        self.test_subject.student_id = "2"
        random.randint = MagicMock(return_value = 1000.0)
        calls = []
        for sk in ["addition","subtraction","multiplication","division"]:
            calls.append(
                    call('kt_set_initial', {
                        'skill': sk,
                        'probability_known': 1.0,
                        'probability_learned': 1.0,
                        'probability_guess': 1.0,
                        'probability_mistake':1.0,
                        'student_id':"2"
                        }, self.test_subject.initial_response_callback 
                    )
              )
        self.test_subject.new_student_callback({"student_id":"2"})
        self.test_subject.send.assert_has_calls(calls)
        
