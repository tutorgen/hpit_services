import urllib.parse

from hpit.server.app import ServerApp
app = ServerApp.get_instance().app

class Command:
    description = "Lists all the available routes."
    
    def __init__(self, manager, parser):
        self.manager = manager

    def run(self, arguments, configuration):
        self.arguments = arguments
        self.configuration = configuration

        output = []
        for rule in app.url_map.iter_rules():

            options = {}
            for arg in rule.arguments:
                options[arg] = "[{0}]".format(arg)

            methods = ','.join(rule.methods)
            output.append(urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, str(rule))))

        for line in sorted(output):
            print(line)
