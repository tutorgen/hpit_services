#The tutor interacts with HPIT by submitting transaction request
#Tutors send messages in the form of JSON, consisting of two parameters:
#   name: string -- A period delimited name for the message.
#   payload: Object -- The message payload.
# Specialized web APIs can be built on top of this architecture later on.
import argparse
import os
import random
import uuid
from datetime import datetime
from time import sleep
from daemonize import Daemonize
from lib import Plugin

pid = ''.join(["tmp/plugin_", str(uuid.uuid4()), ".pid"])

random.seed(datetime.now())

plugin_types = ['example', 'knowledge_tracing']

main_parser = argparse.ArgumentParser(
    description='Example HPIT Plugin / Knowledge Tracing.')
main_parser.add_argument('--version', action='version', 
    version='(HPIT) Example Plugin(version 0.0.1) - Codename Aluminium')
main_parser.add_argument('name', type=str, help="Name of the plugin.")
main_parser.add_argument('type', type=str, help="The type of plugin.")
main_parser.add_argument('--daemon', action='store_true', help="Daemonize the plugin.")
main_parser.add_argument('--pid', type=str, help="The location of the pid file.")

#def example_tutor_callback(tutor):
#    event = random.choice(event_names)
#
#    print("Sending a random event: " + event)
#    response = tutor.send(event, {'test': 1234})
#    print("RECV: " + str(response.status_code) + " " + response.text)

def test_plugin_callback(*args, **kwargs):
    print("TEST")

def example_plugin_callback(*args, **kwargs):
    print("EXAMPLE")

if __name__ == '__main__':
    arguments = main_parser.parse_args()

    if arguments.pid:
        pid = arguments.pid

        if not os.path.isabs(pid):
            pid = os.path.join(os.getcwd(), pid)

    plugin_type = arguments.type

    if plugin_type not in plugin_types:
        raise ValueError("Invalid Example Plugin Type. Choices are: " + repr(plugin_types))

    def main():
        plugin = Plugin(arguments.name)
        plugin.subscribe(
            test=test_plugin_callback, 
            example=example_plugin_callback)
        plugin.start()

    if arguments.daemon:
        daemon = Daemonize(app=arguments.name, pid=pid, action=main)
        daemon.start()
    else:
        main()
