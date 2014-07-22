import sure
import unittest
import httpretty
from unittest.mock import *

import logging
from hpitclient.settings import HpitClientSettings

HPIT_URL_ROOT = HpitClientSettings.settings().HPIT_URL_ROOT
import random

import json
import shlex

from tutors import ReplayTutor

class TestReplayTutor(unittest.TestCase):
    
    
    def test_constructor(self):
        """
        ReplayTutor.__init__() Test plan:
            - make sure shlex passed args is parsed properly
            - exception raised if no args
            - exception raised if no db_name
            - make sure once, logger set
        """
        ReplayTutor.__init__.when.called_with("1234","1234",None,None,None).should.throw(Exception)
        
        ReplayTutor.__init__.when.called_with("1234","1234",None,None,shlex.quote(json.dumps({"arg":"val"}))).should.throw(Exception)
        
        args = {"db_name":"value1"}
        args_string = shlex.quote(json.dumps(args))
        
        r = ReplayTutor("1234","1234",None,None,args_string)
        r.logger.should.equal(None)
        r.run_once.should.equal(None)
        r.args["db_name"].should.equal("value1")
        
    def test_main_callback(self):
        """
        ReplayTutor.main_callback() Test plan:
            - add some records to a test Mongo database
            -       before current time, at current time, after current time
            -       filter true, filter false
            - construct args around boundaries
            -       before time lower than early date (returns nothing)
            -       before time after earliest date (returns earliest record)
            -       after time before later date (returns latest record)
            -       after time after later date (returns nothing)
            -       times straddle middle date (returns middle date)
            -       before time after after time (returns nothing)
            - make sure returns false if run_once, otherwise true
        """
        


