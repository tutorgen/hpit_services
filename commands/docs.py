import shutil

class Command:
    description = "Copy's the root project README.md to the server assets folder."

    def run(self, args, configuration):
        self.args = args
        self.configuration = configuration

        shutil.copy('./README.md', './server/assets/docs.md')
