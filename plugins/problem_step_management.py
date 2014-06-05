from client import Plugin

from pymongo import MongoClient

class ProblemStepManagementPlugin(Plugin):

    def __init__(self, name, logger, args = None):
        super().__init__(name)
        self.logger = logger
        self.mongo = MongoClient('mongodb://localhost:27017/')
        self.db = self.mongo.hpit.problem_steps

        self.subscribe(
            add_problem_step=self.add_problem_step,
            remove_problem_step=self.remove_problem_step,
            get_problem_step=self.get_problem_step_callback,
            list_problem_steps=self.list_problem_steps_callback)

    def add_problem_step_callback(self, transaction):
        entity_id = transaction['entity_id']
        problem_name = transaction['problem_name']
        problem_step_name = transaction['problem_step_name']
        problem_step_text = transaction['problem_step_text']

        problem_step = self.db.find_one({
            'entity_id': entity_id,
            'problem_name': problem_name,
            'problem_step_name': problem_step_name
        })

        if not problem_step:
            self.db.insert({
                'entity_id': entity_id,
                'problem_name': problem_name,
                'problem_step_name': problem_step_name,
                'problem_step_text': problem_step_text,
            })

            self.send_response(transaction['id'], {
                'problem_name': problem_name,
                'problem_step_name': problem_step_name,
                'problem_step_text': problem_step_text,
                'success': True,
                'updated': False
            })
        else:
            self.db.update({'_id': problem['_id']}, {
                'entity_id': entity_id,
                'problem_name': problem_name,
                'problem_step_name': problem_step_name,
                'problem_step_text': problem_step_text,
            })

            self.send_response(transaction['id'], {
                'problem_name': problem_name,
                'problem_step_name': problem_step_name,
                'problem_step_text': problem_step_text,
                'success': True,
                'updated': True
            })

    def remove_problem_step_callback(self, transaction):
        entity_id = transaction['entity_id']
        problem_name = transaction['problem_name']
        problem_step_name = transaction['problem_step_name']

        problem_step = self.db.find_one({
            'entity_id': entity_id,
            'problem_name': problem_name,
            'problem_step_name': problem_step_name
        })

        if problem_step:
            self.db.remove({
                'entity_id': entity_id,
                'problem_name': problem_name,
                'problem_step_name': problem_step_name
            })

            self.send_response(transaction['id'], {
                'problem_name': problem_name,
                'problem_step_name': problem_step_name,
                'exists': True,
                'success': True,
            })
        else:
            self.send_response(transaction['id'], {
                'problem_name': problem_name,
                'problem_step_name': problem_step_name,
                'exists': False,
                'success': False
            })

    def get_problem_step_callback(self, transaction):
        entity_id = transaction['entity_id']
        problem_name = transaction['problem_name']
        problem_step_name = transaction['problem_step_name']

        problem_step = self.db.find_one({
            'entity_id': entity_id,
            'problem_name': problem_name,
            'problem_step_name': problem_step_name
        })

        if not problem_step:
            self.send_response(transaction['id'], {
                'problem_name': problem_name,
                'problem_step_name': problem_step_name,
                'exists': False,
                'success': False
            })
        else:
            self.send_response(transaction['id'], {
                'problem_name': problem_name,
                'problem_step_name': problem_step_name,
                'problem_step_text': problem_step['problem_step_text'],
                'exists': True,
                'success': True
            })

    def list_problem_steps_callback(self, transaction):
        entity_id = transaction['entity_id']

        if 'problem_name' in transaction:
            problem_name = transaction['problem_name']
            problem_steps = self.db.find({
                'entity_id': entity_id,
                'problem_name': problem_name
            })

            problem_steps = [p for p in problem_steps]

            self.send_response(transaction['id'], {
                'problem_steps': problem_steps,
                'success': True
            })
        else:
            problem_steps = self.db.find({
                'entity_id': entity_id
            })

            problem_steps = [p for p in problem_steps]

            self.send_response(transaction['id'], {
                'problem_name': problem_name,
                'problem_steps': problem_steps,
                'success': True
            })
