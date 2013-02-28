__author__ = 'marcus'

import logging
import threading
import time
from giraffe.service.collector import Collector
from giraffe.service.rest_api import Rest_API

logger = logging.getLogger("service")

@DeprecationWarning
class Service(object):

    def __init__(self):
        self.collector = Collector()
        self.rest_api = Rest_API()
        self.threads = []

        self.threads.append(self.collector)
        self.threads.append(self.rest_api)

    def launch(self):
        try:
            for t in self.threads:
                t.start()

            while threading.active_count() > 0:
                time.sleep(0.1)

        except KeyboardInterrupt:
            logger.info("Ctrl-c received! Sending stop service")
            for t in self.threads:
                t.stop()

        except:
            logger.exception("Error: unable to start thread")

        finally:
            logger.info("Exiting Service")
