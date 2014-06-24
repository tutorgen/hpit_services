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
from tutors import ExampleTutor, KnowledgeTracingTutor
from tutors import StudentActivityLoggingTutor

#import plugins
from plugins import ExamplePlugin, DataStoragePlugin, KnowledgeTracingPlugin
from plugins import ProblemManagementPlugin, ProblemStepManagementPlugin
from plugins import SkillManagementPlugin, StudentManagementPlugin
from plugins import StudentActivityLoggingPlugin

 
main_parser = argparse.ArgumentParser(
    description='ExampleTutor/KnowledgeTracingTutor for HPIT.')
main_parser.add_argument('--version', action='version', 
    version='(HPIT) Example Tutor(version 0.0.1) - Codename Alphalpha')
main_parser.add_argument('name', type=str, help="Name of the tutor.")
main_parser.add_argument('type', type=str, help="The type of Tutor.")
main_parser.add_argument('--once', action='store_true', help="Only run one loop of the tutor.")
main_parser.add_argument('--daemon', action='store_true', help="Daemonize the tutor.")
main_parser.add_argument('--pid', type=str, help="The location of the pid file.")
main_parser.add_argument('--entity', type=str, help="Either 'tutor' or 'plugin'.")
main_parser.add_argument('--args', type=str, help = "JSON string of command line arguments.")


random.seed(datetime.now())

tutor_types = ['example', 'knowledge_tracing', 'activity_logging']

plugin_types = [
    'example', 
    'knowledge_tracing', 
    'skill', 
    'student', 
    'problem',
    'problem_step',
    'data',
    'activity_logging']

if __name__ == '__main__':
    arguments = main_parser.parse_args()

    logger_path = os.path.join(os.getcwd(), 'log/'+arguments.entity+'_' + arguments.name + '.log')
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
            'activity_logging': StudentActivityLoggingPlugin,
        }
        tutor_classes = {
            'example': ExampleTutor,
            'knowledge_tracing': KnowledgeTracingTutor,
            'activity_logging': StudentActivityLoggingTutor,
        }
        if arguments.entity == 'plugin':
            if entity_subtype not in plugin_classes.keys():
                raise Exception("Internal Error: Plugin type not supported.")
        elif arguments.entity == 'tutor':
            if entity_subtype not in tutor_classes.keys():
                raise Exception("Internal Error: Tutor type not supported.")
        #logger = logging.getLogger(__name__)
        entity = None
        if arguments.entity == 'plugin':
            entity = plugin_classes[entity_subtype](arguments.name, logger=logger, args = arguments.args)
            entity.start()
        elif arguments.entity == 'tutor':
            entity = tutor_classes[entity_subtype](arguments.name, logger=logger,run_once=run_once, args = arguments.args)
            entity.start()
        
    if arguments.daemon:
        daemon = Daemonize(app=arguments.name, pid=pid, action=main)
        daemon.start()
    else:
        main()
