import os
from hpit.server.app import ServerApp
from pymongo import MongoClient
app_instance = ServerApp.get_instance()
app = app_instance.app
db = app_instance.db
mongo = app_instance.mongo

from hpit.management.settings_manager import SettingsManager
settings = SettingsManager.get_server_settings()
plugin_settings = SettingsManager.get_plugin_settings()


class Command:
    description = "Indexes the Mongo Database."
    
    def __init__(self, manager, parser):
        self.manager = manager

    def run(self, arguments, configuration):
        self.arguments = arguments
        self.configuration = configuration

        #server dbs
        with app.app_context():
            mongo.db.plugin_messages.create_index('receiver_entity_id')
            mongo.db.plugin_transactions.create_index('receiver_entity_id')

            mongo.db.sent_messages_and_transactions.create_index('time_received')
            mongo.db.sent_responses.create_index('time_response_received')

            mongo.db.sent_messages_and_transactions.create_index([
                ("receiver_entity_id", -1),
                ("message_id", 1)
            ])
            mongo.db.responses.create_index([
                    ('receiver_entity_id',1),
                    ('session_token',1)
            ])
            
        #plugin dbs
        plugin_mongo = MongoClient(plugin_settings.MONGODB_URI)
        plugin_db = plugin_mongo[plugin_settings.MONGO_DBNAME]
        plugin_db.hpit_problems.create_index([
            ('problem_text', 1),
            ('problem_name', 1)
        ])
        plugin_db.hpit_knowledge_tracing.create_index([
            ('skill_id', 1),
            ('student_id', 1),
            ('sender_entity_id', 1)
        ])
        plugin_db.hpit_knowledge_tracing.create_index('student_id')

        print("DONE! - Indexed the mongo database.")