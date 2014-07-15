from hpitclient import Plugin

class ExamplePlugin(Plugin):

    def __init__(self, entity_id, api_key, logger, args = None):
        super().__init__(entity_id, api_key)
        self.logger = logger

    def post_connect(self):
        super().post_connect()

        self.subscribe(
            test=self.test_plugin_callback, 
            example=self.example_plugin_callback)

    #Example Plugin
    def test_plugin_callback(self, message):
        self.logger.debug("TEST")
        self.logger.debug(message)

    def example_plugin_callback(self, message):
        self.logger.debug("EXAMPLE")
        self.logger.debug(message)
