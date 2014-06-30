from server.app import ServerApp
app = ServerApp.get_instance().app

class Command:
    description = "Runs the server in debug mode."
    
    def __init__(self, manager, parser):
        self.manager = manager
    
    def run(self, args, configuration):
        self.args = args
        self.configuration = configuration

        app.run(debug=True, port=8000, host='0.0.0.0')
