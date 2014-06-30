from tutors import StudentActivityLoggingTutor
import httpretty
from client.settings import HPIT_URL_ROOT
import sure
from unittest.mock import *


test_subject = None
def setup_funciton(funciton):
	""" setup any state tied to the execution of the given method in a
    class.  setup_method is invoked for every test method of a class.
    """
	global test_subject
	test_subject = StudentActivityLoggingTutor(1234, 5678, None)
	httpretty.enable()
	httpretty.register_uri(httpretty.POST, HPIT_URL_ROOT+"/connect",
							body='{"entity_name":"student_activity_logging_tutor","entity_id":"4"}',
							)

def teardown_function(funciton):
	""" teardown any state that was previously setup with a setup_method
    call.
    """
	global test_subject

    httpretty.disable()
    httpretty.reset()
    test_subject = None

def test_constructor():
	"""
    StudentActivityLoggingTutor.__init__() Test plan:
        -Ensure run_once, logger set correctly
    """
	test_subject.logger.should.equal(None)
	test_subject.run_once.should.equal(run_once)

def test_work():
	"""
    StudentActivityLoggingTutor.work() Test plan:
        -Ensure send() is called
    """
    test_subject.send = MagicMock()
    test_subject.send.assert_called_with()


