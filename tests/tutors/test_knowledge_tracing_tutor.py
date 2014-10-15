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
        tmp_subject.skill_ids.should.equal({'addition':None, 'subtraction':None, 'multiplication':None, 'division':None})
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
        self.test_subject.skill_ids["addition"] = "+"
        self.test_subject.skill_ids["subtraction"] = "-"
        self.test_subject.skill_ids["multiplication"] = "*"
        self.test_subject.skill_ids["division"] = "/"
        calls = [
            call('kt_reset',{'skill_id':"+","student_id":"2"}),
            call('kt_reset',{'skill_id':"-","student_id":"2"}),
            call('kt_reset',{'skill_id':"*","student_id":"2"}),
            call('kt_reset',{'skill_id':"/","student_id":"2"}),
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
        
        self.test_subject.main_callback().should.equal(True)
        self.test_subject.send.call_count.should.equal(0)
        
        self.test_subject.skill_ids["addition"] = "+"
        self.test_subject.skill_ids["subtraction"] = "-"
        self.test_subject.skill_ids["multiplication"] = "*"
        self.test_subject.skill_ids["division"] = "/"
        
        random.randint = MagicMock(return_value = 91)
        calls = []
        calls.append(call('get_student_model',{
            "student_id":"2",        
        },self.test_subject.get_student_model_callback
            )
        )
        for sk in ["addition","subtraction","multiplication","division"]:
            calls.append(
                call('kt_trace', {
                    'skill_id': self.test_subject.skill_ids[sk],
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
        self.test_subject.send.call_count.should.equal(1)
        
        
    
    def test_trace_response_callback(self):
        """
        KnowledgeTracingTutor.trace_response_callback() Test plan:
            -mock logger, should be called
            -mock send_log_entry, should be called
        """
        self.test_subject.send_log_entry= MagicMock()
        self.test_subject.trace_response_callback("this is a response")
        self.test_subject.send_log_entry.assert_called_with("RECV: kt_trace response recieved. this is a response")
    
    def test_initial_response_callback(self):
        """
        KnowledgeTracingTutor.initial_response_callback() Test plan:
            -mock logger, should be called
            -mock send_log_entry, should be called
        """
        self.test_subject.send_log_entry = MagicMock()
        self.test_subject.initial_response_callback("this is a response")
        self.test_subject.send_log_entry.assert_called_with("RECV: kt_set_initial response recieved. this is a response")
    
    def test_new_student_callback(self):
        """
        KnowledgeTracingTutor.new_student_callback() Test plan:
            - student id should be set to response student id
            - mock send, should be called for each skill with get_skill_id
        """
        self.test_subject.send = MagicMock()
        self.test_subject.student_id = "2"
        
        calls = []
        for sk in ["addition","subtraction","multiplication","division"]:
            calls.append(
                call("get_skill_id",{"skill_name":sk},self.test_subject.get_skills_callback)
            )
            
        self.test_subject.new_student_callback({"student_id":"2"})
        self.test_subject.send.assert_has_calls(calls)
    
    def test_get_skills_callback(self):
        """
        KnowledgeTracingTutor.get_skills_callback() Test plan:
            - make sure skill_ids set for incoming skill
            - make sure kt_set_initial is called for that skill
        """
        
        self.test_subject.send = MagicMock()
        self.test_subject.student_id = "2"
        
        random.randint = MagicMock(return_value = 1000.0)
        
        self.test_subject.get_skills_callback({"skill_id":"+","skill_name":"addition"})
  
        self.test_subject.send.assert_called_with('kt_set_initial', {
            'skill_id': "+",
            'probability_known': 1.0,
            'probability_learned': 1.0,
            'probability_guess': 1.0,
            'probability_mistake':1.0,
            'student_id':"2"
            }, self.test_subject.initial_response_callback 
        )
        self.test_subject.skill_ids["addition"].should.equal("+")
              
        
