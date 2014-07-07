import os

from clint.textui import puts, colored

from gears.environment import Environment
from gears.assets import build_asset
from gears.finders import FileSystemFinder
from gears.exceptions import FileNotFound

class Command:
    description = "Add a new HPIT entity."

    def __init__(self, manager, parser):
        self.manager = manager

        parser.add_argument('type', metavar='type', type=str, 
                            choices=['plugin', 'tutor', 'service'], 
                            help='A plugin, tutor or service entity.')
        parser.add_argument('kind', metavar='kind', type=str, 
                            help="Indentifying name for the entity.")
        parser.add_argument('id', type=str, 
                            help="The entity ID registered in HPIT. (default=example)")
        parser.add_argument('api_key', type=str, 
                            help="The api key for this entity. (default=example)")


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
        entity_kind = arguments.kind
        entity_id = arguments.id
        api_key = arguments.api_key

        things = self.get_entity_collection(entity_type, configuration)

        ids_configured = [x['entity_id'] for x in things if 'entity_id' in x]

        if entity_id in ids_configured:
            raise ValueError("Entity already exists in configuration.")

        things.append({
            'entity_id': entity_id,
            'api_key': api_key,
            'type': entity_kind,
            'active': False
            })

        self.set_entity_collection(entity_type, configuration, things)

        if self.manager.server_is_running():
            self.manager.spin_up_all(entity_type, configuration)
