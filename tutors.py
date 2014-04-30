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
from lib import Tutor

pid = ''.join(["tmp/tutor_", str(uuid.uuid4()), ".pid"])

random.seed(datetime.now())

tutor_types = ['example']
event_names = ['test', 'example', 'add_student', 'remove_student', 'trace']

main_parser = argparse.ArgumentParser(
    description='Example HPIT Tutor.')
main_parser.add_argument('--version', action='version', 
    version='(HPIT) Example Tutor(version 0.0.1) - Codename Alphalpha')
main_parser.add_argument('name', type=str, help="Name of the tutor.")
main_parser.add_argument('type', type=str, help="The type of Tutor.")
main_parser.add_argument('--once', action='store_true', help="Only run one loop of the tutor.")
main_parser.add_argument('--daemon', action='store_true', help="Daemonize the tutor.")
main_parser.add_argument('--pid', type=str, help="The location of the pid file.")

def example_tutor_callback(tutor):
    event = random.choice(event_names)

    logger = logging.getLogger(__name__)
    logger.debug("Sending a random event: " + event)
    response = tutor.send(event, {'test': 1234})
    logger.debug("RECV: " + str(response.status_code) + " " + response.text)

    sleep(1)

    if tutor.run_once:
        return False
    else:
        return True

if __name__ == '__main__':
    arguments = main_parser.parse_args()

    logger_path = os.path.join(os.getcwd(), 'log/tutor_' + arguments.name + '.log')

    if arguments.pid:
        pid = arguments.pid

        if not os.path.isabs(pid):
            pid = os.path.join(os.getcwd(), pid)

    run_once = False
    tutor_type = arguments.type

    if arguments.once:
        run_once = True

    if tutor_type not in tutor_types:
        raise ValueError("Invalid Example Tutor Type. Choices are: " + repr(tutor_types))

    def main():
        logging.basicConfig(
            filename=logger_path,
            level=logging.DEBUG,
            propagate=False,
            format='%(asctime)s %(levelname)s:----:%(message)s', 
            datefmt='%m/%d/%Y %I:%M:%S %p')

        logger = logging.getLogger(__name__)

        callback_name = ''.join([tutor_type, '_tutor_callback'])
        callback = globals()[callback_name]

        tutor = Tutor(arguments.name, callback, run_once=run_once)
        tutor.start()

    if arguments.daemon:
        daemon = Daemonize(app=arguments.name, pid=pid, action=main)
        daemon.start()
    else:
        main()
