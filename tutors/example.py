#The tutor interacts with HPIT by submitting transaction request
#Tutors send messages in the form of JSON, consisting of two parameters:
#   name: string -- A period delimited name for the message.
#   payload: Object -- The message payload.
# Specialized web APIs can be built on top of this architecture later on.
import argparse
from time import sleep
from daemonize import Daemonize

pid = "/tmp/test.pid"

def main():
    while True:
        sleep(5)

def send_message():
    pass

main_parser = argparse.ArgumentParser(
    description='Example HPIT Tutor.')
main_parser.add_argument('--version', action='version', 
    version='(HPIT) Example Tutor(version 0.0.1) - Codename Alphalpha')
main_parser.add_argument('name', type=str, help="Name of the tutor.")
main_parser.add_argument('-D', action='store_true', help="Daemonize the tutor.")
main_parser.add_argument('--cycle', type=str, nargs='+', help="Cycle messages event names.")

if __name__ == '__main__':
    arguments = main_parser.parse_args()

    if should_daemonize:
        daemon = Daemonize(app="test_app", pid=pid, action=main)
        daemon.start()
    else:
        send_message()