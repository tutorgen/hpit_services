import argparse
import json
import subprocess
import os
import signal

from server.settings import HPIT_PID_FILE

def read_configuration():
    """
    Read the JSON configuration file and return the config parameters
    """
    
    try:
        with open('configuration.json', 'r') as f:
            return json.loads(''.join(f.readlines()))
    except FileNotFoundError:
        return {}
        
        
def write_configuration(configuration):
    """
    Dump the JSON configuration to a file
    """
    
    with open('configuration.json', 'w') as f:
        f.write(json.dumps(configuration, indent=4))
        
        
def get_entity_collection(entity_type, configuration):
    """
    Get a collection of entities based on its name, from a given configuration.
    """

    plural = entity_type + 's'

    things = []
    if plural in configuration:
        things = configuration[plural]

    return things
    
def set_entity_collection(entity_type, configuration, collection):
    """
    Set the collection of similar entities in a configuration
    """

    plural = entity_type + 's'
    configuration[plural] = collection
    
def get_entity_py_file(entity_type, subtype):
    """
    Get the filename of the source file associated with a tutor/plugin implemetation
    """
    
    plural = entity_type + 's'
    return os.path.join(plural, subtype + '.py')

    
    
    
