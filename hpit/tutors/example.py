import argparse
import logging
import os
import random
import uuid
from datetime import datetime
from time import sleep

from hpitclient import Tutor

class ExampleTutor(Tutor):
    def __init__(self, entity_id, api_key, logger=None, run_once=None, args = None):
        super().__init__(entity_id, api_key, self.main_callback)
        self.run_once = run_once
        self.logger = logger
        self.event_names = [
            'test', 'example', 'add_student', 
            'remove_student', 'trace']

    def main_callback(self):
        event = random.choice(self.event_names)

        logger = logging.getLogger(__name__)
        self.send_log_entry("Sending a random event: " + event)
        response = self.send(event, {'test': 1234})
        self.send_log_entry("RECV: " + str(response))

        sleep(1)

        if self.run_once:
            return False
        else:
            return True
