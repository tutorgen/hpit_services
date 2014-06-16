from client import Plugin
from pymongo import MongoClient
import logging
import os

logger_path = ps.path.join(os.getcwd(), 'log/' + 'log_student_activity/' + 'info.log')
logging.basicConfig(filename=logger_path,
					level=logging.INFO,
					propagate=False,
					format='%(asctime)s %(levelname)s:----:%(message)s', 
            		datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)

class StudentActivityLoggingPlugin(Plugin):
	def __init__(self, name, logger, args=None):
		super().__init__(name)
		self.logger = logger
		self.mongo = MongoClient('mongodb://localhost:27017')
		self.db = self.mongo.hpit_student_activity_logging

		self.subscribe(log_student_activity=self.log_student_activity_callback)

	def log_student_activity_callback(self, message):
		self.logger.debug("LOG_STUDENT_ACTIVITY")
		self.logger.debug(message)
		#poll messages from HPIT server, messages is a python dictionary
		messages = self._poll()
		for key, value in messages.items():
			logger.info(key)
			logger.info(value)