from client import Plugin

from pymongo import MongoClient

class KnowledgeTracingPlugin(Plugin):

    def __init__(self, name, logger):
        super().__init__(name)
        self.logger = logger
        self.mongo = MongoClient('mongodb://localhost:27017/')
        self.db = self.mongo.hpit_knowledge_tracing

        self.subscribe(
            kt_set_initial=self.kt_set_initial_callback,
            kt_trace=self.knowledge_tracing_callback)

    #Knowledge Tracing Plugin
    def knowledge_tracing_callback(self, transaction):
        self.logger.debug("KNOWLEDGE_TRACING")
        self.logger.debug(transaction)

    def kt_set_initial_callback(self, transaction):
        self.logger.debug("KT_SET_INITIAL")
        self.logger.debug(transaction)
