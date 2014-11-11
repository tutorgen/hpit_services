import os
from hpit.server.app import ServerApp
app_instance = ServerApp.get_instance()
app = app_instance.app
db = app_instance.db
mongo = app_instance.mongo

from hpit.management.settings_manager import SettingsManager
settings = SettingsManager.get_server_settings()

class Command:
    description = "Indexes the Mongo Database."
    
    def __init__(self, manager, parser):
        self.manager = manager

    def run(self, arguments, configuration):
        self.arguments = arguments
        self.configuration = configuration

        with app.app_context():
            mongo.db.plugin_messages.create_index('receiver_entity_id')
            mongo.db.plugin_transactions.create_index('receiver_entity_id')

            mongo.db.sent_messages_and_transactions.create_index('time_received')
            mongo.db.sent_responses.create_index('time_response_received')

            mongo.db.sent_messages_and_transactions.create_index([
                ("receiver_entity_id", -1),
                ("message_id", 1)
            ])
            mongo.db.responses.create_index('receiver_entity_id')
            mongo.db.hpit_problems.create_index([
                ('problem_text', 1),
                ('problem_name', 1)
            ])
            mongo.db.hpit_knowledge_tracing.create_index([
                ('skill_id', 1),
                ('student_id', 1),
                ('sender_entity_id', 1)
            ])
            mongo.db.hpit_knowledge_tracing.create_index('student_id')

        print("DONE! - Indexed the mongo database.")