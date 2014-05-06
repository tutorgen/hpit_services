#The tutor interacts with HPIT by submitting transaction request
#Tutors send messages in the form of JSON, consisting of two parameters:
#   name: string -- A period delimited name for the message.
#   payload: Object -- The message payload.
# Specialized web APIs can be built on top of this architecture later on.
import argparse
import logging
import os
import random
import uuid
from datetime import datetime
from time import sleep
from daemonize import Daemonize

from plugins import ExamplePlugin, DataStoragePlugin, KnowledgeTracingPlugin
from plugins import ProblemManagementPlugin, ProblemStepManagementPlugin
from plugins import SkillManagementPlugin, StudentManagementPlugin

pid = ''.join(["tmp/plugin_", str(uuid.uuid4()), ".pid"])

random.seed(datetime.now())

plugin_types = [
    'example', 
    'knowledge_tracing', 
    'skill', 
    'student', 
    'problem',
    'problem_step',
    'data']

main_parser = argparse.ArgumentParser(
    description='Example HPIT Plugin / Knowledge Tracing.')
main_parser.add_argument('--version', action='version', 
    version='(HPIT) Example Plugin(version 0.0.1) - Codename Aluminium')
main_parser.add_argument('name', type=str, help="Name of the plugin.")
main_parser.add_argument('type', type=str, help="The type of plugin.")
main_parser.add_argument('--daemon', action='store_true', help="Daemonize the plugin.")
main_parser.add_argument('--pid', type=str, help="The location of the pid file.")

if __name__ == '__main__':
    arguments = main_parser.parse_args()

    logger_path = os.path.join(os.getcwd(), 'log/plugin_' + arguments.name + '.log')

    if arguments.pid:
        pid = arguments.pid

        if not os.path.isabs(pid):
            pid = os.path.join(os.getcwd(), pid)

    plugin_type = arguments.type

    if plugin_type not in plugin_types:
        raise ValueError("Invalid Example Plugin Type. Choices are: " + repr(plugin_types))

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
        }

        if plugin_type not in plugin_classes.keys():
            raise Exception("Internal Error: Plugin type not supported.")

        logger = logging.getLogger(__name__)
        plugin = plugin_classes[plugin_type](arguments.name, logger)
        plugin.start()

    if arguments.daemon:
        daemon = Daemonize(app=arguments.name, pid=pid, action=main)
        daemon.start()
    else:
        main()
