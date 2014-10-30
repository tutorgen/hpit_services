import argparse
import json
import os
import sys
import pkgutil
import subprocess
import signal
import time
import shutil
from hpit.management import commands

from hpit.server.app import ServerApp
from hpit.management.settings_manager import SettingsManager

class EntityManager:

    def __init__(self):
        self.settings = SettingsManager.get_server_settings()
        self.app_instance = ServerApp.get_instance()
        self.app_instance.bootstrap_user()

    def read_configuration(self):
        """
        Read the JSON configuration file and return the config parameters
        """
        
        try:
            with open('configuration.json', 'r') as f:
                return json.loads(''.join(f.read()))
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
        
        
    def get_entity_pid_file(self, entity_type, entity_id):
        """
        Get the PID filename, which helps the system keep track of running processes.
        """
        
        return os.path.join('tmp', entity_type + '_' + entity_id + '.pid')
        
        
    def build_sub_commands(self, subparsers):
        pkgpath = os.path.dirname(commands.__file__)
        pkgs = pkgutil.iter_modules([pkgpath])
        for _, name, _ in pkgs:
            pkg = __import__('hpit.management.commands.' + name, globals(), locals(), ['Command'], 0)
            pkg_parser = subparsers.add_parser(name)
            cmd = pkg.Command(self, pkg_parser)
            pkg_parser.set_defaults(description=cmd.description, func=cmd.run)

            if hasattr(cmd, 'arguments'):
                for argument in cmd.arguments:
                    pkg_parser.add_argument(argument)


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

        try:
            arguments.func(arguments, configuration)
        except AttributeError:
            main_parser.print_help()

        self.write_configuration(configuration)
        
        
    def spin_up_entity(self, entity, entity_type):
        """
        Start an entity, as specified in configuration
        """
        
        entity_subtype = entity['type']
        entity_id = entity['entity_id']
        api_key = entity['api_key']

        name = 'Unknown'
        if 'name' in entity:
            name = entity['name']
        
        subp_args = [sys.executable, '-m', 'hpit.management.entity_daemon']

        if 'args' in entity:
            entity_args = shlex.quote(json.dumps(entity['args']))
            subp_args.append("--args")
            subp_args.append(entity_args)
            
        if 'once' in entity:
            subp_args.append("--once")
            
        subp_args.extend([entity_id, api_key, entity_type, entity_subtype])
        
        print("Starting entity: " + name + " ID#: " + entity_id)

        with open("log/output_"+entity_type+"_"+entity_subtype+".txt","w") as f:
            subp = subprocess.Popen(subp_args, stdout = f, stderr = f)

        pidfile = self.get_entity_pid_file(entity_type, entity_id)
       
        with open(pidfile,"w") as pfile:
            pfile.write(str(subp.pid))


    def wind_down_entity(self, entity, entity_type):
        """
        Shut down all entities of a given type from a collection
        """
        
        entity_id = entity['entity_id']
        print("Stopping entity: " + entity_id)
        pidfile = self.get_entity_pid_file(entity_type, entity_id)

        try:
            with open(pidfile) as f:
                pid = f.read()

                try:
                    os.kill(int(pid), signal.SIGTERM)
                except OSError:
                    print("Failed to kill entity " + str(entity_id))

            os.remove(pidfile)
        except ProcessLookupError:
            print("Error: Process ID not found. The process may have exited prematurely.")
        except FileNotFoundError:
            print("Error: Could not find PIDfile for entity: " + entity_id)


    def start(self, arguments, configuration):
        """
        Start the tutors and plugins as specified in configuration
        """
        
        if not os.path.exists('tmp'):
            os.makedirs('tmp')

        if not os.path.exists('log'):
            os.makedirs('log')

        print("Starting plugins...")
        entity_collection = self.get_entity_collection('plugin', configuration)

        for item in entity_collection:
            if item['active']:
                continue;

            item['active'] = True
            self.spin_up_entity(item, 'plugin')

        for i in range(0, 10):
            print("Waiting " + str(10 - i) + " seconds for the plugins to boot.\r", end='')
            time.sleep(1)
        print("")
        
        print("Starting tutors...")
        entity_collection = self.get_entity_collection('tutor', configuration)

        for item in entity_collection:
            if item['active']:
                continue;

            item['active'] = True
            self.spin_up_entity(item, 'tutor')

        print("DONE!")


    def stop(self, arguments, configuration):
        """
        Stop the hpit server, plugins, and tutors.
        """
        
        print("Stopping plugins...")
        entity_collection = self.get_entity_collection('plugin', configuration)

        for item in entity_collection:
            if not item['active']:
                continue;

            item['active'] = False
            self.wind_down_entity(item, 'plugin')

        print("Stopping tutors...")
        entity_collection = self.get_entity_collection('tutor', configuration)

        for item in entity_collection:
            if not item['active']:
                continue;

            item['active'] = False
            self.wind_down_entity(item, 'tutor')

        #Cleanup the tmp directory
        try:
            shutil.rmtree('tmp')
        except FileNotFoundError:
            pass

        print("DONE!")




