import os
import subprocess

from management.settings_manager import SettingsManager
settings = SettingsManager.get_server_settings()

class Command:
    description = "Start the mongodb server."
    
    def __init__(self, manager, parser):
        self.manager = manager
    
    def run(self, args, configuration):
        self.args = args
        self.configuration = configuration
       
        subprocess.call(['mongod', '--dbpath', os.path.join(settings.PROJECT_DIR, 'server/db/mongo')]) 
