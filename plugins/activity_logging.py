from client import Plugin
from pymongo import MongoClient

class StudentActivityLoggingPlugin(Plugin):
	def __init__(self, entity_id, api_key, logger, args=None):
		super().__init__(entity_id=entity_id, api_key=api_key)
		self.logger = logger
		self.mongo = MongoClient('mongodb://localhost:27017')
	

	def post_connect(self):
		super().post_connect()
		self.subscribe(activity_logging=self.log_student_activity_callback)

	def log_student_activity_callback(self, message):
		"""
		First verify the validity of the message.
		Store the message in database if the message is valid.
		Otherwise
		"""
		#log
		self.logger.debug("LOG_STUDENT_ACTIVITY")
		self.logger.debug(message)
		#validate the message
		sub = message['subject']
		verb = message['verb']
		obj = message['object']
		entity_id = message['entity_id']
		message_id = message['id']
		error = {}
		#the message is valid, store it
		if self.validateMessage(sub, verb, obj, error):
			self.mongo.db.student_activity_log.insert({
				'subject' : sub,
				'verb' : verb,
				'object' : obj,
				'entity_id' : entity_id
			})
		else:
			self.send_response(message_id=message_id, payload=error)

	def validateMessage(self, sub, verb, obj, error):
		"""
		Validate the message
		Return True if the message is valid
		Return False and populate error otherwise
		"""
		#for now, as long as sub, verb, and obj are strings, return True
		if type(sub) is type('str') and type(verb) is type('str') and type(obj) is type('str'):
			return True
		else:
			error.update({'error': 'sub, verb, and obj all have to be strings'})
			return False


