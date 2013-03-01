__author__ = 'mbrandenburger, fbahr'

import logging
# import threading
from multiprocessing import Process, active_children
import time
from giraffe.service.collector import Collector
from giraffe.service.rest_api import Rest_API

logger = logging.getLogger("service")


class Service(object):

    def __init__(self):
        self.collector = Collector()
        self.rest_api = Rest_API()

        # self.threads = []
        # self.threads.append(self.collector)
        # self.threads.append(self.rest_api)

        self.subprocesses = []
        self.subprocesses.append(Process(target=self.collector.run))
        self.subprocesses.append(Process(target=self.rest_api.run))

    def launch(self):
        try:
            # for t in self.threads:
            #     t.start()
            #
            # num_threads = len(self.threads)
            # while threading.active_count() > num_threads:
            #     time.sleep(0.1)

            for process in self.subprocesses:
                process.start()

            num_processes = len(self.subprocesses)
            while active_children() >= num_processes:
                time.sleep(0.1)

        except KeyboardInterrupt:
            logger.info("Ctrl-c received! Sending stop service")
            # for t in self.threads:
            #     t.stop()
            for process in self.subprocesses:
                process.terminate()
                process.join()

        except:
            logger.exception("Error: unable to start thread")

        finally:
            logger.info("Exiting Service")
