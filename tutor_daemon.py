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
import platform
if platform.system() != "Windows":
    from daemonize import Daemonize

from client import Tutor

pid = ''.join(["tmp/tutor_", str(uuid.uuid4()), ".pid"])

random.seed(datetime.now())

tutor_types = ['example', 'knowledge_tracing']

main_parser = argparse.ArgumentParser(
    description='ExampleTutor/KnowledgeTracingTutor for HPIT.')
main_parser.add_argument('--version', action='version', 
    version='(HPIT) Example Tutor(version 0.0.1) - Codename Alphalpha')
main_parser.add_argument('name', type=str, help="Name of the tutor.")
main_parser.add_argument('type', type=str, help="The type of Tutor.")
main_parser.add_argument('--once', action='store_true', help="Only run one loop of the tutor.")
main_parser.add_argument('--daemon', action='store_true', help="Daemonize the tutor.")
main_parser.add_argument('--pid', type=str, help="The location of the pid file.")


class ExampleTutor(Tutor):
    def __init__(self, name, logger=None, run_once=None):
        super().__init__(name, self.main_callback)
        self.run_once = run_once
        self.logger = logger
        self.event_names = [
            'test', 'example', 'add_student', 
            'remove_student', 'trace']

    def setup(self):
        pass

    def shutdown(self):
        pass

    def main_callback(self):
        event = random.choice(self.event_names)

        logger = logging.getLogger(__name__)
        logger.debug("Sending a random event: " + event)
        response = self.send(event, {'test': 1234})
        logger.debug("RECV: " + str(response))

        sleep(1)

        if self.run_once:
            return False
        else:
            return True

    def run(self):
        self.connect()
        self.setup()
        self.start()
        self.shutdown()
        self.disconnnect()



class KnowledgeTracingTutor(Tutor):
    def __init__(self, name, logger, run_once=None):
        super().__init__(name, self.main_callback, run_once=run_once)
        self.run_once = run_once
        self.logger = logger
        self.skills = ['addition', 'subtraction', 'multiplication', 'division']

    def setup(self):
        for sk in self.skills:
            self.send('kt_set_initial', {
                'skill': sk,
                'probability_known': random.randint(0, 1000) / 1000.0,
                'probability_learned': random.randint(0, 1000) / 1000.0,
                'probability_guess': random.randint(0, 1000) / 1000.0,
                'probability_mistake': random.randint(0, 1000) / 1000.0,
                }, self.initial_response_callback)

    def shutdown(self):
        for sk in self.skills:
            self.send('kt_reset', {
                'skill': sk,
                })

    def main_callback(self):
        for sk in self.skills:
            if 90 < random.randint(0, 100):
                correct = random.randint(0, 100)

                self.send('kt_trace', {
                    'skill': sk,
                    'correct': True if 50 < random.randint(0, 100) else False
                    }, self.trace_response_callback)

        sleep(1)

        return True

    def trace_response_callback(self, response):
        self.logger.debug("RECV: kt_trace response recieved. " + str(response))

    def initial_response_callback(self, response):
        self.logger.debug("RECV: kt_set_initial response recieved. " + str(response))

    def run(self):
        self.connect()
        self.setup()
        self.start()
        self.shutdown()
        self.disconnect()



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

        if tutor_type == "example":
            ExampleTutor(arguments.name, logger=logger, run_once=run_once).run()
        elif tutor_type == "knowledge_tracing":
            KnowledgeTracingTutor(arguments.name, logger=logger, run_once=run_once).run()
        else:
            raise Exception("Internal Error: Tutor type not supported.")

    if arguments.daemon:
        daemon = Daemonize(app=arguments.name, pid=pid, action=main)
        daemon.start()
    else:
        main()
