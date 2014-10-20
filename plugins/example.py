from hpitclient import Plugin

class ExamplePlugin(Plugin):

    def __init__(self, entity_id, api_key, logger, args = None):
        super().__init__(entity_id, api_key)
        self.logger = logger

    def post_connect(self):
        super().post_connect()

        self.subscribe(
            test=self.test_plugin_callback, 
            example=self.example_plugin_callback,
            kt_trace=self.kt_trace_callback)
        
        #self._post_data("message-auth",{"message_name":"kt_trace","other_entity_id":"01177f8f-c082-4d2d-a9b5-97623cb7bbc9"}) #problem manager

    #Example Plugin
    def test_plugin_callback(self, message):
        self.send_log_entry("TEST")
        self.send_log_entry(message)

    def example_plugin_callback(self, message):
        self.send_log_entry("EXAMPLE")
        self.send_log_entry(message)

    def kt_trace_callback(self,message):
        self.logger.debug("I got a message I shouldn't have!")
