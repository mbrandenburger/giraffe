__author__ = 'marcus'

import time
import logging

from daemon import runner

class App():

    def __init__(self, logger):
        self.logger = logger
        self.pidfile_path = '/tmp/testdaemon.pid'
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_timeout = 5


def run(self):
        while True:
            self.logger.info("Hallo")
            time.sleep(10)



logger = logging.getLogger("TestDaemonLogger")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("/tmp/log/daemon/daemon.log")
handler.setFormatter(formatter)
logger.addHandler(handler)

app = App(logger)

daemon_runner = runner.DaemonRunner(app)
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()