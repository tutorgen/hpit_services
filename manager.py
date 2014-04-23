import argparse
import json
import subprocess
import os
import signal

def read_configuration():
    try:
        with open('configuration.json', 'r') as f:
            return json.loads(''.join(f.readlines()))
    except FileNotFoundError:
        return {}

def write_configuration(configuration):
    with open('configuration.json', 'w') as f:
        f.write(json.dumps(configuration, indent=4))

def create_entity(*args, **kwargs):
    print("Create")
    print(args, kwargs)

def destroy_entity(*args, **kwargs):
    print("Destory")
    print(args, kwargs)

def up_entity(*args, **kwargs):
    print("Up")
    print(args, kwargs)

def down_entity(*args, **kwargs):
    print("Down")
    print(args, kwargs)

def start(*args, **kwargs):
    if os.path.isfile("hpit_pid"):
        print("The HPIT Server is already running.")
    else:
        print("Starting the HPIT Hub Server...")
        subprocess.call(["gunicorn", "hpit:app", "--daemon", "--pid", "hpit_pid"])
    print("DONE!")

def stop(*args, **kwargs):
    if os.path.isfile('hpit_pid'):
        print("Stopping the HPIT Hub Server...")
        with open('hpit_pid') as f:
            pid = f.read()
            os.kill(int(pid), signal.SIGTERM)
            os.remove('hpit_pid')
    else:
        print("The HPIT Server is not running.")
    print("DONE!")

def status(*args, **kwargs):
    print("Status is...")
    if os.path.isfile('hpit_pid'):
        print("The HPIT Server is running.")
    else:
        print("The HPIT Server it not running.")

def create_command(sub, name, description, func):
    parser = sub.add_parser(name, description=description)
    parser.add_argument('type', metavar='type', type=str, 
                        choices=['plugin', 'tutor', 'service'], 
                        help='A plugin, tutor or service entity.')
    parser.add_argument('name', metavar='name', type=str, 
                        help="Indentifying name for the entity.")
    parser.add_argument('--class', type=str, 
                        help="The class of the entity. (default=example)")
    parser.set_defaults(func=func)

    return parser

def build_argument_parser():
    main_parser = argparse.ArgumentParser(
        description='Manager that spins up plugins, tutors, and web services.')
    main_parser.add_argument('--version', action='version', 
        version='(HPIT) Hyper Personalized Intelligent Tutor(version 0.2) - Codename Asura')

    subparsers = main_parser.add_subparsers(title='Sub-Commands')

    create_parser = create_command(subparsers, 'create', 
        "Create a new HPIT entity.", create_entity)
    destroy_parser = create_command(subparsers, 'destroy', 
        "Destroy an entity.", destroy_entity)
    up_parser = create_command(subparsers, 'up', 
        'Spin up an entity.', up_entity)
    down_parser = create_command(subparsers, 'down', 
        'Shutdown an entity.', down_entity)

    create_parser.add_argument('--count', type=int, 
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
        arguments.func(arguments)
    except:
        main_parser.print_help()

    write_configuration(configuration)
