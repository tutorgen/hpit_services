import unittest
from mock import *

import random

from hpit.tutors import ReplayTutor2

class TestReplayTutor2(unittest.TestCase):

    def setUp(self):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.test_subject = ReplayTutor2(123,456,None)
        self.test_subject.should_dispatch_async = False
        
    def tearDown(self):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        self.test_subject = None
        
    def test_constructor(self):
        """
        ReplayTutor2.__init__() Test plan:
            - run_once, logger, skills, student_id all set
            - random.seed() called
        """
        random.seed = MagicMock()
        
        tmp_subject = ReplayTutor2(123,456,None)
        tmp_subject.logger.should.equal(None)
        tmp_subject.run_once.should.equal(None)
        tmp_subject.student_id_value.should.equal(None)
        tmp_subject.session_id_value.should.equal(None)
        
        
    def test_post_connect(self):
        """
        ReplayTutor2.post_connect() Test plan:
            - mock send, make sure called
        """
        self.test_subject.send = MagicMock()
        self.test_subject.post_connect()
        self.test_subject.send.assert_called_with("tutorgen.add_student",{},self.test_subject.new_student_callback)
    
    def test_setup_gui(self):
        """
        ReplayTutor2.setup_gui() Test plan:
            - not testing
        """
        pass
    
    def test_main_loop(self):
        """
        ReplayTutor2.main_loop() Test plan:
            - set self.callback to return false, should raise exception
            - make _dispatch_response return false, should throw exception
            - otherwise, should call self.root.after
        """
        #set up mocks
        self.test_subject._poll_responses = MagicMock(return_value="response")
        
        #callback returns false
        self.test_subject.callback = MagicMock(return_value=False)
        self.test_subject.main_loop.when.called_with().should.throw(Exception)
        
        #_dispatch responses returns false
        self.test_subject.callback = MagicMock(return_value=True)
        self.test_subject._dispatch_responses = MagicMock(return_value=False)
        self.test_subject.main_loop.when.called_with().should.throw(Exception)
        
        #should call after
        self.test_subject._dispatch_responses = MagicMock(return_value=True)
        self.test_subject.root = MagicMock()
        self.test_subject.main_loop()
        self.test_subject.root.after.assert_called_with(self.test_subject.poll_wait,self.test_subject.main_loop) 
    
    def test_import_datashop_file(self):
        """
        ReplayTutor2.import_datashop_file() Test plan:
            - not testing
        """
        pass
    
    def test_kt_trace(self):
        """
        ReplayTutor2.kt_trace() Test plan:
            - mock GUI elements
            - set outcome.get to return "correct", response should reflect that
            - set outcome.get to return "bwee", response should reflect that
        """
        
        self.test_subject.send = MagicMock()
        #mock GUI
        self.test_subject.student_id = MagicMock()
        self.test_subject.student_id.get.return_value = "123"
        self.test_subject.skill_id = MagicMock()
        self.test_subject.skill_id.get.return_value = "456"
        self.test_subject.outcome = MagicMock()
        self.test_subject.outcome.get.return_value = "correct"
        
        #correct
        self.test_subject.kt_trace()
        self.test_subject.send.assert_called_with("tutorgen.kt_trace",{
             "student_id":"123",
            "correct":True,
            "skill_id":"456",
        }, self.test_subject.transaction_response_callback)
        self.test_subject.send.reset_mock()
        
        #incorrect
        self.test_subject.outcome.get.return_value = "incorrect"
        self.test_subject.kt_trace()
        self.test_subject.send.assert_called_with("tutorgen.kt_trace",{
             "student_id":"123",
            "correct":False,
            "skill_id":"456",
        }, self.test_subject.transaction_response_callback)
        self.test_subject.send.reset_mock()
        
    
    def test_set_attribute(self):
        """
        ReplayTutor2.set_attribute() Test plan:
            - mock GUI elements, make sure send is sent with them
        """
        self.test_subject.student_id = MagicMock()
        self.test_subject.student_id.get.return_value="sid"
        self.test_subject.attr_name = MagicMock()
        self.test_subject.attr_name.get.return_value="aname"
        self.test_subject.attr_value = MagicMock()
        self.test_subject.attr_value.get.return_value="aval"
        
        self.test_subject.send=MagicMock()
        self.test_subject.set_attribute()
        self.test_subject.send.assert_called_with("tutorgen.set_attribute",{
            "student_id":"sid",
            "attribute_name":"aname",
            "attribute_value":"aval",
        }, self.test_subject.transaction_response_callback)
        
    
    def test_populate_form(self):
       """
       ReplayTutor2.populate_form() Test plan:
            - not testing
       """
       pass
    
    def test_new_student_callback(self):
        """
        ReplayTutor2.new_student_callback() Test plan:
            - make sure stdent_id_value and session_id_value are properly set
        """
        self.test_subject.student_id = MagicMock()
        self.test_subject.session_id = MagicMock()
        self.test_subject.button=MagicMock()
        self.test_subject.attr_button=MagicMock()
        self.test_subject.kt_button=MagicMock()
        
        response = {"student_id":"3","session_id":"5"}
        self.test_subject.new_student_callback(response)
        self.test_subject.student_id_value.should.equal("3")
        self.test_subject.session_id_value.should.equal("5")
    
    def test_transaction_response_callback(self):
        """
        ReplayTutor2.transaction_response_callback() Test plan:
            - not testing
        """
        pass
    
    def test_submit_transaction(self):
        """
        ReplayTutor2.submit_transaction() Test plan:
            - mock send, set json_in, make sure called properly
        """
        self.test_subject.problem_name = MagicMock()
        self.test_subject.problem_name.get.return_value="pname"
        self.test_subject.step_name = MagicMock()
        self.test_subject.step_name.get.return_value="sname"
        self.test_subject.transaction_id = MagicMock()
        self.test_subject.transaction_id.get.return_value="tid"
        self.test_subject.student_id = MagicMock()
        self.test_subject.student_id.get.return_value="sid"
        self.test_subject.outcome = MagicMock()
        self.test_subject.outcome.get.return_value="out"
        self.test_subject.session_id = MagicMock()
        self.test_subject.session_id.get.return_value="sess"
        
        self.test_subject.send_transaction=MagicMock()
        
        self.test_subject.json_in = {"Default":"skill_name"}
        
        self.test_subject.submit_transaction()
        self.test_subject.send_transaction.assert_called_with({
            "problem_name":"pname",
            "step_text":"sname",
            "transaction_text":"tid",
            "session_id":"sess",
            'skill_ids': {"skill_name":""},
            'skill_names': {"Default":"skill_name"},
            'student_id':"sid",
            'outcome': "out",
        }, self.test_subject.transaction_response_callback)
        
    
    def test_main_callback(self):
        """
        ReplayTutor2.main_callback() Test plan:
            - make sure returns true
        """
        self.test_subject.main_callback().should.equal(True)
              
        
