from hpitclient import Plugin

from datetime import datetime

from pymongo import MongoClient
from bson.objectid import ObjectId

class ProblemManagementPlugin(Plugin):

    def __init__(self, entity_id, api_key, logger,args = None):
        super().__init__(entity_id, api_key)
        self.logger = logger
        self.mongo = MongoClient('mongodb://localhost:27017/')
        self.db = self.mongo.hpit.hpit_problems
        self.step_db = self.mongo.hpit.hpit_steps
        
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
            add_step=self.add_step_callback,
            remove_step=self.remove_step_callback,
            get_step=self.get_step_callback,
            get_problem_steps=self.get_problem_steps_callback)

    #Problem Management Plugin
    def add_problem_callback(self, message):
        sender_entity_id = message['sender_entity_id']
        
        try:
            problem_name = message['problem_name']
            problem_text = message['problem_text']
        except KeyError:
            self.send_response(messsage["message_id"], {
                    "error": "Add problem requires 'problem_name' and 'problem_text'",
            })
        
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
            })
        

    def remove_problem_callback(self, message):
        sender_entity_id = message['sender_entity_id']
        problem_id = message['problem_id']

        problem = self.db.find_one({
            'edit_allowed_id': sender_entity_id,
            'problem_name': problem_id,
        })

        if problem:
            self.db.remove({
                'edit_allowed_id': sender_entity_id,
                '_id': ObjectID(problem_id),
            })

            self.send_response(message['message_id'], {
                'exists': True,
                'success': True,
            })
        else:
            self.send_response(message['message_id'], {
                "error": "Could not delete problem; it does not exist",
                'problem_id': problem_id,
                'exists': False,
                'success': False
            })


    def get_problem_callback(self, message):
        problem_id = message['problem_id']

        problem = self.db.find_one({
            '_id': ObjectID(problem_id),
        })

        if not problem:
            self.send_response(message['message_id'], {
                'error': "Error:  problem with id" + problem_id + " does not exist.",
                'exists': False,
                'success': False
            })
            return
        else:
            self.send_response(message['message_id'], {
                'problem_id':problem_id,
                'problem_name': problem["problem_name"],
                'problem_text': problem['problem_text'],
                'date_created': problem["date_created"],
                'edit_allowed_id' : problem["edit_allowed_id"],
                'exists': True,
                'success': True
            })
    
    def edit_problem_callback(self,message):
        fields = message["fields"]
        problem_id = message["problem_id"]
        
        problem = self.db.find_one({
                "_id" : ObjectID(problem_id),
                "edit_allowed_id" : message["sender_entity_id"],
        })
        
        if not problem:
            self.send_response(message["message_id"], {
                "error": "Error: either problem with provided id doesn't exist, or you do not have permission to edit.",
                "success":'false',
            })
            return
        else:
            update_dict = {}
            for f in self.problem_fields:
                if f in fields:
                    update_dict[f] = fields[f]
                    problem[f] = fields[f]
            
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
            problem_id = message["problem_id"]
        except KeyError:
            self.send_response(message["message_id"],{
                    "error": "clone_problem requires a 'problem_id'."
            })
            return
        
        problem = self.db.find_one({
                "_id":ObjectID(problem_id)
        })
        
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
                    "problem_id":problem["_id"],
                    "step_text": step["step_text"],
                    "allowed_edit_id": entity_id,
                    "date_created":datetime.now(),
            })
            step_ids.append(str(new_step_id))
        
        self.send_response(message["message_id"], {
            "problem_id":new_problem_id,
            "step_ids":step_ids,
            "success":True
        })
        
        
    def add_step_callback(self,message):
        entity_id = message["sender_entity_id"]
        
        try:
            problem_id = message["problem_id"]
            step_text = message["step_text"]
        except KeyError:
            self.send_response(message["message_id"],{
                    "error": "add_step requires a 'problem_id' and 'step_text'"
            })
            return
            
        problem = self.db.find_one({
                "_id":ObjectID(problem_id),
                "allowed_edit_id":entity_id
        })
        
        if not problem:
            self.send_response(message["message_id"], {
                "error": "Error: either problem with provided id doesn't exist, or you do not have permission to edit.",
                "success":'false',
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
            step_id = message["step_id"]
        except KeyError:
            self.send_response(message["message_id"], {
                    "error": "remove_step requires 'step_id'",
            })
            return
            
        step = self.step_db.find_one({
                "_id":ObjectID(step_id),
                "allowed_access_id": entity_id,
        })
        if not step:
            self.send_response(message["message_id"], {
                    "error": "Either the step doesn't exist or you don't have permission to remove it.",
            })
            return
        else:
            self.step_db.remove({"_id":ObjectID(step_id)})
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
                    "error": "get_step requires a 'step_id'"
            })
            return
        
        step = self.step_db.find_one({"_id":ObjectID(step_id)})
        if not step:
            self.send_response(message["message_id"],{
                    "error": "Step does not exist."
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
            problem_id = message["problem_id"]
        except KeyError:
            self.send_response(message["message_id"], {
                "error":"get_problem_callback requires a 'problem_id'",      
            })
            return
            
        problem = self.db.find_one({"_id":ObjectID(problem_id)})
        if not problem:
            self.send_response(message["message_id"], {
                "error":"Problem with ID " + str(problem_id) + " does not exist.",      
            })
            return
        else:
            steps = self.steps_db.find({"problem_id":ObjectID(problem_id)})
            return_steps = []
            for step in return_steps:
                return_steps.append({
                        "step_id" : str(step["_id"]),
                        "step_text": step["step_text"],
                        "date_created": step["date_created"],
                        "allowed_edit_id": step["allowed_edit_id"],
                })
            self.send_response(message["message_id"], {
                "steps": return_steps,
                "problem_id": problem_id,
                "success":True,
            })
            
                        
