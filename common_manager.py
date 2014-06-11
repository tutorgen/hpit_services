import argparse
import json
import os
import commands
import pkgutil

from server.settings import settings

import platform
if platform.system() == "Windows":
    from win_manager import *
else:
    from unix_manager import *



def read_configuration():
    """
    Read the JSON configuration file and return the config parameters
    """
    
    try:
        with open('configuration.json', 'r') as f:
            return json.loads(''.join(f.readlines()))
    except FileNotFoundError:
        return {}
        
        
def write_configuration(configuration):
    """
    Dump the JSON configuration to a file
    """
    
    with open('configuration.json', 'w') as f:
        f.write(json.dumps(configuration, indent=4))
        
        
def get_entity_collection(entity_type, configuration):
    """
    Get a collection of entities based on its name, from a given configuration.
    """

    plural = entity_type + 's'

    things = []
    if plural in configuration:
        things = configuration[plural]

    return things
    
    
def set_entity_collection(entity_type, configuration, collection):
    """
    Set the collection of similar entities in a configuration
    """

    plural = entity_type + 's'
    configuration[plural] = collection
    
    
def get_entity_py_file(entity_type, subtype):
    """
    Get the filename of the source file associated with a tutor/plugin implemetation
    """
    
    plural = entity_type + 's'
    return os.path.join(plural, subtype + '.py')


def get_entity_pid_file(entity_type, entity_name):
    """
    Get the PID filename, which helps the system keep track of running processes.
    """
    
    return os.path.join('tmp', entity_type + '_' + entity_name + '.pid')
    
    
def server_is_running():
    """
    If the PID is there, then it must be running
    """
    return os.path.isfile(settings.HPIT_PID_FILE)
    
    
def add_entity(arguments, configuration):
    """
    Add and entity to be spun up by HPIT
    """
    
    things = get_entity_collection(arguments.entity, configuration)

    count = arguments.count if arguments.count else 1
    entity_type = arguments.type if arguments.type else 'example'

    for thing in things:
        names = thing['name'].split('.')

        if arguments.name in names:
            raise ValueError("Entity already exists in configuration.")

    for i in range(0, count):
        name = '.'.join([arguments.name, str(i)])

        things.append({
            'name': name,
            'type': entity_type,
            'active': False
            })

    set_entity_collection(arguments.entity, configuration, things)

    if server_is_running():
        spin_up_all(arguments.entity, configuration)
    
    
def remove_entity(arguments, configuration):
    """
    Stop an entity from running
    """
    
    things = get_entity_collection(arguments.entity, configuration)

    things_to_remove = []
    things_to_keep = []

    for thing in things:
        names = thing['name'].split('.')

        if arguments.name in names:
            things_to_remove.append(thing)
        else:
            things_to_keep.append(thing)

    set_entity_collection(arguments.entity, configuration, things_to_keep)

    if server_is_running():
        wind_down_collection(things_to_remove)
        
   
def status(arguments, configuration):
    """
    Print the running status of the server.
    """
    
    print("Status is...")
    if server_is_running():
        print("The HPIT Server is running.")
    else:
        print("The HPIT Server it not running.")


def create_command(sub, name, description, func):
    """
    Called in build_argument_parser; an encapsulation for adding sub parsers
    """
    parser = sub.add_parser(name, description=description)
    parser.add_argument('entity', metavar='entity', type=str, 
                        choices=['plugin', 'tutor', 'service'], 
                        help='A plugin, tutor or service entity.')
    parser.add_argument('name', metavar='name', type=str, 
                        help="Indentifying name for the entity.")
    parser.add_argument('--type', type=str, 
                        help="The subtype of the entity. (default=example)")
    parser.set_defaults(func=func)

    return parser


def run_test(arguments, configuration):
    from commands.test import Command
    Command(arguments, configuration).run()

def run_debug(arguments, configuration):
    from commands.debug import Command
    Command(arguments, configuration).run()

def run_syncdb(arguments, configuration):
    from commands.syncdb import Command
    Command(arguments, configuration).run()

def run_routes(arguments, configuration):
    from commands.routes import Command
    Command(arguments, configuration).run()

def run_docs(arguments, configuration):
    from commands.docs import Command
    Command(arguments, configuration).run()

def run_assets(arguments, configuration):
    from commands.assets import Command
    Command(arguments, configuration).run()


def build_sub_commands(subparsers):
    pkgpath = os.path.dirname(commands.__file__)
    pkgs = pkgutil.iter_modules([pkgpath])
    for _, name, _ in pkgs:
        pkg = __import__('commands.' + name, globals(), locals(), ['Command'], 0)
        cmd = pkg.Command()
        pkg_parser = subparsers.add_parser(name, description=cmd.description)
        pkg_parser.set_defaults(func=cmd.run)


def build_argument_parser():
    """
    Generate the argument parser for the manager using Python ArgumentParser
    """
    
    main_parser = argparse.ArgumentParser(
        description='Manager that spins up plugins, tutors, and web services.')
    main_parser.add_argument('--version', action='version', 
        version=settings.HPIT_VERSION)

    subparsers = main_parser.add_subparsers(title='Sub-Commands')

    add_parser = create_command(subparsers, 'add', 
        "Add a new HPIT entity.", add_entity)
    remove_parser = create_command(subparsers, 'remove', 
        "Remove an entity by name.", remove_entity)

    build_sub_commands(subparsers)

    add_parser.add_argument('--count', type=int, 
                        help="The number of entities to create. Will append '.N' to the name.")

    status_parser = subparsers.add_parser('status', description='Status of HPIT System')
    status_parser.set_defaults(func=status)

    start_parser = subparsers.add_parser('start', description='Bring all entities online.')
    start_parser.set_defaults(func=start)

    stop_parser = subparsers.add_parser('stop', description='Take all entities offline.')
    stop_parser.set_defaults(func=stop)

    return main_parser


def run_manager():
    """
    Replaces the old main entry point
    """
    
    configuration = read_configuration()
    main_parser = build_argument_parser()
    arguments = main_parser.parse_args()

    try:
        arguments.func(arguments, configuration)
    except AttributeError:
        main_parser.print_help()

    write_configuration(configuration)
    
    
def wind_down_all(entity_type, configuration):
    """
    Stop all entities of a certain type
    """
    
    entity_collection = get_entity_collection(entity_type, configuration)
    wind_down_collection(entity_type, entity_collection)
    




