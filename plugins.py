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
from lib import Plugin

pid = ''.join(["tmp/plugin_", str(uuid.uuid4()), ".pid"])

random.seed(datetime.now())

plugin_types = [
    'example', 
    'knowledge_tracing', 
    'skill', 
    'student', 
    'problem']

main_parser = argparse.ArgumentParser(
    description='Example HPIT Plugin / Knowledge Tracing.')
main_parser.add_argument('--version', action='version', 
    version='(HPIT) Example Plugin(version 0.0.1) - Codename Aluminium')
main_parser.add_argument('name', type=str, help="Name of the plugin.")
main_parser.add_argument('type', type=str, help="The type of plugin.")
main_parser.add_argument('--daemon', action='store_true', help="Daemonize the plugin.")
main_parser.add_argument('--pid', type=str, help="The location of the pid file.")

#Example Plugin
def test_plugin_callback(transaction):
    logger = logging.getLogger(__name__)
    logger.debug("TEST")
    logger.debug(transaction)

def example_plugin_callback(transaction):
    logger = logging.getLogger(__name__)
    logger.debug("EXAMPLE")
    logger.debug(transaction)


#Knowledge Tracing Plugin
def knowledge_tracing_callback(transaction):
    logger = logging.getLogger(__name__)
    logger.debug("KNOWLEDGE_TRACING")
    logger.debug(transaction)

def kt_set_initial_callback(transaction):
    logger = logging.getLogger(__name__)
    logger.debug("KT_SET_INITIAL")
    logger.debug(transaction)


#Student Management Plugin
def add_student_callback(transaction):
    logger = logging.getLogger(__name__)
    logger.debug("ADD_STUDENT")
    logger.debug(transaction)

def remove_student_callback(transaction):
    logger = logging.getLogger(__name__)
    logger.debug("REMOVE_STUDENT")
    logger.debug(transaction)

def get_student_callback(transaction):
    logger = logging.getLogger(__name__)
    logger.debug("GET_STUDENT")
    logger.debug(transaction)


#Skill Management Plugin
def add_skill_callback(transaction):
    logger = logging.getLogger(__name__)
    logger.debug("ADD_SKILL")
    logger.debug(transaction)

def remove_skill_callback(transaction):
    logger = logging.getLogger(__name__)
    logger.debug("REMOVE_SKILL")
    logger.debug(transaction)

def get_skill_callback(transaction):
    logger = logging.getLogger(__name__)
    logger.debug("GET_SKILL")
    logger.debug(transaction)



#Problem Management Plugin
def add_problem_callback(transaction):
    logger = logging.getLogger(__name__)
    logger.debug("ADD_PROBLEM")
    logger.debug(transaction)

def remove_problem_callback(transaction):
    logger = logging.getLogger(__name__)
    logger.debug("REMOVE_PROBLEM")
    logger.debug(transaction)

def get_problem_callback(transaction):
    logger = logging.getLogger(__name__)
    logger.debug("GET_PROBLEM")
    logger.debug(transaction)

def add_problem_step_callback(transaction):
    logger = logging.getLogger(__name__)
    logger.debug("ADD_PROBLEM_STEP")
    logger.debug(transaction)

def remove_problem_step_callback(transaction):
    logger = logging.getLogger(__name__)
    logger.debug("REMOVE_PROBLEM_STEP")
    logger.debug(transaction)

def get_problem_step_callback(transaction):
    logger = logging.getLogger(__name__)
    logger.debug("GET_PROBLEM_STEP")
    logger.debug(transaction)

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

        plugin = Plugin(arguments.name)

        if plugin_type == 'example':
            plugin.subscribe(
                test=test_plugin_callback, 
                example=example_plugin_callback)
        elif plugin_type == 'knowledge_tracing':
            plugin.subscribe(
                kt_set_initial=kt_set_initial_callback,
                knowledge_tracing=knowledge_tracing_callback)
        elif plugin_type == 'student':
            plugin.subscribe(
                add_student=add_student_callback,
                remove_student=remove_student_callback,
                get_student=get_student_callback)
        elif plugin_type == 'skill':
            plugin.subscribe(
                add_skill=add_skill_callback,
                remove_skill=remove_skill_callback,
                get_skill=get_skill_callback)
        elif plugin_type == 'problem':
            plugin.subscribe(
                add_problem=add_problem_callback,
                remove_problem=remove_problem_callback,
                get_problem=get_problem_callback,
                add_problem_step=add_problem_step,
                remove_problem_step=remove_problem_step,
                get_problem_step=get_problem_step_callback)
        else:
            raise Exception("Internal Error: Plugin type not supported.")

        plugin.start()

    if arguments.daemon:
        daemon = Daemonize(app=arguments.name, pid=pid, action=main)
        daemon.start()
    else:
        main()
