from client import Plugin

from pymongo import MongoClient

class StudentManagementPlugin(Plugin):

    def __init__(self, entity_id, api_key, logger, args = None):
        super().__init__(entity_id, api_key)
        self.logger = logger
        self.mongo = MongoClient('mongodb://localhost:27017/')
        self.db = self.mongo.hpit_students

        self.subscribe(
            add_student=self.add_student_callback,
            remove_student=self.remove_student_callback,
            get_student=self.get_student_callback)

    #Student Management Plugin
    def add_student_callback(self, message):
        self.logger.debug("ADD_STUDENT")
        self.logger.debug(message)

    def remove_student_callback(self, message):
        self.logger.debug("REMOVE_STUDENT")
        self.logger.debug(message)

    def get_student_callback(self, message):
        self.logger.debug("GET_STUDENT")
        self.logger.debug(message)
