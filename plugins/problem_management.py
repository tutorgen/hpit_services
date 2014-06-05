from client import Plugin

from pymongo import MongoClient

class ProblemManagementPlugin(Plugin):

    def __init__(self, name, logger,args = None):
        super().__init__(name)
        self.logger = logger
        self.mongo = MongoClient('mongodb://localhost:27017/')
        self.db = self.mongo.hpit.problems

        self.subscribe(
            add_problem=self.add_problem_callback,
            remove_problem=self.remove_problem_callback,
            get_problem=self.get_problem_callback,
            list_problems=self.list_problems_callback)

    #Problem Management Plugin
    def add_problem_callback(self, transaction):
        entity_id = transaction['entity_id']
        problem_name = transaction['problem_name']
        problem_text = transaction['problem_text']

        problem = self.db.find_one({
            'entity_id': entity_id,
            'problem_name': problem_name,
            })

        if not problem:
            self.db.insert({
                'entity_id': entity_id,
                'problem_name': problem_name,
                'problem_text': problem_text,
            })

            self.send_response(transaction['id'], {
                'problem_name': problem_name,
                'problem_text': problem_text,
                'success': True,
                'updated': False
            })
        else:
            self.db.update({'_id': problem['_id']}, {
                'entity_id': entity_id,
                'problem_name': problem_name,
                'problem_text': problem_text,
            })

            self.send_response(transaction['id'], {
                'problem_name': problem_name,
                'problem_text': problem_text,
                'success': True,
                'updated': True
            })


    def remove_problem_callback(self, transaction):
        entity_id = transaction['entity_id']
        problem_name = transaction['problem_name']

        problem = self.db.find_one({
            'entity_id': entity_id,
            'problem_name': problem_name,
        })

        if problem:
            self.db.remove({
                'entity_id': entity_id,
                'problem_name': problem_name,
            })

            self.send_response(transaction['id'], {
                'problem_name': problem_name,
                'exists': True,
                'success': True,
            })
        else:
            self.send_response(transaction['id'], {
                'problem_name': problem_name,
                'exists': False,
                'success': False
            })


    def get_problem_callback(self, transaction):
        entity_id = transaction['entity_id']
        problem_name = transaction['problem_name']

        problem = self.db.find_one({
            'entity_id': entity_id,
            'problem_name': problem_name,
        })

        if not problem:
            self.send_response(transaction['id'], {
                'problem_name': problem_name,
                'exists': False,
                'success': False
            })
        else:
            self.send_response(transaction['id'], {
                'problem_name': problem_name,
                'problem_text': problem['problem_text'],
                'exists': True,
                'success': True
            })

    def list_problems_callback(self, transaction):
        entity_id = transaction['entity_id']

        problems = self.db.find({
            'entity_id': entity_id
        })

        problems = [p for p in problems]

        self.send_response(transaction['id'], {
            'problems': problems,
            'success': True
        })
