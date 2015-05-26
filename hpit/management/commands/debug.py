from hpit.server.app import ServerApp
app = ServerApp.get_instance().app

from hpit.management.settings_manager import SettingsManager
settings = SettingsManager.get_server_settings()

class Command:
    description = "Runs the server in debug mode."
    
    def __init__(self, manager, parser):
        self.manager = manager
    
    def run(self, args, configuration):
        self.args = args
        self.configuration = configuration

        app.run(debug=True, port=int(settings.HPIT_BIND_PORT), host=settings.HPIT_BIND_IP, use_reloader=False)
