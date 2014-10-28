"""
This script is used to start the Flask server on Windows.  In Unix, uWSGI 
is used to start the server, which is coded using relative imports.  This is a 
workaround so the relative imports are preserved in Windows.
"""

import os
from management.settings_manager import SettingsManager

try:
    settings_manager = SettingsManager.init_instance(os.environ['HPIT_ENV'])
except KeyError:
    settings_manager = SettingsManager.init_instance('debug')
    
from server.views.api import *
from server.views.dashboard import *
from server.app import ServerApp

server_app = ServerApp.get_instance()
server_app.bootstrap_user()

server_app.app.run(port = int(settings_manager.HPIT_BIND_PORT))
