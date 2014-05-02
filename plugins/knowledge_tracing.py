from lib import Plugin

class KnowledgeTracingPlugin(Plugin):

    def __init__(self, name, logger):
        super().__init__(name)
        self.logger = logger

        self.subscribe(
            kt_set_initial=self.kt_set_initial_callback,
            knowledge_tracing=self.knowledge_tracing_callback)

    #Knowledge Tracing Plugin
    def knowledge_tracing_callback(self, transaction):
        self.logger.debug("KNOWLEDGE_TRACING")
        self.logger.debug(transaction)

    def kt_set_initial_callback(self, transaction):
        self.logger.debug("KT_SET_INITIAL")
        self.logger.debug(transaction)
