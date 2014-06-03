import argparse
import json
import subprocess
import os
import signal

from server.settings import HPIT_PID_FILE

DETACHED_PROCESS = 8 #code for windows subprocess

def spin_up_all(entity_type, configuration):
    """
    Start all entities of a given type, as specified in configuration
    """
    
    entity_collection = get_entity_collection(entity_type, configuration)

    for item in entity_collection:
        if not item['active']:
            item['active'] = True
            name = item['name']
            entity_subtype = item['type']
            print("Starting entity: " + name)
            filename = get_entity_py_file(entity_type, item['type'])
            pidfile = get_entity_pid_file(entity_type, name)
            
            if entity_type == 'tutor':
                subp = subprocess.Popen(["python", "tutor_daemon.py", "--pid", pidfile, name, entity_subtype], creationflags=DETACHED_PROCESS, stderr = subprocess.STDOUT)
                with open(pidfile,"w") as pfile:
                    pfile.write(str(subp.pid))
            elif entity_type == 'plugin':
                subp = subprocess.Popen(["python", "plugin_daemon.py", "--pid", pidfile, name, entity_subtype], creationflags=DETACHED_PROCESS, stderr = subprocess.STDOUT)
                with open(pidfile,"w") as pfile:
                    pfile.write(str(subp.pid))
            else:
                print("ERROR: UNKNOWN ENTITY TYPE")


def wind_down_collection(entity_type, entity_collection):
    """
    Shut down all entities of a given type from a collection
    """
    
    for item in entity_collection:
        if item['active']:
            item['active'] = False
            name = item['name']
            print("Stopping entity: " + name)
            pidfile = get_entity_pid_file(entity_type, name)

            try:
                with open(pidfile) as f:
                    pid = f.read()
                    os.kill(int(pid), signal.SIGTERM)

                os.remove(pidfile)
            except FileNotFoundError:
                print("Error: Could not find PIDfile for entity: " + name)


def start(arguments, configuration):
    """
    Start the hpit server, tutors, and plugins as specified in configuration
    """
    
    if not os.path.exists('tmp'):
        os.makedirs('tmp')

    if not os.path.exists('log'):
        os.makedirs('log')

    if server_is_running():
        print("The HPIT Server is already running.")
    else:
        print("Starting the HPIT Hub Server for Windows...")
        subp = subprocess.Popen(["python", "server_wrapper.py", "--pid", HPIT_PID_FILE], creationflags=DETACHED_PROCESS)
        with open(HPIT_PID_FILE,"w") as pfile:
            pfile.write(str(subp.pid))
        print("Starting tutors...")
        spin_up_all('tutor', configuration)
        print("Starting plugins...")
        spin_up_all('plugin', configuration)
    print("DONE!")


def stop(arguments, configuration):
    """
    Stop the hpit server, plugins, and tutors.
    """
    
    if server_is_running():
        print("Stopping plugins...")
        wind_down_all('plugin', configuration)
        print("Stopping tutors...")
        wind_down_all('tutor', configuration)

        print("Stopping the HPIT Hub Server...")
        with open(HPIT_PID_FILE) as f:
            pid = f.read()
            os.kill(int(pid), signal.SIGTERM)
        os.remove(HPIT_PID_FILE)
    else:
        print("The HPIT Server is not running.")
    print("DONE!")
    
    

    
from common_manager import *

