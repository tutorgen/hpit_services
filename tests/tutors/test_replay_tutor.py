import sure
import unittest
from unittest.mock import *

import logging
import random

import json
import shlex

from pymongo import MongoClient
import datetime

from tutors import ReplayTutor

class TestReplayTutor(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        client = MongoClient()
        client.drop_database("test_replay")

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

        args = {"db_name":"value1","filter":"filter1"}
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
            -       before time equal earliest date (returns earliest record)
            -       after time before later date (returns latest record)
            -       after time after later date (returns nothing)
            -       after time equal later date (returns latest record)

            -       times straddle middle date (returns middle date)
            -       before time after after time (returns nothing)
            - make sure returns false if run_once, otherwise true
        """

        #fill test db with stuff
        client = MongoClient()
      
        client.test_replay.messages.insert({"value":"1","time_created":datetime.datetime(2010,1,1).strftime("%m-%d-%Y %H:%M:%S"),"event":"event1","payload":"payload1"})
        client.test_replay.messages.insert({"value":"2","time_created":datetime.datetime(2018,1,1).strftime("%m-%d-%Y %H:%M:%S"),"event":"event2","payload":"payload2"})
        client.test_replay.messages.insert({"value":"3","time_created":datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S"),"event":"event3","payload":"payload3"})
  
        #before time lower than early date (returns nothing)
        args = {"db_name":"test_replay", "filter":{},"beforeTime":datetime.datetime(2009,1,1).strftime("%m-%d-%Y %H:%M:%S")}
        args_string = shlex.quote(json.dumps(args))
        r = ReplayTutor("1234","1234",None,None,args_string)
        r.send = MagicMock()
        r.main_callback()
        r.send.call_count.should.equal(0)
        
        #before time after earliest date (returns earliest record)
        args = {"db_name":"test_replay", "filter":{},"beforeTime":datetime.datetime(2011,1,1).strftime("%m-%d-%Y %H:%M:%S")}
        args_string = shlex.quote(json.dumps(args))
        r = ReplayTutor("1234","1234",None,None,args_string)
        r.send = MagicMock()
        r.main_callback()
        r.send.call_count.should.equal(1)
        
        #before time equals earliest date (returns earliest record)
        args = {"db_name":"test_replay", "filter":{},"beforeTime":datetime.datetime(2010,1,1).strftime("%m-%d-%Y %H:%M:%S")}
        args_string = shlex.quote(json.dumps(args))
        r = ReplayTutor("1234","1234",None,None,args_string)
        r.send = MagicMock()
        r.main_callback()
        r.send.call_count.should.equal(1)
        
        #after time before later date (returns latest record)
        args = {"db_name":"test_replay", "filter":{},"afterTime":datetime.datetime(2017,1,1).strftime("%m-%d-%Y %H:%M:%S")}
        args_string = shlex.quote(json.dumps(args))
        r = ReplayTutor("1234","1234",None,None,args_string)
        r.send = MagicMock()
        r.main_callback()
        r.send.call_count.should.equal(1)
        
        #after time after later date (returns nothing)
        args = {"db_name":"test_replay", "filter":{},"afterTime":datetime.datetime(2019,1,1).strftime("%m-%d-%Y %H:%M:%S")}
        args_string = shlex.quote(json.dumps(args))
        r = ReplayTutor("1234","1234",None,None,args_string)
        r.send = MagicMock()
        r.main_callback()
        r.send.call_count.should.equal(0)
        
        #after time equal later date (returns last record)
        args = {"db_name":"test_replay", "filter":{},"afterTime":datetime.datetime(2018,1,1).strftime("%m-%d-%Y %H:%M:%S")}
        args_string = shlex.quote(json.dumps(args))
        r = ReplayTutor("1234","1234",None,None,args_string)
        r.send = MagicMock()
        r.main_callback()
        r.send.call_count.should.equal(1)

        #times straddle middle date (returns middle date)
        args = {"db_name":"test_replay", "filter":{},"afterTime":datetime.datetime(2012,1,1).strftime("%m-%d-%Y %H:%M:%S"),"beforeTime":datetime.datetime(2016,1,1).strftime("%m-%d-%Y %H:%M:%S")}
        args_string = shlex.quote(json.dumps(args))
        r = ReplayTutor("1234","1234",None,None,args_string)
        r.send = MagicMock()
        r.main_callback()
        r.send.call_count.should.equal(1)
        
        #before time after after time (returns nothing)
        args = {"db_name":"test_replay", "filter":{},"beforeTime":datetime.datetime(2012,1,1).strftime("%m-%d-%Y %H:%M:%S"),"afterTime":datetime.datetime(2016,1,1).strftime("%m-%d-%Y %H:%M:%S")}
        args_string = shlex.quote(json.dumps(args))
        r = ReplayTutor("1234","1234",None,None,args_string)
        r.send = MagicMock()
        r.main_callback()
        r.send.call_count.should.equal(0)
        
        #testing filter
        args = {"db_name":"test_replay", "filter":{"value":"1"}}
        args_string = shlex.quote(json.dumps(args))
        r = ReplayTutor("1234","1234",None,None,args_string)
        r.send = MagicMock()
        r.main_callback()
        r.send.call_count.should.equal(1)
        
        #run_once true
        args = {"db_name":"test_replay", "filter":{}}
        args_string = shlex.quote(json.dumps(args))
        r = ReplayTutor("1234","1234",None,True,args_string)
        r.send = MagicMock()
        r.main_callback().should.equal(False)
        
        #run_once none
        args = {"db_name":"test_replay", "filter":{}}
        args_string = shlex.quote(json.dumps(args))
        r = ReplayTutor("1234","1234",None,None,args_string)
        r.send = MagicMock()
        r.main_callback().should.equal(True)


