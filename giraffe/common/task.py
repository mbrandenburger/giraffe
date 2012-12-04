__author__ = 'marcus'


import threading

class Task(object):

    def __init__(self, timerInterval):
        self.timerInterval = timerInterval
        self.isRunning = False
        self.callbacks = []

    def __init__(self, timerInterval, callback):
#        (Marcus) TODO:
#       Hier den Konstruktor aufrufen, geht leider nicht
#
#        self.__init__(timerInterval)
        self.timerInterval = timerInterval
        self.isRunning = False
        self.callbacks = []

        self.registerCallback(callback)

    def registerCallback(self, listener):
        self.callbacks.append(listener)

    def notifyCallback(self,param):
        for listener in self.callbacks:
            listener(param)

    def run(self):
        pass

class Launcher(object):

    def __init__(self, service):
        self.requestStop = False
        self.service = service
        self.start()

    def start(self):
        self.requestStop = False
        self.run()

    def requestStop(self):
        self.requestStop = True

    def run(self):
        self.service.isRunning = True
        returnValue = self.service.run()
        self.service.notifyCallback(returnValue)
        if self.requestStop == False and self.service.timerInterval > 0:
            threading.Timer(self.service.timerInterval,self.run).start()
        else:
            self.service.isRunning = False