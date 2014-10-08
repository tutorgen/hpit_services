import argparse
import logging
import os
import random
import signal
import uuid
from datetime import datetime

import platform
if platform.system() != "Windows":
    from daemonize import Daemonize

from environment.settings_manager import SettingsManager

try:
    settings_manager = SettingsManager.init_instance(os.environ['HPIT_ENV'])
except KeyError:
    settings_manager = SettingsManager.init_instance('debug')

from hpitclient.settings import HpitClientSettings
settings = HpitClientSettings.settings()
settings.HPIT_URL_ROOT = 'http://127.0.0.1:8000'

#import tutors and plugins
from tutors import *
from plugins import *

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
    'student_management']

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


class BaseDaemon:

    def __init__(self, entity_type, entity_subtype, entity_id, api_key, run_once, args, pid):
        self.entity_type = entity_type
        self.entity_subtype = entity_subtype
        self.entity_id = entity_id
        self.api_key = api_key
        self.run_once = run_once
        self.args = args
        self.pid = pid


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
            'student_management': StudentManagementPlugin
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


class PosixDaemon(BaseDaemon):

    def __init__(self, entity_type, entity_subtype, entity_id, api_key, run_once=False, args=None, pid=None):
        super().__init__(entity_type, entity_subtype, entity_id, api_key, run_once, args, pid)

    def _main(self):
        logging.basicConfig(
            filename=logger_path,
            level=logging.DEBUG,
            propagate=False,
            format='%(asctime)s %(levelname)s:----:%(message)s', 
            datefmt='%m/%d/%Y %I:%M:%S %p')

        self.logger = logging.getLogger(__name__)

        try:
            self.entity = self.get_entity_class()
        except Exception as e:
            self.logger.error(str(e))

        if self.entity:
            signal.signal(signal.SIGTERM, self.entity.disconnect)
            self.entity.start()

    def start(self):
        if not self.pid:
            self._main()
        else:
            daemon = Daemonize(app=self.entity_id, pid=self.pid, action=self._main)
            daemon.start()


class WindowsDaemon(BaseDaemon):

    def __init__(self, entity_type, entity_subtype, entity_id, api_key, run_once=False, args=None, pid=None):
        super().__init__(entity_type, entity_subtype, entity_id, api_key, run_once, args, pid)

    def _main(self):
        logging.basicConfig(
            filename=logger_path,
            level=logging.DEBUG,
            propagate=False,
            format='%(asctime)s %(levelname)s:----:%(message)s', 
            datefmt='%m/%d/%Y %I:%M:%S %p')

        self.logger = logging.getLogger(__name__)

        try:
            self.entity = self.get_entity_class()
        except Exception as e:
            self.logger.debug(str(e))
        
        if self.entity:
            signal.signal(signal.SIGTERM, self.entity.disconnect)
            self.entity.start()

        os.remove(pid)

    def start(self):
        self._main()


if __name__ == '__main__':

    main_parser.print_help()

    arguments = main_parser.parse_args()

    logger_path = os.path.join(os.getcwd(), 'log/'+arguments.entity+'_' + arguments.entity_id + '.log')
    pid = ''.join(["tmp/"+arguments.entity+"_", str(uuid.uuid4()), ".pid"])
    
    if arguments.pid:
        pid = arguments.pid

        if not os.path.isabs(pid):
            pid = os.path.join(os.getcwd(), pid)

    entity_subtype = arguments.type
    
    if arguments.entity == 'plugin':
        if entity_subtype not in plugin_types:
            raise ValueError("Invalid Example Plugin Type. Choices are: " + repr(plugin_types))
    elif arguments.entity == 'tutor':
        if entity_subtype not in tutor_types:
            raise ValueError("Invalid Example Tutor Type. Choices are: " + repr(tutor_types))
    else:
        raise ValueError("Invalid entity argument:  must be tutor or plugin.")

    if platform.system() == "Windows":
        daemon = WindowsDaemon(arguments.entity, entity_subtype, arguments.entity_id, arguments.api_key, arguments.once, arguments.args, pid)
        daemon.start()
    elif arguments.daemon:
        daemon = PosixDaemon(arguments.entity, entity_subtype, arguments.entity_id, arguments.api_key, arguments.once, arguments.args, pid)
        daemon.start()
    else:
        #Not passing the PID file causes this to run normally (not daemonized)
        not_daemon = PosixDaemon(arguments.entity, entity_subtype, arguments.entity_id, arguments.api_key, arguments.once, arguments.args)
        not_daemon.start()

