import os
import nose

from environment.settings_manager import SettingsManager
settings = SettingsManager.get_server_settings()

class Command:
    description = "Unit Test the code."
    arguments = ['--test-path']
    
    def __init__(self, manager, parser):
        self.manager = manager
    
    def run(self, arguments, configuration):
        
        if "test" not in os.environ['HPIT_ENV']:
            answer = input("WARNING: 'test' is not found in HPIT_ENV " + os.environ['HPIT_ENV'] + ". Continue anyway? [y/n] ")
            if answer.lower() == "n":
                return
        
        self.configuration = configuration

        test_path = os.path.join(settings.PROJECT_DIR, 'tests')

        if arguments.test_path:
            test_path = arguments.test_path

        nose.main(argv=['-w', test_path, '--verbose' , '--nologcapture'])
