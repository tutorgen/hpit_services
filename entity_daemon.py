import argparse
import logging
import os
import random
import uuid
from datetime import datetime
from time import sleep
import sys

import platform
if platform.system() != "Windows":
    from daemonize import Daemonize
    
#import tutors
from tutors import ExampleTutor, KnowledgeTracingTutor,ReplayTutor

#import plugins
from plugins import ExamplePlugin, DataStoragePlugin, KnowledgeTracingPlugin
from plugins import ProblemManagementPlugin, ProblemStepManagementPlugin
from plugins import SkillManagementPlugin, StudentManagementPlugin
from plugins import HintFactoryPlugin

random.seed(datetime.now())

tutor_types = ['example', 'knowledge_tracing','replay']

plugin_types = [
    'example', 
    'knowledge_tracing', 
    'skill', 
    'student', 
    'problem',
    'problem_step',
    'data',
    'hint_factory']

subtype_help = "The sub type of entity. tutor=(" + ', '.join(tutor_types) + ") plugin=(" + ', '.join(plugin_types) + ")"

main_parser = argparse.ArgumentParser(
    description='Entity creation daemonizer for HPIT Tutors and PluginsHPIT.',
    usage=argparse.SUPPRESS)
main_parser.add_argument('--version', action='version', 
    version='(HPIT) Example Tutor(version 0.0.1) - Codename Alphalpha')
main_parser.add_argument('entity_id', type=str, help="The entity ID of the entity.")
main_parser.add_argument('api_key', type=str, help="The API Key for the entity.")
main_parser.add_argument('entity', type=str, help="The type of entity. (tutor, plugin)")
main_parser.add_argument('type', type=str, help=subtype_help)
main_parser.add_argument('--once', action='store_true', help="Only run one loop of the tutor.")
main_parser.add_argument('--daemon', action='store_true', help="Daemonize the tutor.")
main_parser.add_argument('--pid', type=str, help="The location of the pid file.")
main_parser.add_argument('--args', type=str, help = "JSON string of command line arguments.")


if __name__ == '__main__':

    main_parser.print_help()

    arguments = main_parser.parse_args()

    logger_path = os.path.join(os.getcwd(), 'log/'+arguments.entity+'_' + arguments.entity_id + '.log')
    pid = ''.join(["tmp/"+arguments.entity+"_", str(uuid.uuid4()), ".pid"])
    
    if arguments.pid:
        pid = arguments.pid

        if not os.path.isabs(pid):
            pid = os.path.join(os.getcwd(), pid)

    run_once = False
    if arguments.once:
        run_once = True

    entity_subtype = arguments.type
    
    if arguments.entity == 'plugin':
        if entity_subtype not in plugin_types:
            raise ValueError("Invalid Example Plugin Type. Choices are: " + repr(plugin_types))
    elif arguments.entity == 'tutor':
        if entity_subtype not in tutor_types:
            raise ValueError("Invalid Example Tutor Type. Choices are: " + repr(tutor_types))
    else:
        raise ValueError("Invalid entity argument:  must be tutor or plugin.")
    
    def main():
        
        logging.basicConfig(
            filename=logger_path,
            level=logging.DEBUG,
            propagate=False,
            format='%(asctime)s %(levelname)s:----:%(message)s', 
            datefmt='%m/%d/%Y %I:%M:%S %p')

        logger = logging.getLogger(__name__)

        plugin_classes = {
            'example': ExamplePlugin,
            'knowledge_tracing': KnowledgeTracingPlugin,
            'student': StudentManagementPlugin,
            'skill': SkillManagementPlugin,
            'problem': ProblemManagementPlugin,
            'problem_step': ProblemStepManagementPlugin,
            'data': DataStoragePlugin,
            'hint_factory' : HintFactoryPlugin
        }
        tutor_classes = {
            'example': ExampleTutor,
            'knowledge_tracing': KnowledgeTracingTutor,
            'replay' : ReplayTutor,
        }
        
        if arguments.entity == 'plugin':
            if entity_subtype not in plugin_classes.keys():
                raise Exception("Internal Error: Plugin type not supported.")
        elif arguments.entity == 'tutor':
            if entity_subtype not in tutor_classes.keys():
                raise Exception("Internal Error: Tutor type not supported.")

        logger = logging.getLogger(__name__)
        
        entity = None
        if arguments.entity == 'plugin':
            entity = plugin_classes[entity_subtype](arguments.entity_id, arguments.api_key, logger, args = arguments.args)
            entity.start()
        elif arguments.entity == 'tutor':
            entity = tutor_classes[entity_subtype](arguments.entity_id, arguments.api_key, logger=logger, run_once=run_once, args = arguments.args)
            entity.start()
        
        if platform.system() == "Windows": #remove PID if process finishes on its own
            os.remove(pid)
            
    if arguments.daemon:
        daemon = Daemonize(app=arguments.entity_id, pid=pid, action=main)
        daemon.start()
    else:
        main()

