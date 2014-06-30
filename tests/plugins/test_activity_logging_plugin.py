import httpretty
import sure
from client.settings import HPIT_URL_ROOT
from plugins import StudentActivityLoggingPlugin
from unittest.mock import *

test_subject = None
def setup_function(function):
	""" setup any state tied to the execution of the given method in a
    class.  setup_method is invoked for every test method of a class.
    """
	global test_subject
	httpretty.enable()
	httpretty.register_uri(httpretty.POST, HPIT_URL_ROOT+"/connect",
							body='{"entity_name":"student_activity_logging_plugin", "entity_id":"4"}',
							)
	httpretty.register_uri(httpretty.POST, HPIT_URL_ROOT+"/plugin/subscribe",
							body='',
							)
	test_subject = StudentActivityLoggingPlugin(1234, 5678, None)

def teardown_function(function):
	""" teardown any state that was previously setup with a setup_method
    call.
    """
    global test_subject

    httpretty.disable()
    httpretty.reset()
    test_subject = None

def test_constructor():
	"""
    StudentActivityLoggingPlugin.__init__() Test Plan:
        -ensure logger is set to param
    """
    test_subject.logger.should.equal(None)

def test_post_connect():
	"""
    StudentActivityLoggingPlugin.post_connect() Test plan:
        -ensure callbacks are set for test and example
    """
    test_subject.post_connect()
    test_subject.callbacks['activity_logging'].should.equal(test_subject.log_student_activity_callback)


def test_log_student_activity_callback():
	"""
    StudentActivityLoggingPlugin.log_student_activity_callback() Test plan:
        -Mock logger, ensure written to when called
        -Mock mongodb, ensure written to when called
        -Mock send_response, ensure called
    """
	test_message = "This is a message"
	calls = [call("LOG_STUDENT_ACTIVITY"), call(test_message)]
	test_subject.logger = Mock()
	test_subject.logger.debug.assert_has_calls(calls)

	test_subject.validateMessage = MagicMock(return_value=True)
	#test mongodb is written
	test_subject.mongo.db.student_activity_log.insert = MagicMock()
	test_subject.mongo.db.student_activity_log.insert.assert_called_with()

	test_subject.validateMessage = MagicMock(return_value=False)
	#test send_response is called correctly
	test_subject.send_response = MagicMock()
	test_subject.send_response.assert_called_with()

def test_validateMessage():
	"""
	StudentActivityLoggingPlugin.validateMessage() Test plan:
        -ensure True is returned when sub, verb, and obj are the right type
        -ensure False is returned and error is updated when otherwise 
	"""
	error = {}
	test_subject.validateMessage("i", "made", "it", error).should.equal(True)

	test_subject.validateMessage(5, "made", "it", error).should.equal(False)
	error.should.equal({'error': 'sub, verb, and obj all have to be strings'})






