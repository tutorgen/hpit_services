import pytest

class Command:
    description = "Unit Test the code."
    
    def __init__(self, manager, parser):
        self.manager = manager
    
    def run(self, args, configuration):
        self.args = args
        self.configuration = configuration

        pytest.main(['tests','--tb=short'])
