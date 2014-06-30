class Command:
    description = "Show if the HPIT server is currently running or not."
    
    def __init__(self, manager, parser):
        self.manager = manager

    def run(self, arguments, configuration):
        self.arguments = arguments
        self.configuration = configuration

        print("Status is...")
        if self.manager.server_is_running():
            print("The HPIT Server is running.")
        else:
            print("The HPIT Server it not running.")
