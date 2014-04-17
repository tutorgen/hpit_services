import argparse

main_parser = argparse.ArgumentParser(
    description='Manager that spins up plugins, tutors, and web services.')

def create_entity(*args, **kwargs):
    print(args, kwargs)

def destroy_entity(*args, **kwargs):
    print(args, kwargs)

def up_entity(*args, **kwargs):
    print(args, kwargs)

def down_entity(*args, **kwargs):
    print(args, kwargs)

def start(*args, **kwargs):
    print(args, kwargs)

def stop(*args, **kwargs):
    print(args, kwargs)

def command_list(*args, **kwargs):
    main_parser.print_help()

def status(*args, **kwargs):
    print(args, kwargs)

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


if __name__ == '__main__':
    main_parser.set_defaults(func=command_list)
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

    status_parser = subparsers.add_parser('status', description='Status of HPIT System')
    status_parser.set_defaults(func=status)

    start_parser = subparsers.add_parser('start', description='Bring all entities online.')
    start_parser.set_defaults(func=start)

    stop_parser = subparsers.add_parser('stop', description='Take all entities offline.')
    stop_parser.set_defaults(func=stop)

    args = main_parser.parse_args()
    print(args)
    args.func(args)