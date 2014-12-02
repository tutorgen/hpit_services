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

        self.db = self.mongo[settings.MONGO_DBNAME].hpit_problems
        self.step_db = self.mongo[settings.MONGO_DBNAME].hpit_steps
        self.transaction_db = self.mongo[settings.MONGO_DBNAME].hpit_transactions
        self.worked_db = self.mongo[settings.MONGO_DBNAME].hpit_problems_worked
        
        self.problem_fields = ["problem_name","problem_text"]
        
        self.shared_messages = self.get_shared_messages(args)
        if not self.shared_messages:
            raise Exception("Failed to initilize; invalid shared_messages")

    def post_connect(self):
        super().post_connect()
        
        self.subscribe({
            "tutorgen.add_problem":self.add_problem_callback,
            "tutorgen.remove_problem":self.remove_problem_callback,
            "tutorgen.get_problem":self.get_problem_callback,
            "tutorgen.edit_problem":self.edit_problem_callback,
            "tutorgen.list_problems":self.list_problems_callback,
            "tutorgen.clone_problem":self.clone_problem_callback,
            "tutorgen.add_problem_worked":self.add_problem_worked_callback,
            "tutorgen.get_problems_worked":self.get_problems_worked_callback,
            "tutorgen.add_step":self.add_step_callback,
            "tutorgen.remove_step":self.remove_step_callback,
            "tutorgen.get_step":self.get_step_callback,
            "tutorgen.get_problem_steps":self.get_problem_steps_callback,
            "get_student_model_fragment":self.get_student_model_fragment_callback})
        
        self.register_transaction_callback(self.transaction_callback_method)
        
        #temporary POC code
        #response = self._get_data("message-owner/get_student_model_fragment")
        #if response["owner"] == self.entity_id:
        #    self._post_data("message-auth",{"message_name":"get_student_model_fragment","other_entity_id":"360798c9-2598-4468-a624-d60f6d4b9f4d"}) #knowledge tracing
        #self._post_data("share-message",{"message_name":"get_student_model_fragment","other_entity_ids":["360798c9-2598-4468-a624-d60f6d4b9f4d"]}) #knowledge tracing
        
        for k,v in self.shared_messages.items():
            self._post_data("share-message",{"message_name":k,"other_entity_ids":self.shared_messages[k]})
        
        
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
            "edit_allowed_id":message["sender_entity_id"],
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
            problem_id = ObjectId(str(message["problem_id"]))
        except KeyError:
            self.send_response(message["message_id"],{
                    "error": "clone_problem requires a 'problem_id'.",
                    "success":False,
            })
            return
        except bson.errors.InvalidId:
            self.send_response(message["message_id"],{
                    "error" : "The supplied 'problem_id' is not a valid ObjectId.",
                    "success":False
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
        
        steps = self.step_db.find({"problem_id":problem["_id"],"edit_allowed_id":problem["edit_allowed_id"]})
        
        step_ids = []
        transaction_ids = []
        for step in steps:
            new_step_id = self.step_db.insert({
                    "problem_id":new_problem_id,
                    "step_text": step["step_text"],
                    "edit_allowed_id": entity_id,
                    "date_created":datetime.now(),
                    "skill_ids":step["skill_ids"],
                    "skill_names":step["skill_names"],
            })
            step_ids.append(str(new_step_id))
        
            transactions = self.transaction_db.find({"step_id":step["_id"],"edit_allowed_id":problem["edit_allowed_id"]})
            
            for transaction in transactions:
                new_transaction_id = self.transaction_db.insert({
                    "step_id":new_step_id,
                    "transaction_text":transaction["transaction_text"],
                    "edit_allowed_id":entity_id,
                    "date_created":datetime.now(),
                    "skill_ids":transaction["skill_ids"],
                    "skill_names":transaction["skill_names"],
                })
                transaction_ids.append(str(new_transaction_id))
        
        self.send_response(message["message_id"], {
            "problem_id":str(new_problem_id),
            "step_ids":step_ids,
            "transaction_ids":transaction_ids,
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
            student_id = str(message["student_id"])
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
            problem_id = ObjectId(str(message["problem_id"]))
            step_text = message["step_text"]
        except KeyError:
            self.send_response(message["message_id"],{
                    "error": "add_step requires a 'problem_id' and 'step_text'",
                    "success":False
            })
            return
        except bson.errors.InvalidId:
            self.send_response(message["message_id"],{
                    "error" : "The supplied 'problem_id' is not a valid ObjectId.",
                    "success":False
            })
            return
        
        try:
            if "skill_ids" not in message:
                skill_ids = {}
            else:
                skill_ids = dict(message["skill_ids"])
        except TypeError:
            self.send_response(message["message_id"],{
                    "error" : "The supplied 'skill_ids' is not valid; must be dict.",
                    "success":False
            })
            return
        
        try:
            if "skill_names" not in message:
                skill_names = {}
            else: 
                skill_names = dict(message["skill_names"])
        except TypeError:
            self.send_response(message["message_id"],{
                    "error" : "The supplied 'skill_names' is not valid; must be dict.",
                    "success":False
            })
            return
            
        problem = self.db.find_one({
                "_id":ObjectId(problem_id),
                "edit_allowed_id":entity_id
        })
        
        if not problem:
            self.send_response(message["message_id"], {
                "error": "Error: either problem with provided id doesn't exist, or you do not have permission to edit.",
                "success":False,
            })
            return
        else:
            step = self.step_db.find_one({"problem_id":problem["_id"],"step_text":step_text,"edit_allowed_id":message["sender_entity_id"]})
            if not step:
                step_id = self.step_db.insert({
                        "problem_id":problem["_id"],
                        "step_text": step_text,
                        "edit_allowed_id": entity_id,
                        "date_created": datetime.now(),
                        "skill_ids": skill_ids,
                        "skill_names": skill_names,
                })
            else:
                step_id = step["_id"]
                
            self.send_response(message["message_id"], {
                "step_id": str(step_id),
                "success": True,
            })
      
    def remove_step_callback(self,message):
        entity_id = message["sender_entity_id"]
        
        try:
            step_id = ObjectId(str(message["step_id"]))
        except KeyError:
            self.send_response(message["message_id"], {
                    "error": "remove_step requires 'step_id'",
                    "success":False
            })
            return
        except bson.errors.InvalidId:
            self.send_response(message["message_id"],{
                    "error" : "The supplied 'step_id' is not a valid ObjectId.",
                    "success":False
            })
            return
            
        step = self.step_db.find_one({
                "_id":ObjectId(step_id),
                "edit_allowed_id": entity_id,
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
            step_id = ObjectId(str(message["step_id"]))
        except KeyError:
            self.send_response(message["message_id"],{
                    "error": "get_step requires a 'step_id'",
                    "success":False,
            })
            return
        except bson.errors.InvalidId:
            self.send_response(message["message_id"],{
                    "error" : "The supplied 'step_id' is not a valid ObjectId.",
                    "success":False
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
                    "edit_allowed_id": step["edit_allowed_id"],
                    "skill_ids": step["skill_ids"],
                    "skill_names": step["skill_names"],
                    "success":True,
            })
            return
          
    def get_problem_steps_callback(self,message):
        entity_id = message["sender_entity_id"]
        
        try:
            problem_id = ObjectId(str(message["problem_id"]))
        except KeyError:
            self.send_response(message["message_id"], {
                "error":"get_problem_callback requires a 'problem_id'",   
                "success":False
            })
            return
        except bson.errors.InvalidId:
            self.send_response(message["message_id"],{
                    "error" : "The supplied 'problem_id' is not a valid ObjectId.",
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
                        "edit_allowed_id": step["edit_allowed_id"],
                        "skill_ids": step["skill_ids"],
                        "skill_names": step["skill_names"],
                })
            self.send_response(message["message_id"], {
                "steps": return_steps,
                "problem_id": str(problem_id),
                "success":True,
            })
            
    def _add_transaction_from_message(self,message):
        """
        This will add a transaction, but rather than send a response, will return it.
        This is so both transaction_callback and add_transaction_callback can use the same code
        """
        
        entity_id = message["sender_entity_id"]
        
        try:
            step_id = ObjectId(str(message["step_id"]))
            transaction_text = message["transaction_text"]
            session_id = message["session_id"]
            student_id = message["student_id"]
        except KeyError:
            return {
                    "error": "This action requires a 'step_id', 'session_id','student_id' and 'transaction_text'",
                    "success":False
                }
            
        except bson.errors.InvalidId:
            return {
                    "error" : "The supplied 'step_id' is not a valid ObjectId.",
                    "success":False
            }
            
        try:
            if "skill_ids" not in message:
                skill_ids = {}
            else:
                skill_ids = dict(message["skill_ids"])
        except TypeError:
            return {
                    "error" : "The supplied 'skill_ids' is not valid; must be dict.",
                    "success":False
            }
        
        try:
            if "skill_names" not in message:
                skill_names = {}
            else: 
                skill_names = dict(message["skill_names"])
        except TypeError:
            return {
                    "error" : "The supplied 'skill_names' is not valid; must be dict.",
                    "success":False
            }
        
        try:
            if "level_names" not in message:
                level_names = {"Default":"default"}
            else:
                level_names = dict(message["level_names"])
        except TypeError:
            return {
                "error": "The supplied 'level_names' is not valid; must be dict.",
                "success":False,
            }
        
        step = self.step_db.find_one({
                "_id":ObjectId(step_id),
                "edit_allowed_id":entity_id
        })
        
        if not step:
            return {
                "error": "Error: either step with provided id doesn't exist, or you do not have permission to edit.",
                "success":False,
            }
        else:
            transaction = self.transaction_db.find_one({
                    "step_id":step["_id"],
                    "transaction_text":transaction_text,
                    "edit_allowed_id": entity_id,
            })
            if not transaction:
                transaction_id = self.transaction_db.insert({
                        "step_id":step["_id"],
                        "transaction_text": transaction_text,
                        "edit_allowed_id": entity_id,
                        "date_created": datetime.now(),
                        "skill_ids": skill_ids,
                        "skill_names": skill_names,
                        "session_id":str(session_id),
                        "student_id":str(student_id),
                        "level_names":level_names,
                })
            else:
                transaction_id = transaction["_id"]
            return {
                "transaction_id": str(transaction_id),
                "success": True,
            }
        
    def add_transaction_callback(self,message):
        self.send_response(message["message_id"],self._add_transaction_from_message(message))
        """
        entity_id = message["sender_entity_id"]
        
        try:
            step_id = ObjectId(str(message["step_id"]))
            transaction_text = message["transaction_text"]
            session_id = message["session_id"]
            student_id = message["student_id"]
        except KeyError:
            self.send_response(message["message_id"],{
                    "error": "add_transaction requires a 'step_id', 'session_id','student_id' and 'transaction_text'",
                    "success":False
            })
            return
        except bson.errors.InvalidId:
            self.send_response(message["message_id"],{
                    "error" : "The supplied 'step_id' is not a valid ObjectId.",
                    "success":False
            })
            return
            
        try:
            if "skill_ids" not in message:
                skill_ids = {}
            else:
                skill_ids = dict(message["skill_ids"])
        except TypeError:
            self.send_response(message["message_id"],{
                    "error" : "The supplied 'skill_ids' is not valid; must be dict.",
                    "success":False
            })
            return
        
        try:
            if "skill_names" not in message:
                skill_names = {}
            else: 
                skill_names = dict(message["skill_names"])
        except TypeError:
            self.send_response(message["message_id"],{
                    "error" : "The supplied 'skill_names' is not valid; must be dict.",
                    "success":False
            })
            return
        
        try:
            if "level_names" not in message:
                level_names = {"Default":"default"}
            else:
                level_names = dict(message["level_names"])
        except TypeError:
            self.send_response(message["message_id"],{
                "error": "The supplied 'level_names' is not valid; must be dict.",
                "success":False,
            })
            return
        
        step = self.step_db.find_one({
                "_id":ObjectId(step_id),
                "edit_allowed_id":entity_id
        })
        
        if not step:
            self.send_response(message["message_id"], {
                "error": "Error: either step with provided id doesn't exist, or you do not have permission to edit.",
                "success":False,
            })
            return
        else:
            transaction_id = self.transaction_db.insert({
                    "step_id":step["_id"],
                    "transaction_text": transaction_text,
                    "edit_allowed_id": entity_id,
                    "date_created": datetime.now(),
                    "skill_ids": skill_ids,
                    "skill_names": skill_names,
                    "session_id":str(session_id),
                    "student_id":str(student_id),
                    "level_names":level_names,
            })
            self.send_response(message["message_id"], {
                "transaction_id": str(transaction_id),
                "success": True,
            })
        """
    
    def remove_transaction_callback(self,message):
        entity_id = message["sender_entity_id"]
        
        try:
            transaction_id = ObjectId(str(message["transaction_id"]))
        except KeyError:
            self.send_response(message["message_id"], {
                    "error": "remove_transaction requires 'transaction_id'",
                    "success":False
            })
            return
        except bson.errors.InvalidId:
            self.send_response(message["message_id"],{
                    "error" : "The supplied 'transaction_id' is not a valid ObjectId.",
                    "success":False
            })
            return
            
        transaction = self.transaction_db.find_one({
                "_id":ObjectId(transaction_id),
                "edit_allowed_id": entity_id,
        })
        if not transaction:
            self.send_response(message["message_id"], {
                    "error": "Either the transaction doesn't exist or you don't have permission to remove it.",
                    "success":False
            })
            return
        else:
            self.transaction_db.remove({"_id":ObjectId(transaction_id)})
            self.send_response(message["message_id"], {
                    "success":True,
                    "exists":True,
            })
    
    def get_step_transactions_callback(self,message):
        entity_id = message["sender_entity_id"]
        
        try:
            step_id = ObjectId(str(message["step_id"]))
        except KeyError:
            self.send_response(message["message_id"], {
                "error":"get_step_transactions_callback requires a 'step_id'",   
                "success":False
            })
            return
        except bson.errors.InvalidId:
            self.send_response(message["message_id"],{
                    "error" : "The supplied 'step_id' is not a valid ObjectId.",
                    "success":False
            })
            return
            
        step = self.step_db.find_one({"_id":ObjectId(step_id)})
        if not step:
            self.send_response(message["message_id"], {
                "error":"Step with ID " + str(step_id) + " does not exist.",
                "success":False
            })
            return
        else:
            transactions = self.transaction_db.find({"step_id":ObjectId(step_id)})
            return_transactions = []
            for transaction in transactions:
                return_transactions.append({
                        "transaction_id" : str(transaction["_id"]),
                        "transaction_text": transaction["transaction_text"],
                        "date_created": transaction["date_created"],
                        "edit_allowed_id": transaction["edit_allowed_id"],
                        "skill_ids":transaction["skill_ids"],
                        "skill_names":transaction["skill_names"],
                })
            self.send_response(message["message_id"], {
                "transactions": return_transactions,
                "step_id": str(step_id),
                "success":True,
            })
    
    
    
    
    def get_student_model_fragment_callback(self,message):      
        if self.logger:
            self.send_log_entry("GET STUDENT MODEL FRAGMENT" + str(message))
            
        try:
            student_id = str(message["student_id"])
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
        
    def transaction_callback_method(self,message):
        #check for missing values
        try:
            problem_name = message["problem_name"]
            step_text = message["step_text"]
            transaction_text = message["transaction_text"]
            session_id = message["session_id"]
            student_id = message["student_id"]
            sender_entity_id = message["sender_entity_id"]
        except KeyError:
            self.send_response(message["message_id"],{
                    "error":"Problem Manager transactions require a problem_name, step_text, transaction_text, session_id, and student_id",
                    "responder":"problem_manager"
            })
            return
            
        if "problem_text" in message:
            problem_text = message["problem_text"]
        else:
            problem_text = "none"
        
        if "step_text" in message:
            problem_text = message["step_text"]
        else:
            problem_text = "none"
        
        try:
            if "skill_ids" not in message:
                skill_ids = {}
            else:
                skill_ids = dict(message["skill_ids"])
        except TypeError:
            self.send_response(message["message_id"],{
                    "error" : "The supplied 'skill_ids' is not valid; must be dict.",
                    "success":False,
                    "responder":"problem_manager"
            })
            return
        
        try:
            if "skill_names" not in message:
                skill_names = {}
            else: 
                skill_names = dict(message["skill_names"])
        except TypeError:
            self.send_response(message["message_id"],{
                    "error" : "The supplied 'skill_names' is not valid; must be dict.",
                    "success":False,
                    "responder":"problem_manager"
            })
            return
        
        #check for problem, add if not there
        problem= self.db.find_one({"problem_name":problem_name})
        if not problem:
            problem_id = self.db.insert({
                'edit_allowed_id': sender_entity_id,
                'problem_name': problem_name,
                'problem_text': problem_text,
                'date_created': datetime.now(),
            })
        else:
            problem_id = problem["_id"]
            
        #check for step, add if not there
        step = self.step_db.find_one({"step_text":step_text,"problem_id":problem_id})
        if not step:
            step_id = self.step_db.insert({
                    "problem_id":problem_id,
                    "step_text": step_text,
                    "edit_allowed_id": sender_entity_id,
                    "date_created": datetime.now(),
                    "skill_ids": skill_ids,
                    "skill_names": skill_names,
            })
        else:
            step_id = step["_id"]
            
        #add transaction using _add_transaction_from_message
        message["step_id"] = step_id
        response = self._add_transaction_from_message(message)
        
        #update problem worked db
        if "error" not in response:
            self.worked_db.update({"student_id":student_id,"problem_id":problem_id},{"student_id":student_id,"problem_id":problem_id},upsert=True)
        
        response["responder"] = "problem_manager"
        self.send_response(message["message_id"],response)
        
            
             
                        
