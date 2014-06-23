from client import Plugin

from pymongo import MongoClient

class KnowledgeTracingPlugin(Plugin):

    def __init__(self, entity_id, api_key, logger, args = None):
        super().__init__(entity_id, api_key)
        self.logger = logger
        self.mongo = MongoClient('mongodb://localhost:27017/')
        self.db = self.mongo.hpit.hpit_knowledge_tracing


    def post_connect(self):
        super().post_connect()
        
        self.subscribe(
            kt_set_initial=self.kt_set_initial_callback,
            kt_reset=self.kt_reset,
            kt_trace=self.kt_trace)

    #Knowledge Tracing Plugin
    def kt_trace(self, message):
        self.logger.debug("RECV: kt_trace with message: " + str(message))

        kt_config = self.db.find_one({
            'entity_id': message['entity_id'],
            'skill': message['skill']
        })

        if not kt_config:
            self.logger.debug("ERROR: Could not find inital setting for knowledge tracer.")
            self.send_response(message['id'], {
                'error': 'No initial settings for plugin (KnowledgeTracingPlugin).',
                'send': {
                    'event_name': 'kt_set_initial',
                    'probability_known': 'float(0.0-1.0)', 
                    'probability_learned': 'float(0.0-1.0)',
                    'probability_guess': 'float(0.0-1.0)',
                    'probability_mistake': 'float(0.0-1.0)'
                }
            })

            return True

        p_known = kt_config['probability_known']
        p_learned = kt_config['probability_learned']
        p_guess = kt_config['probability_guess']
        p_mistake = kt_config['probability_mistake']

        correct = message['correct']

        numer = 0
        denom = 1

        if correct:
            numer = p_known * (1 - p_mistake)
            denom = numer + (1 - p_known) * p_guess
        else:
            numer = p_known * p_mistake
            denom = numer + (1 - p_known) * (1 - p_guess)

        p_known_prime = numer / denom if denom != 0 else 0
        p_known = p_known_prime + (1 - p_known_prime) * p_learned

        self.db.update({'_id': kt_config['_id']}, {'$set': {
            'probability_known': p_known
        }})

        self.logger.debug("SUCCESS: kt_trace with new data: " + str(kt_config))

        self.send_response(message['id'], {
            'skill': kt_config['skill'],
            'probability_known': p_known,
            'probability_learned': p_learned,
            'probability_guess': p_guess,
            'probability_mistake': p_mistake
            })

    def kt_set_initial_callback(self, message):
        self.logger.debug("RECV: kt_set_initial with message: " + str(message))

        kt_config = self.db.find_one({
            'entity_id': message['entity_id'],
            'skill': message['skill']
        })

        if not kt_config:
            self.db.insert({
                'entity_id': message['entity_id'],
                'skill': message['skill'],
                'probability_known': message['probability_known'],
                'probability_learned': message['probability_learned'],
                'probability_guess': message['probability_guess'],
                'probability_mistake': message['probability_mistake']
                })
        else:
            self.db.update({'_id': kt_config['_id']},
                {'$set': {
                    'probability_known' : message['probability_known'],
                    'probability_learned' : message['probability_learned'],
                    'probability_guess' : message['probability_guess'],
                    'probability_mistake' : message['probability_mistake']
                }})

        self.send_response(message['id'], {
            'skill': message['skill'],
            'probability_known': message['probability_known'],
            'probability_learned': message['probability_learned'],
            'probability_guess': message['probability_guess'],
            'probability_mistake': message['probability_mistake']
            })

    def kt_reset(self, message):
        self.logger.debug("RECV: kt_reset with message: " + str(message))

        kt_config = self.db.find_one({
            'entity_id': message['entity_id'],
            'skill': message['skill']
        })

        if kt_config:
            self.db.update({'_id': kt_config['_id']}, {'$set': {
                'probability_known': 0.0,
                'probability_learned': 0.0,
                'probability_guess': 0.0,
                'probability_mistake': 0.0
            }})

        self.send_response(message['id'], {
            'skill': kt_config['skill'],
            'probability_known': 0.0,
            'probability_learned': 0.0,
            'probability_guess': 0.0,
            'probability_mistake': 0.0
        })
