from time import sleep
from daemonize import Daemonize
from lib.plugin import Plugins

pid = "/tmp/test.pid"

def main():
    while True:
        sleep(5)

daemon = Daemonize(app="test_app", pid=pid, action=main)
daemon.start()