from hpitclient import Plugin

from datetime import datetime

from pymongo import MongoClient
from bson.objectid import ObjectId
import bson

from hpit.management.settings_manager import SettingsManager
settings = SettingsManager.get_plugin_settings()

class ProblemManagementPlugin(Plugin):

    def __init__(self, entity_id, api_key, logger,args = None):
        super().__init__(entity_id, api_key)
        self.logger = logger
        self.mongo = MongoClient(settings.MONGODB_URI)
        self.db = self.mongo.hpit.hpit_problems
        self.step_db = self.mongo.hpit.hpit_steps
        self.worked_db = self.mongo.hpit.hpit_problems_worked
        
        self.problem_fields = ["problem_name","problem_text"]

    def post_connect(self):
        super().post_connect()
        
        self.subscribe(
            add_problem=self.add_problem_callback,
            remove_problem=self.remove_problem_callback,
            get_problem=self.get_problem_callback,
            edit_problem=self.edit_problem_callback,
            list_problems=self.list_problems_callback,
            clone_problem=self.clone_problem_callback,
            add_problem_worked=self.add_problem_worked_callback,
            get_problems_worked=self.get_problems_worked_callback,
            add_step=self.add_step_callback,
            remove_step=self.remove_step_callback,
            get_step=self.get_step_callback,
            get_problem_steps=self.get_problem_steps_callback,
            get_student_model_fragment=self.get_student_model_fragment_callback)

    #Problem Management Plugin
    def add_problem_callback(self, message):
        sender_entity_id = message['sender_entity_id']
        
        try:
            problem_name = message['problem_name']
            problem_text = message['problem_text']
        except KeyError:
            self.send_response(message["message_id"], {
                    "error": "Add problem requires 'problem_name' and 'problem_text'",
                    "success":False,
            })
            return
        
        problem = self.db.find_one({
            'problem_name': problem_name,
            'problem_text': problem_text,
            })

        if not problem:
            problem_id = self.db.insert({
                'edit_allowed_id': sender_entity_id,
                'problem_name': problem_name,
                'problem_text': problem_text,
                'date_created': datetime.now(),
            })

            self.send_response(message['message_id'], {
                'problem_name': problem_name,
                'problem_text': problem_text,
                'success': True,
                'problem_id':str(problem_id)
            })
        
        else:
            self.send_response(message['message_id'], {
                'error': "This problem already exists.  Try cloning the 'problem_id' sent in this response.",
                'problem_id': str(problem["_id"]),
                "success":False
            })
        
    def remove_problem_callback(self, message):
        sender_entity_id = message['sender_entity_id']
        
        try:
            problem_id = str(message['problem_id'])
        except KeyError:
            self.send_response(message["message_id"], {
                    "error":"remove_problem requires 'problem_id'",
                    "success":False,
            })
            return
            
        problem = self.db.find_one({
            'edit_allowed_id': sender_entity_id,
            '_id': ObjectId(problem_id),
        })

        if problem:
            self.db.remove({
                'edit_allowed_id': sender_entity_id,
                '_id': ObjectId(problem_id),
            })

            self.send_response(message['message_id'], {
                'exists': True,
                'success': True,
            })
        else:
            self.send_response(message['message_id'], {
                "error": "Could not delete problem; it does not exist",
                'problem_id': str(problem_id),
                'exists': False,
                'success': False
            })

    def get_problem_callback(self, message):
        try:
            problem_id = str(message['problem_id'])
        except KeyError:
            self.send_response(message["message_id"], {
                    "error":"get_problem requires a 'problem_id'",
                    "success":False,
            })
            return
            
        problem = self.db.find_one({
            '_id': ObjectId(problem_id),
        })

        if not problem:
            self.send_response(message['message_id'], {
                'error': "Error:  problem with id" + str(problem_id) + " does not exist.",
                'exists': False,
                'success': False
            })
            return
        else:
            self.send_response(message['message_id'], {
                'problem_id':str(problem_id),
                'problem_name': problem["problem_name"],
                'problem_text': problem['problem_text'],
                'date_created': problem["date_created"],
                'edit_allowed_id' : problem["edit_allowed_id"],
                'exists': True,
                'success': True
            })
    
    def edit_problem_callback(self,message):
        try:
            problem_id = str(message["problem_id"])
            fields = message["fields"]
        except KeyError:
            self.send_response(message["message_id"], {
                    "error":"edit_problem requires 'problem_id' and 'fields'",
                    "success":False
            })
            return
                    
        problem = self.db.find_one({
                "_id" : ObjectId(problem_id),
                "edit_allowed_id" : message["sender_entity_id"],
        })
        
        if not problem:
            self.send_response(message["message_id"], {
                "error": "Error: either problem with provided id doesn't exist, or you do not have permission to edit.",
                "success":False,
            })
            return
        else:
            if not isinstance(fields,dict):
                self.send_response(message["message_id"],{
                        "error":"Fields needs to be a dict.",
                        "success":False
                })
                return 
                
            update_dict = {}
            for f in self.problem_fields:
                if f in fields:
                    update_dict[f] = fields[f]
                    problem[f] = fields[f]
                    
            if len(update_dict) > 0:
                self.db.update({"_id":problem["_id"]},{"$set":update_dict})
                
            self.send_response(message['message_id'], {
                'problem_name': problem["problem_name"],
                'problem_text': problem['problem_text'],
                'date_created': problem["date_created"],
                'edit_allowed_id' : problem["edit_allowed_id"],
                'success': True
            })

    def list_problems_callback(self, message):
        problems = self.db.find({})
        problems = [p for p in problems]
        self.send_response(message['message_id'], {
            'problems': problems,
            'success': True
        })
        
    def clone_problem_callback(self,message):
        entity_id = message["sender_entity_id"]
        
        try:
            problem_id = str(message["problem_id"])
        except KeyError:
            self.send_response(message["message_id"],{
                    "error": "clone_problem requires a 'problem_id'.",
                    "success":False,
            })
            return
        
        problem = self.db.find_one({
                "_id":ObjectId(problem_id)
        })
        
        if not problem:
            self.send_response(message["message_id"], {
                    "error": "Problem with id " + str(problem_id) + " does not exist.",
                    "success":False
            })
            return
                   
        
        new_problem_id = self.db.insert({
                'edit_allowed_id': entity_id,
                'problem_name': problem["problem_name"],
                'problem_text': problem["problem_text"],
                'date_created': datetime.now(),
            })
        
        steps = self.step_db.find({"problem_id":problem["_id"]})
        step_ids = []
        for step in steps:
            new_step_id = self.step_db.insert({
                    "problem_id":new_problem_id,
                    "step_text": step["step_text"],
                    "allowed_edit_id": entity_id,
                    "date_created":datetime.now(),
            })
            step_ids.append(str(new_step_id))
        
        self.send_response(message["message_id"], {
            "problem_id":str(new_problem_id),
            "step_ids":step_ids,
            "success":True
        })
        
    def add_problem_worked_callback(self,message):
       
        try:
            problem_id = ObjectId(str(message["problem_id"]))
            student_id = str(message["student_id"])
        except KeyError:
            self.send_response(message["message_id"],{
                    "error" : "add_problem_worked requires a 'problem_id' and 'student_id'",
                    "success":False
            })
            return
        except bson.errors.InvalidId:
            self.send_response(message["message_id"],{
                    "error" : "The supplied 'problem_id' is not a valid ObjectId.",
                    "success":False
            })
            return
        
        problem = self.db.find_one({"_id":ObjectId(str(problem_id))})
        if not problem:
            self.send_response(message["message_id"],{
                    "error" : "Problem with ID "+str(problem_id) + " does not exist.",
                    "success":False
            })
            return
            
        self.worked_db.insert({"student_id":student_id,"problem_id":problem_id})
        self.send_response(message["message_id"],{
                    "success":True
            })
        
    def get_problems_worked_callback(self,message):
        try:
            student_id = message["student_id"]
        except KeyError:
            self.send_response(message["message_id"],{
                    "error" : "add_problem_worked requires a 'student_id'",
                    "success":False
            })
            return
            
        
        problems_worked = self.worked_db.find({"student_id":student_id})
        problems = [p for p in problems_worked]
        
        self.send_response(message["message_id"],{
               "success":True,
               "problems_worked": problems,
        })
        
            
        
            
        
    def add_step_callback(self,message):
        entity_id = message["sender_entity_id"]
        
        try:
            problem_id = str(message["problem_id"])
            step_text = message["step_text"]
        except KeyError:
            self.send_response(message["message_id"],{
                    "error": "add_step requires a 'problem_id' and 'step_text'",
                    "success":False
            })
            return
            
        problem = self.db.find_one({
                "_id":ObjectId(problem_id),
                "allowed_edit_id":entity_id
        })
        
        if not problem:
            self.send_response(message["message_id"], {
                "error": "Error: either problem with provided id doesn't exist, or you do not have permission to edit.",
                "success":False,
            })
            return
        else:
            step_id = self.step_db.insert({
                    "problem_id":problem["_id"],
                    "step_text": step_text,
                    "allowed_edit_id": entity_id,
                    "date_created": datetime.now()
            })
            self.send_response(message["message_id"], {
                "step_id": str(step_id),
                "success": True,
            })
      
    def remove_step_callback(self,message):
        entity_id = message["sender_entity_id"]
        
        try:
            step_id = str(message["step_id"])
        except KeyError:
            self.send_response(message["message_id"], {
                    "error": "remove_step requires 'step_id'",
                    "success":False
            })
            return
            
        step = self.step_db.find_one({
                "_id":ObjectId(step_id),
                "allowed_edit_id": entity_id,
        })
        if not step:
            self.send_response(message["message_id"], {
                    "error": "Either the step doesn't exist or you don't have permission to remove it.",
                    "success":False
            })
            return
        else:
            self.step_db.remove({"_id":ObjectId(step_id)})
            self.send_response(message["message_id"], {
                    "success":True,
                    "exists":True,
            })
          
    def get_step_callback(self,message):
        entity_id = message["sender_entity_id"]
        
        try:
            step_id = message["step_id"]
        except KeyError:
            self.send_response(message["message_id"],{
                    "error": "get_step requires a 'step_id'",
                    "success":False,
            })
            return
        
        step = self.step_db.find_one({"_id":ObjectId(step_id)})
        if not step:
            self.send_response(message["message_id"],{
                    "error": "Step does not exist.",
                    "success":False
            })
            return
        else:
            self.send_response(message["message_id"],{
                    "step_id": str(step["_id"]),
                    "step_text": step["step_text"],
                    "date_created": step["date_created"],
                    "allowed_edit_id": step["allowed_edit_id"],
                    "success":True,
            })
            return
          
    def get_problem_steps_callback(self,message):
        entity_id = message["sender_entity_id"]
        
        try:
            problem_id = str(message["problem_id"])
        except KeyError:
            self.send_response(message["message_id"], {
                "error":"get_problem_callback requires a 'problem_id'",   
                "success":False
            })
            return
            
        problem = self.db.find_one({"_id":ObjectId(problem_id)})
        if not problem:
            self.send_response(message["message_id"], {
                "error":"Problem with ID " + str(problem_id) + " does not exist.",
                "success":False
            })
            return
        else:
            steps = self.step_db.find({"problem_id":ObjectId(problem_id)})
            return_steps = []
            for step in steps:
                return_steps.append({
                        "step_id" : str(step["_id"]),
                        "step_text": step["step_text"],
                        "date_created": step["date_created"],
                        "allowed_edit_id": step["allowed_edit_id"],
                })
            self.send_response(message["message_id"], {
                "steps": return_steps,
                "problem_id": str(problem_id),
                "success":True,
            })
            
    def get_student_model_fragment_callback(self,message):      
        if self.logger:
            self.send_log_entry("GET STUDENT MODEL FRAGMENT" + str(message))
            
        try:
            student_id = message["student_id"]
        except KeyError:
            self.send_response(message["message_id"],{
                "error":"problem_managment get_student_model_fragment requires 'student_id'"       
            })
            return
        
        problems_worked = self.worked_db.find({"student_id":student_id})
        problems = [p for p in problems_worked]
        
        self.send_response(message["message_id"],{
               "name":"problem_management",
               "fragment": problems,
        })
        
            
             
                        
