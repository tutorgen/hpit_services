from client import Plugin

#I've decided to use ArrangoDB, which is like MongoDB but with graphs.
#SQLAlchemy doesn't like directed graph relationships and buildinging
#around those limitations will be painful. Arrango looks like it will
#be relatively painless and will allow us to get up and running quickly.

class HintFactoryPlugin(Plugin):

    def __init__(self, entity_id, api_key, logger, args = None):
        super().__init__(entity_id, api_key)
        self.logger = logger

    def post_connect(self):
        super().post_connect()

        self.subscribe(
            hf_init_problem=self.init_problem_callback, 
            hf_push_state=self.push_state_callback,
            hf_hint_exists=self.hint_exists_callback,
            hf_get_hint=self.get_hint_callback)

    #Hint Factory Plugin
    def init_problem_callback(self, message):
        self.logger.debug("INIT PROBLEM")
        self.logger.debug(message)

    def push_state_callback(self, message):
        self.logger.debug("PUSH PROBLEM STATE")
        self.logger.debug(message)

    def hint_exists_callback(self, message):
        self.logger.debug("HINT EXISTS")
        self.logger.debug(message)

    def get_hint_callback(self, message):
        self.logger.debug("GET HINT")
        self.logger.debug(message)
