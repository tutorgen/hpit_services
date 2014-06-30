import os

from clint.textui import puts, colored

from gears.environment import Environment
from gears.assets import build_asset
from gears.finders import FileSystemFinder
from gears.exceptions import FileNotFound

class Command:
    description = "Remove an HPIT entity from the configuration."

    def __init__(self, manager, parser):
        self.manager = manager

        parser.add_argument('type', metavar='type', type=str, 
                            choices=['plugin', 'tutor', 'service'], 
                            help='A plugin, tutor or service entity.')
        parser.add_argument('id', type=str, 
                            help="The entity ID registered in HPIT. (default=example)")


    def get_entity_collection(self, entity_type, configuration):
        """
        Get a collection of entities based on its name, from a given configuration.
        """

        plural = entity_type + 's'

        things = []
        if plural in configuration:
            things = configuration[plural]

        return things
        
        
    def set_entity_collection(self, entity_type, configuration, collection):
        """
        Set the collection of similar entities in a configuration
        """

        plural = entity_type + 's'
        configuration[plural] = collection
       

    def run(self, arguments, configuration):
        self.arguments = arguments
        self.configuration = configuration

        entity_type = arguments.type
        entity_id = arguments.id

        things = self.get_entity_collection(entity_type, configuration)

        things_to_keep = [x for x in things if 'entity_id' in x and x['entity_id'] != entity_id]
        things_to_remove = [x for x in things if 'entity_id' in x and x['entity_id'] == entity_id]

        self.set_entity_collection(entity_type, configuration, things_to_keep)

        if self.manager.server_is_running():
            self.manager.wind_down_collection(things_to_remove)
