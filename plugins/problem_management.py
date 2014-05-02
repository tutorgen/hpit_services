from client import Plugin

from pymongo import MongoClient

class ProblemManagementPlugin(Plugin):

    def __init__(self, name, logger):
        super().__init__(name)
        self.logger = logger
        self.mongo = MongoClient('mongodb://localhost:27017/')
        self.db = self.mongo.hpit_problems

        self.subscribe(
            add_problem=self.add_problem_callback,
            remove_problem=self.remove_problem_callback,
            get_problem=self.get_problem_callback,
            add_problem_step=self.add_problem_step,
            remove_problem_step=self.remove_problem_step,
            get_problem_step=self.get_problem_step_callback)

    #Problem Management Plugin
    def add_problem_callback(self, transaction):
        self.logger.debug("ADD_PROBLEM")
        self.logger.debug(transaction)

    def remove_problem_callback(self, transaction):
        self.logger.debug("REMOVE_PROBLEM")
        self.logger.debug(transaction)

    def get_problem_callback(self, transaction):
        self.logger.debug("GET_PROBLEM")
        self.logger.debug(transaction)

    def add_problem_step_callback(self, transaction):
        self.logger.debug("ADD_PROBLEM_STEP")
        self.logger.debug(transaction)

    def remove_problem_step_callback(self, transaction):
        self.logger.debug("REMOVE_PROBLEM_STEP")
        self.logger.debug(transaction)

    def get_problem_step_callback(self, transaction):
        self.logger.debug("GET_PROBLEM_STEP")
        self.logger.debug(transaction)
