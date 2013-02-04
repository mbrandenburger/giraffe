__author__ = 'marcus'

import logging
import threading
import datetime
import time
from flask import Flask

_logger = logging.getLogger("service.flask")

class WebServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.app = Flask(__name__)

        @self.app.route("/")
        def hello():
            return "Hello World!"

    def quit(self):
        try:
            self._Thread__stop()
        except:
            print(str(self.getName()) + ' could not be terminated')

    def run(self):
        self.app.run()


class ThreadClass(threading.Thread):
    def run(self):
        while True:
            now = datetime.datetime.now()
            print "%s says Hello World at time: %s" % (self.getName(), now)
            time.sleep(1)

    def quit(self):
        try:
            self._Thread__stop()
        except:
            print(str(self.getName()) + ' could not be terminated')

if __name__ == '__main__':

    threads = []

    try:
        for i in range(2):
            t = ThreadClass()
            threads.append(t)
            t.start()

        server = WebServer()
        threads.append(server)
        server.start()

        while True:
            now = datetime.datetime.now()
            print "Main ticker: %s" % now
            time.sleep(1)

    except KeyboardInterrupt:
        for t in threads:
            t.quit()

        print 'Keybard Interrupt'

    finally:
        print 'done'





