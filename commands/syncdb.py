from server import db

class Command:
    description = "Creates all the tables in the database."

    def run(self, args, configuration):
        self.args = args
        self.configuration = configuration

        db.create_all()
