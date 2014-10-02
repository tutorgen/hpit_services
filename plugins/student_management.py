from hpitclient import Plugin

from pymongo import MongoClient
from bson.objectid import ObjectId

from threading import Timer

import time

from environment.settings_manager import SettingsManager
settings = SettingsManager.get_plugin_settings()

class StudentManagementPlugin(Plugin):

    def __init__(self, entity_id, api_key, logger, args = None):
        super().__init__(entity_id, api_key)
        self.logger = logger
        self.mongo = MongoClient(settings.MONGODB_URI)
        self.db = self.mongo.hpit.hpit_students
        
        self.TIMEOUT = 15
        self.student_model_fragment_names = ["knowledge_tracing","problem_management"]
        self.student_models = {}
        self.timeout_threads = {}

    def post_connect(self):
        super().post_connect()
        
        self.subscribe(
            add_student=self.add_student_callback,
            get_student=self.get_student_callback,
            set_attribute=self.set_attribute_callback,
            get_attribute=self.get_attribute_callback,
            get_student_model = self.get_student_model_callback)

    #Student Management Plugin
    def add_student_callback(self, message):
        if self.logger:
            self.logger.debug("ADD_STUDENT")
            self.logger.debug(message)
        
        try:
            attributes = message["attributes"]
        except KeyError:
            attributes = {}
            
        student_id = self.db.insert({"attributes":attributes})
        self.send_response(message["message_id"],{"student_id":str(student_id),"attributes":attributes})
        
    def get_student_callback(self, message):
        if self.logger:
            self.logger.debug("GET_STUDENT")
            self.logger.debug(message)
        
        try:
            student_id = message["student_id"]
        except:
            self.send_response(message["message_id"],{"error":"Must provide a 'student_id' to get a student"})
            return
        
        return_student = self.db.find_one({"_id":ObjectId(student_id)})
        if not return_student:
            self.send_response(message["message_id"],{"error":"Student with id " + str(student_id) + " not found."})
        else:
            self.send_response(message["message_id"],{"student_id":str(return_student["_id"]),"attributes":return_student["attributes"]})
            
    def set_attribute_callback(self, message):
        if self.logger:
            self.logger.debug("SET_ATTRIBUTE")
            self.logger.debug(message)
        
        try:
            student_id = message["student_id"]
            attribute_name = message["attribute_name"]
            attribute_value = message["attribute_value"]
        except KeyError:
            self.send_response(message["message_id"],{"error":"Must provide a 'student_id', 'attribute_name' and 'attribute_value'"})
            return
            
        update = self.db.update({'_id':ObjectId(str(student_id))},{'$set':{'attributes.'+str(attribute_name): str(attribute_value)}},upsert=False, multi=False)
        if not update["updatedExisting"]:
            self.send_response(message["message_id"],{"error":"Student with id " + str(student_id) + " not found."})
        else:
            record = self.db.find_one({"_id":ObjectId(str(student_id))})
            self.send_response(message["message_id"],{"student_id":str(record["_id"]),"attributes":record["attributes"]})
               
    def get_attribute_callback(self, message):
        if self.logger:
            self.logger.debug("GET_ATTRIBUTE")
            self.logger.debug(message)
        
        try:
            student_id = message["student_id"]
            attribute_name = message["attribute_name"]
        except KeyError:
            self.send_response(message["message_id"],{"error":"Must provide a 'student_id' and 'attribute_name'"})
            return 
            
        student = self.db.find_one({'_id':ObjectId(str(student_id))})
        if not student:
            self.send_response(message["message_id"],{"error":"Student with id " + str(student_id) + " not found."})
            return
        else:
            try:
                attr = student["attributes"][attribute_name]
            except KeyError:
                attr = ""
            self.send_response(message["message_id"],{"student_id":str(student["_id"]),attribute_name:attr})

    def get_student_model_callback(self,message):
        if self.logger:
            self.logger.debug("GET_STUDENT_MODEL")
            self.logger.debug(message)
            self.send_log_entry("GET_STUDENT_MODEL")
            self.send_log_entry(message)
            
            
        try:
            student_id = message["student_id"]
        except KeyError:
            self.send_response(message["message_id"],{
                "error":"get_student_model requires a 'student_id'",         
            })
            return
        
        self.student_models[message["message_id"]] = {}
        self.timeout_threads[message["message_id"]] = Timer(self.TIMEOUT, self.kill_timeout, [message])
        self.timeout_threads[message["message_id"]].start()

        self.send("get_student_model_fragment",{
                "update":True,
                "student_id" : message["student_id"],
        },self.get_populate_student_model_callback_function(message))
        
    
    def get_populate_student_model_callback_function(self,message):
        def populate_student_model(response):
            
            #check if values exist
            try:
                name = response["name"]
                fragment = response["fragment"]
            except KeyError:
                return
            
            #check if name is valid
            if response["name"] not in self.student_model_fragment_names:
                return

            #fill student model
            try:
                self.student_models[str(message["message_id"])][response["name"]] = response["fragment"]
                if self.logger:
                    self.logger.debug("GOT FRAGMENT " + str(response["fragment"]))
                    self.send_log_entry("GOT FRAGMENT " + str(response["fragment"]))
                    
            except KeyError:
                return
            
            #check to see if student model complete
            for name in self.student_model_fragment_names:
                try:
                    if self.student_models[str(message["message_id"])][name] == None:
                        break
                except KeyError:
                    break
            else:
                #student model complete, send response (unless timed out)
                if message["message_id"] in self.timeout_threads:
                    self.send_response(message["message_id"],{
                        "student_model" : self.student_models[message["message_id"]],       
                    })
                    self.timeout_threads[message["message_id"]].cancel()
                    del self.timeout_threads[message["message_id"]]
                    del self.student_models[message["message_id"]]
                    return
 
        return populate_student_model
        
    def kill_timeout(self,message):
        if self.logger:
            self.logger.debug("TIMEOUT " + str(message))
            self.send_log_entry("TIMEOUT " + str(message))
        try:
            self.send_response(message["message_id"],{
                "error":"Get student model timed out. Here is a partial student model.",
                "student_model":self.student_models[str(message["message_id"])]
            })
        except KeyError:
            self.send_response(message["message_id"],{
                "error":"Get student model timed out. Here is a partial student model.",
                "student_model":{},
            })
        
        try:
            del self.timeout_threads[str(message["message_id"])]
            del self.student_models[str(message["message_id"])]
        except KeyError:
            pass
        
