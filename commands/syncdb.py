import os
from server.app import ServerApp
db = ServerApp.get_instance().db

class Command:
    description = "Creates all the tables in the database."
    
    def __init__(self, manager, parser):
        self.manager = manager

    def run(self, arguments, configuration):
        self.arguments = arguments
        self.configuration = configuration

        db.create_all()

        try:
            os.mkdir(os.path.join(os.getcwd(), 'server/db/mongo'))
        except FileExistsError:
            pass

        print("DONE! - Sync'd the database with the data model")