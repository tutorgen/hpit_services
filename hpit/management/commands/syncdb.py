import os
from hpit.server.app import ServerApp
app_instance = ServerApp.get_instance()
app = app_instance.app
db = app_instance.db
mongo = app_instance.mongo

from hpit.management.settings_manager import SettingsManager
settings = SettingsManager.get_server_settings()

class Command:
    description = "Creates all the tables in the database."
    
    def __init__(self, manager, parser):
        self.manager = manager

    def run(self, arguments, configuration):
        self.arguments = arguments
        self.configuration = configuration

        db.create_all()

        with app.app_context():
            mongo.db.plugin_messages.create_index('receiver_entity_id')

        try:
            os.mkdir(os.path.join(settings.PROJECT_DIR, 'hpit/server/db/mongo'))
        except FileExistsError:
            pass

        print("DONE! - Sync'd the database with the data model")