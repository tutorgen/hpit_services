from environment.settings_manager import SettingsManager
settings_manager = SettingsManager.init_instance('production')

from server.views.api import *
from server.views.dashboard import *
from server.app import ServerApp

server_app = ServerApp.get_instance()
server_app.bootstrap_user()

app = server_app.app
