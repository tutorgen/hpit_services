import os

from server.app import ServerApp
db = ServerApp.get_instance().db

from server.models import User

class Command:
    description = "Change user Administrator status."

    def __init__(self, manager, parser):
        self.manager = manager

        parser.add_argument("--add",type=str,help="Make username in argument an administrator")
        parser.add_argument("--remove",type=str,help="Make username in argument a non administrator")
        parser.add_argument("--status",type=str,help="Is username an administrator?")

    def run(self, arguments, configuration):
        self.arguments = arguments
        self.configuration = configuration
        
        if arguments.status:
            user = User.query.filter(User.username==arguments.add).first()
            if user:
                if user.administrator == True:
                    print ("User " + arguments.add + " is an Administrator.")
                else:
                    print ("User " + arguments.add + " is not an Administrator.")
            else:
                print("Could not find user " + arguments.add)
        
        elif arguments.add:
            user = User.query.filter(User.username==arguments.add).first()
            if user:
                user.administrator = True
                db.session.commit()
                print ("User " + arguments.add + " is now an Administrator.")
            else:
                print("Could not find user " + arguments.add)
                
        elif arguments.remove:
            user = User.query.filter(User.username==arguments.remove).first()
            if user:
                user.administrator = False
                db.session.commit()
                print ("User " + arguments.remove + " is not an Administrator.")
            else:
                print("Could not find user " + arguments.remove)
            
        

       
