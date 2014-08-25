import os
import nose

class Command:
    description = "Unit Test the code."
    arguments = ['--test-path']
    
    def __init__(self, manager, parser):
        self.manager = manager
    
    def run(self, arguments, configuration):
        self.configuration = configuration

        test_path = os.path.join(os.getcwd(), 'tests')

        if arguments.test_path:
            test_path = arguments.test_path

        nose.main(argv=['-w', test_path, '--verbose' , '--nologcapture'])
