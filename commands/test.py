import os
import nose

class Command:
    description = "Unit Test the code."
    
    def __init__(self, manager, parser):
        self.manager = manager
    
    def run(self, args, configuration):
        self.args = args
        self.configuration = configuration
        
        nose.main(argv=['-w', os.path.join(os.getcwd(), 'tests'), '--verbose'])
