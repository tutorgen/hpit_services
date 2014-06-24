from client import Plugin
from pymongo import MongoClient

class StudentActivityLoggingPlugin(Plugin):
	def __init__(self, name, logger, args=None):
		super().__init__(name=name)
		self.logger = logger
		self.mongo = MongoClient('mongodb://localhost:27017')

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
		Return False otherwise
		"""
		#mbox field is required
		if not 'mbox' in sub:
			error.update({'format_error' : 'miss mbox field in subject'})
			return False

		#id, display fields are required
		if not ('id' in verb and 'display' in verb):
			error.update({'format_error' : 'miss id or display field in verb'})
			return False

		#id is required
		if not 'id' in obj:
			error.update({'format_error' : 'miss id field in object'})
			return False

		return True


