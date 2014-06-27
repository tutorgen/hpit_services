import argparse
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

import platform
if platform.system() != "Windows":
    from daemonize import Daemonize

main_parser = argparse.ArgumentParser(
    description='Script that starts up the HPIT server in a wsgi container.')
main_parser.add_argument('--env', metavar='env', type=str,
    choices=['test', 'debug', 'production'],
    help="The environment to run the container in.")
main_parser.add_argument('--daemon', action='store_true', help="Daemonize the tutor.")
main_parser.add_argument('--pid', type=str, help="The location of the pid file.")

arguments = main_parser.parse_args()

environment = 'debug'

if arguments.env:
    environment = arguments.env

print("Spinning up the server in the " + environment + " environment.")

from server.settings import ServerSettingsManager
settings_manager = ServerSettingsManager.init_instance(environment)

from server.views.api import *
from server.views.dashboard import *
from server.app import ServerApp

def main():
    server_app = ServerApp.get_instance()
    server_app.bootstrap_user()

    http_server = HTTPServer(WSGIContainer(server_app.app))
    http_server.listen(settings_manager.settings.HPIT_BIND_PORT)
    IOLoop.instance().start()

if arguments.daemon:
    pid = 'tmp/hpit_server.pid'
    if arguments.pid:
        pid = arguments.pid

        if not os.path.isabs(pid):
            pid = os.path.join(os.getcwd(), pid)

    daemon = Daemonize(app="hpit_server", pid=pid, action=main)
    daemon.start()
else:
    main()
