from server import app

class Command:
    description = "Runs the server in debug mode."
    
    def run(self, args, configuration):
        self.args = args
        self.configuration = configuration

        app.run(debug=True, port=8000)
