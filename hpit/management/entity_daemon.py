import argparse
import logging
from logging.handlers import RotatingFileHandler
import os
import random
import signal
import uuid
from datetime import datetime

import platform

from hpit.management.settings_manager import SettingsManager

try:
    settings_manager = SettingsManager.init_instance(os.environ['HPIT_ENV'])
except KeyError:
    settings_manager = SettingsManager.init_instance('debug')

plugin_settings = SettingsManager.get_plugin_settings()

#import tutors and plugins
from hpit.tutors import *
from hpit.plugins import *

random.seed(datetime.now())

tutor_types = [
    'example', 
    'knowledge_tracing',
    'replay',
    'data_connector',
    'problem_generator',
    'student_model',
    'load_testing'
]

plugin_types = [
    'example', 
    'knowledge_tracing', 
    'skill_management', 
    'student', 
    'problem_generator',
    'problem_management',
    'data',
    'data_connector',
    'hint_factory',
    'student_management',
    'boredom_detector',
    'transaction_management',
]

subtype_help = "The sub type of entity. tutor=(" + ', '.join(tutor_types) + ") plugin=(" + ', '.join(plugin_types) + ")"

main_parser = argparse.ArgumentParser(
    description='Entity bootstrapping engine for HPIT Tutors and PluginsHPIT.',
    usage=argparse.SUPPRESS)
main_parser.add_argument('--version', action='version', 
    version='(HPIT) Example Tutor(version 0.0.1) - Codename Alphalpha')
main_parser.add_argument('entity_id', type=str, help="The entity ID of the entity.")
main_parser.add_argument('api_key', type=str, help="The API Key for the entity.")
main_parser.add_argument('entity', type=str, help="The type of entity. (tutor, plugin)")
main_parser.add_argument('type', type=str, help=subtype_help)
main_parser.add_argument("name", type=str,help="The name of the entity")
main_parser.add_argument('--once', action='store_true', help="Only run one loop of the tutor.")
main_parser.add_argument('--args', type=str, help = "JSON string of command line arguments.")


class BaseDaemon:

    def __init__(self, entity_type, entity_subtype, entity_id, api_key, run_once, args):
        self.entity_type = entity_type
        self.entity_subtype = entity_subtype
        self.entity_id = entity_id
        self.api_key = api_key
        self.run_once = run_once
        self.args = args

    def get_entity_class(self):
        plugin_classes = {
            'example': ExamplePlugin,
            'knowledge_tracing': KnowledgeTracingPlugin,
            'skill_management': SkillManagementPlugin,
            'problem_generator': ProblemGeneratorPlugin,
            'problem_management': ProblemManagementPlugin,
            'data': DataStoragePlugin,
            'data_connector' : DataShopConnectorPlugin,
            'hint_factory' : HintFactoryPlugin,
            'student_management': StudentManagementPlugin,
            'boredom_detector': BoredomDetectorPlugin,
            'transaction_management': TransactionManagementPlugin,
        }
        tutor_classes = {
            'example': ExampleTutor,
            'knowledge_tracing': KnowledgeTracingTutor,
            'problem_generator': ProblemGeneratorTutor,
            'replay' : ReplayTutor,
            'student_model': StudentModelTutor,
            'load_testing': LoadTestingTutor
        }
        
        if self.entity_type == 'plugin':
            if self.entity_subtype not in plugin_classes.keys():
                raise Exception("Internal Error: Plugin type not supported.")
        elif self.entity_type == 'tutor':
            if self.entity_subtype not in tutor_classes.keys():
                raise Exception("Internal Error: Tutor type not supported.")

        entity = False
        if self.entity_type == 'plugin':
            entity = plugin_classes[entity_subtype](self.entity_id, self.api_key, self.logger, args=self.args)
        elif self.entity_type == 'tutor':
            entity = tutor_classes[entity_subtype](self.entity_id, self.api_key, logger=self.logger, run_once=self.run_once, args=self.args)

        return entity

    def start(self):
               
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        log_handler = RotatingFileHandler(logger_path,maxBytes = 10000000, backupCount = 1) #10mb
        log_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(levelname)s:----:%(message)s')
        log_handler.setFormatter(formatter)
        self.logger.addHandler(log_handler)

        self.logger.debug("Retrieving entity class.")
        try:
            self.entity = self.get_entity_class()
        except Exception as e:
            self.logger.error(str(e))
            raise

        if self.entity:
            self.logger.debug("Entity: " + str(self.entity) + " Found.")
            signal.signal(signal.SIGTERM, self.entity.disconnect)
            self.entity.set_hpit_root_url(plugin_settings.HPIT_URL_ROOT)
            self.entity.start()


if __name__ == '__main__':

    main_parser.print_help()

    arguments = main_parser.parse_args()

    logger_path = os.path.join(os.getcwd(), 'log/'+arguments.name+"_"+arguments.entity+'_' + arguments.entity_id + '.log')

    entity_subtype = arguments.type
   
    if arguments.entity == 'plugin':
        if entity_subtype not in plugin_types:
            raise ValueError("Invalid Example Plugin Type. Choices are: " + repr(plugin_types))
    elif arguments.entity == 'tutor':
        if entity_subtype not in tutor_types:
            raise ValueError("Invalid Example Tutor Type. Choices are: " + repr(tutor_types))
    else:
        raise ValueError("Invalid entity argument:  must be tutor or plugin.")

    daemon = BaseDaemon(arguments.entity, entity_subtype, arguments.entity_id, arguments.api_key, arguments.once, arguments.args)
    daemon.start()

