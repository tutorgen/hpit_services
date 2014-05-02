from client import Plugin

class ExamplePlugin(Plugin):

    def __init__(self, name, logger):
        super().__init__(name)
        self.logger = logger

        self.subscribe(
            test=self.test_plugin_callback, 
            example=self.example_plugin_callback)

    #Example Plugin
    def test_plugin_callback(self, transaction):
        self.logger.debug("TEST")
        self.logger.debug(transaction)

    def example_plugin_callback(self, transaction):
        self.logger.debug("EXAMPLE")
        self.logger.debug(transaction)
