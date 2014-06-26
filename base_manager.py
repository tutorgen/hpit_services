import argparse
import json
import os
import commands
import pkgutil

from server.app import ServerApp
from server.settings import ServerSettingsManager

class BaseManager:

    def __init__(self):
        self.settings = ServerSettingsManager.get_instance().settings
        self.app_instance = ServerApp.get_instance()
        self.app_instance.bootstrap_user()

    def read_configuration(self):
        """
        Read the JSON configuration file and return the config parameters
        """
        
        try:
            with open('configuration.json', 'r') as f:
                return json.loads(''.join(f.readlines()))
        except FileNotFoundError:
            return {}
            
            
    def write_configuration(self, configuration):
        """
        Dump the JSON configuration to a file
        """
        
        with open('configuration.json', 'w') as f:
            f.write(json.dumps(configuration, indent=4))
            
            
    def get_entity_collection(self, entity_type, configuration):
        """
        Get a collection of entities based on its name, from a given configuration.
        """

        plural = entity_type + 's'

        things = []
        if plural in configuration:
            things = configuration[plural]

        return things
        
        
    def set_entity_collection(self, entity_type, configuration, collection):
        """
        Set the collection of similar entities in a configuration
        """

        plural = entity_type + 's'
        configuration[plural] = collection
        
        
    def get_entity_pid_file(self, entity_type, entity_name):
        """
        Get the PID filename, which helps the system keep track of running processes.
        """
        
        return os.path.join('tmp', entity_type + '_' + entity_name + '.pid')
        
        
    def server_is_running(self):
        """
        If the PID is there, then it must be running
        """
        return os.path.isfile(self.settings.HPIT_PID_FILE)
        
        
    def status(self, arguments, configuration):
        """
        Print the running status of the server.
        """
        
        print("Status is...")
        if self.server_is_running():
            print("The HPIT Server is running.")
        else:
            print("The HPIT Server it not running.")


    def run_add(self, arguments, configuration):
        from commands.add import Command
        Command(arguments, configuration).run()

    def run_remove(self, arguments, configuration):
        from commands.remove import Command
        Command(arguments, configuration).run()

    def run_test(self, arguments, configuration):
        from commands.test import Command
        Command(arguments, configuration).run()

    def run_debug(self, arguments, configuration):
        from commands.debug import Command
        Command(arguments, configuration).run()

    def run_syncdb(self, arguments, configuration):
        from commands.syncdb import Command
        Command(arguments, configuration).run()

    def run_routes(self, arguments, configuration):
        from commands.routes import Command
        Command(arguments, configuration).run()

    def run_docs(self, arguments, configuration):
        from commands.docs import Command
        Command(arguments, configuration).run()

    def run_assets(self, arguments, configuration):
        from commands.assets import Command
        Command(arguments, configuration).run()


    def build_sub_commands(self, subparsers):
        pkgpath = os.path.dirname(commands.__file__)
        pkgs = pkgutil.iter_modules([pkgpath])
        for _, name, _ in pkgs:
            pkg = __import__('commands.' + name, globals(), locals(), ['Command'], 0)
            pkg_parser = subparsers.add_parser(name)
            cmd = pkg.Command(self, pkg_parser)
            pkg_parser.set_defaults(description=cmd.description, func=cmd.run)


    def build_argument_parser(self):
        """
        Generate the argument parser for the manager using Python ArgumentParser
        """
        
        main_parser = argparse.ArgumentParser(
            description='Manager that spins up plugins, tutors, and web services.')
        main_parser.add_argument('--version', action='version', 
            version=self.settings.HPIT_VERSION)

        subparsers = main_parser.add_subparsers(title='Sub-Commands')

        self.build_sub_commands(subparsers)

        status_parser = subparsers.add_parser('status', description='Status of HPIT System')
        status_parser.set_defaults(func=self.status)

        start_parser = subparsers.add_parser('start', description='Bring all entities online.')
        start_parser.set_defaults(func=self.start)

        stop_parser = subparsers.add_parser('stop', description='Take all entities offline.')
        stop_parser.set_defaults(func=self.stop)

        return main_parser


    def run_manager(self):
        """
        Replaces the old main entry point
        """
        configuration = self.read_configuration()
        main_parser = self.build_argument_parser()
        arguments = main_parser.parse_args()

        import pdb; pdb.set_trace()
        try:
            arguments.func(arguments, configuration)
        except AttributeError:
            main_parser.print_help()

        self.write_configuration(configuration)
        
        
    def wind_down_all(entity_type, configuration):
        """
        Stop all entities of a certain type
        """
        
        entity_collection = self.get_entity_collection(entity_type, configuration)
        wind_down_collection(entity_type, entity_collection)
    




