import argparse
import logging
import os
import random
import uuid
from datetime import datetime
from time import sleep

from client import Tutor

class ReplayTutor(Tutor):
    def __init__(self, name, logger, run_once=None):
        super().__init__(name, self.main_callback, run_once=run_once)
        self.run_once = run_once
        self.logger = logger
        self.args = json.loads(args[1:-1])
        
    def main_callback(self):
        #TODO: replay logic here
        

        if self.run_once:
            return False
        else:
            return True
    
    def run(self):
        self.connect()
        
        self.start()
        
        self.disconnect()    
    
        
