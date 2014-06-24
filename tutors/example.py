import argparse
import logging
import os
import random
import uuid
from datetime import datetime
from time import sleep

from client import Tutor

class ExampleTutor(Tutor):
    def __init__(self, entity_id, api_key, logger=None, run_once=None, args = None):
        super().__init__(entity_id, api_key, self.main_callback)
        self.run_once = run_once
        self.logger = logger
        self.event_names = [
            'test', 'example', 'add_student', 
            'remove_student', 'trace']

    def setup(self):
        pass

    def shutdown(self):
        pass

    def main_callback(self):
        event = random.choice(self.event_names)

        logger = logging.getLogger(__name__)
        logger.debug("Sending a random event: " + event)
        response = self.send(event, {'test': 1234})
        logger.debug("RECV: " + str(response))

        sleep(1)

        if self.run_once:
            return False
        else:
            return True

    def run(self):
        self.connect()
        self.setup()
        self.start()
        self.shutdown()
        self.disconnnect()
