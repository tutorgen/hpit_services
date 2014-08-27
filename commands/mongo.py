import os
import subprocess

from .settings import ServerSettingsManager
settings = ServerSettingsManager.get_instance().settings

class Command:
    description = "Start the mongodb server."
    
    def __init__(self, manager, parser):
        self.manager = manager
    
    def run(self, args, configuration):
        self.args = args
        self.configuration = configuration
       
        subprocess.call(['mongod', '--dbpath', os.path.join(settings.PROJECT_DIR, 'server/db/mongo')]) 
