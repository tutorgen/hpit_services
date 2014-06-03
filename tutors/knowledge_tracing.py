import argparse
import logging
import os
import random
import uuid
from datetime import datetime
from time import sleep

from client import Tutor

class KnowledgeTracingTutor(Tutor):
    def __init__(self, name, logger, run_once=None):
        super().__init__(name, self.main_callback, run_once=run_once)
        self.run_once = run_once
        self.logger = logger
        self.skills = ['addition', 'subtraction', 'multiplication', 'division']

    def setup(self):
        for sk in self.skills:
            self.send('kt_set_initial', {
                'skill': sk,
                'probability_known': random.randint(0, 1000) / 1000.0,
                'probability_learned': random.randint(0, 1000) / 1000.0,
                'probability_guess': random.randint(0, 1000) / 1000.0,
                'probability_mistake': random.randint(0, 1000) / 1000.0,
                }, self.initial_response_callback)

    def shutdown(self):
        for sk in self.skills:
            self.send('kt_reset', {
                'skill': sk,
                })

    def main_callback(self):
        for sk in self.skills:
            if 90 < random.randint(0, 100):
                correct = random.randint(0, 100)

                self.send('kt_trace', {
                    'skill': sk,
                    'correct': True if 50 < random.randint(0, 100) else False
                    }, self.trace_response_callback)

        sleep(1)

        return True

    def trace_response_callback(self, response):
        self.logger.debug("RECV: kt_trace response recieved. " + str(response))

    def initial_response_callback(self, response):
        self.logger.debug("RECV: kt_set_initial response recieved. " + str(response))

    def run(self):
        self.connect()
        self.setup()
        self.start()
        self.shutdown()
        self.disconnect()
