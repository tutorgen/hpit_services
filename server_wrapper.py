"""
This script is used to start the Flask server on Windows.  In Unix, gunicorn 
is used to start the server, which is coded using relative imports.  This is a 
workaround so the relative imports are preserved in Windows.
"""

#from server import app
#from server.settings import settings

from environment.settings_manager import SettingsManager
settings_manager = SettingsManager.init_instance('production')
settings = SettingsManager.get_server_settings()

from server.views.api import *
from server.views.dashboard import *
from server.app import ServerApp

server_app = ServerApp.get_instance()
server_app.bootstrap_user()

server_app.app.run(port = int(settings.HPIT_BIND_PORT))
