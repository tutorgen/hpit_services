from server import db

class Command:
    description = "Creates all the tables in the database."
    
    def __init__(self, manager, parser):
        self.manager = manager

    def run(self, args, configuration):
        self.args = args
        self.configuration = configuration

        db.create_all()
