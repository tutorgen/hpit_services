from lib import Plugin

class DataStoragePlugin(Plugin):

    def __init__(self, name, logger):
        super().__init__(name)
        self.logger = logger

        self.subscribe(
            store_data=self.store_data_callback,
            retrieve_data=self.retrieve_data_callback,
            remove_data=self.remove_data_callback)

    def store_data_callback(self, transaction):
        self.logger.debug("STORE_DATA")
        self.logger.debug(transaction)

    def retrieve_data_callback(self, transaction):
        self.logger.debug("RETRIEVE_DATA")
        self.logger.debug(transaction)

    def remove_data_callback(self, transaction):
        self.logger.debug("REMOVE_DATA")
        self.logger.debug(transaction)
