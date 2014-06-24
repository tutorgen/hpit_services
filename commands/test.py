import pytest

class Command:
    description = "Unit Test the code."
    
    def run(self, args, configuration):
        self.args = args
        self.configuration = configuration

        pytest.main(['-x', 'tests'])
