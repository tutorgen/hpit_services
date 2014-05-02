from lib import Plugin

class StudentManagementPlugin(Plugin):

    def __init__(self, name, logger):
        super().__init__(name)
        self.logger = logger

        self.subscribe(
            add_student=self.add_student_callback,
            remove_student=self.remove_student_callback,
            get_student=self.get_student_callback)

    #Student Management Plugin
    def add_student_callback(self, transaction):
        self.logger.debug("ADD_STUDENT")
        self.logger.debug(transaction)

    def remove_student_callback(self, transaction):
        self.logger.debug("REMOVE_STUDENT")
        self.logger.debug(transaction)

    def get_student_callback(self, transaction):
        self.logger.debug("GET_STUDENT")
        self.logger.debug(transaction)
