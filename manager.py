import argparse
import json
import subprocess
import os
import signal

from settings import *

def read_configuration():
    try:
        with open('configuration.json', 'r') as f:
            return json.loads(''.join(f.readlines()))
    except FileNotFoundError:
        return {}


def write_configuration(configuration):
    with open('configuration.json', 'w') as f:
        f.write(json.dumps(configuration, indent=4))


def get_entity_collection(entity_type, configuration):
    plural = entity_type + 's'

    things = []
    if plural in configuration:
        things = configuration[plural]

    return things


def set_entity_collection(entity_type, configuration, collection):
    plural = entity_type + 's'
    configuration[plural] = collection


def get_entity_py_file(entity_type, subtype):
    plural = entity_type + 's'
    return os.path.join(plural, subtype + '.py')


def get_entity_pid_file(entity_type, entity_name):
    return os.path.join('tmp', entity_type + '_' + entity_name + '.pid')


def spin_up_all(entity_type, configuration):
    entity_collection = get_entity_collection(entity_type, configuration)

    for item in entity_collection:
        if not item['active']:
            item['active'] = True
            name = item['name']
            entity_subtype = item['type']
            print("Starting entity: " + name)
            filename = get_entity_py_file(entity_type, item['type'])
            pidfile = get_entity_pid_file(entity_type, name)

            if entity_type == 'tutor':
                subprocess.call(["python3", "tutors_daemon.py", "--daemon", "--pid", pidfile, name, entity_subtype])
            elif entity_type == 'plugin':
                subprocess.call(["python3", "plugin_daemon.py", "--daemon", "--pid", pidfile, name, entity_subtype])
            else:
                print("ERROR: UNKNOWN ENTITY TYPE")



def wind_down_all(entity_type, configuration):
    entity_collection = get_entity_collection(entity_type, configuration)
    wind_down_collection(entity_type, entity_collection)


def wind_down_collection(entity_type, entity_collection):

    for item in entity_collection:
        if item['active']:
            item['active'] = False
            name = item['name']
            print("Stopping entity: " + name)
            pidfile = get_entity_pid_file(entity_type, name)

            try:
                with open(pidfile) as f:
                    pid = f.read()
                    os.kill(int(pid), signal.SIGTERM)

                os.remove(pidfile)
            except FileNotFoundError:
                print("Error: Could not find PIDfile for entity: " + name)


def server_is_running():
    return os.path.isfile(HPIT_PID_FILE)


def add_entity(arguments, configuration):
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


def start(arguments, configuration):
    if not os.path.exists('tmp'):
        os.makedirs('tmp')

    if not os.path.exists('log'):
        os.makedirs('log')

    if server_is_running():
        print("The HPIT Server is already running.")
    else:
        print("Starting the HPIT Hub Server...")
        subprocess.call(["gunicorn", "hpit:app", "--daemon", "--pid", HPIT_PID_FILE])

        print("Starting tutors...")
        spin_up_all('tutor', configuration)
        print("Starting plugins...")
        spin_up_all('plugin', configuration)
    print("DONE!")


def stop(arguments, configuration):
    if server_is_running():
        print("Stopping plugins...")
        wind_down_all('plugin', configuration)
        print("Stopping tutors...")
        wind_down_all('tutor', configuration)

        print("Stopping the HPIT Hub Server...")
        with open(HPIT_PID_FILE) as f:
            pid = f.read()
            os.kill(int(pid), signal.SIGTERM)
        os.remove(HPIT_PID_FILE)
    else:
        print("The HPIT Server is not running.")
    print("DONE!")


def status(arguments, configuration):
    print("Status is...")
    if server_is_running():
        print("The HPIT Server is running.")
    else:
        print("The HPIT Server it not running.")


def create_command(sub, name, description, func):
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


def build_argument_parser():
    main_parser = argparse.ArgumentParser(
        description='Manager that spins up plugins, tutors, and web services.')
    main_parser.add_argument('--version', action='version', 
        version='(HPIT) Hyper Personalized Intelligent Tutor(version 0.2) - Codename Asura')

    subparsers = main_parser.add_subparsers(title='Sub-Commands')

    add_parser = create_command(subparsers, 'add', 
        "Add a new HPIT entity.", add_entity)
    remove_parser = create_command(subparsers, 'remove', 
        "Remove an entity by name.", remove_entity)

    add_parser.add_argument('--count', type=int, 
                        help="The number of entities to create. Will append '.N' to the name.")

    status_parser = subparsers.add_parser('status', description='Status of HPIT System')
    status_parser.set_defaults(func=status)

    start_parser = subparsers.add_parser('start', description='Bring all entities online.')
    start_parser.set_defaults(func=start)

    stop_parser = subparsers.add_parser('stop', description='Take all entities offline.')
    stop_parser.set_defaults(func=stop)

    return main_parser


if __name__ == '__main__':
    configuration = read_configuration()
    main_parser = build_argument_parser()
    arguments = main_parser.parse_args()

    try:
        arguments.func(arguments, configuration)
    except AttributeError:
        main_parser.print_help()

    write_configuration(configuration)
