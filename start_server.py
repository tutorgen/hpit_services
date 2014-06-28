from server.settings import ServerSettingsManager
settings_manager = ServerSettingsManager.init_instance('production')

from server.views.api import *
from server.views.dashboard import *
from server.app import ServerApp

server_app = ServerApp.get_instance()
server_app.bootstrap_user()

app = server_app.app
