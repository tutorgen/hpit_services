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
        
        self.problem_fields = ["problem_name","problem_text"]

    def post_connect(self):
        super().post_connect()
        
        self.subscribe(
            add_problem=self.add_problem_callback,
            remove_problem=self.remove_problem_callback,
            get_problem=self.get_problem_callback,
            list_problems=self.list_problems_callback)

    #Problem Management Plugin
    def add_problem_callback(self, message):
        sender_entity_id = message['sender_entity_id']
        problem_name = message['problem_name']
        problem_text = message['problem_text']

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
                'problem_id':problem_id
            })
        
        else:
            self.send_response(message['message_id'], {
                'error': "This problem already exists.  Try cloning the 'problem_id' sent in this response.",
                'problem_id': problem["_id"],
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
                'problem_id': problem_id,
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
        else:
            self.send_response(message['message_id'], {
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
