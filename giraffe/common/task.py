__author__ = 'marcus'


import threading

class Task(threading.Thread):

    def __init__(self, callback):
        threading.Thread.__init__(self)
        self.isRunning = False
        self.requestStop = False
        self.callbacks = []

        self.registerCallback(callback)

    def registerCallback(self, listener):
        self.callbacks.append(listener)

    def notifyCallback(self,param):
        for listener in self.callbacks:
            listener(param)

    def run(self):
        pass

    def stop(self):
        self.isRunning = False
        self.requestStop = False
        self.callbacks = [];
        self._Thread__stop()


class PeriodicMeterTask(Task):

    def __init__(self, callback, period):
        Task.__init__(self, callback)
        self.period = period
        self.timer = None

    def run(self):

        meter_msg = self.meter()
        self.notifyCallback(meter_msg)

        if self.requestStop == False:
            self.timer = threading.Timer(self.period,self.run)
            self.timer.start()
        else:
            self.isRunning = False

    def stop(self):
        self.timer.cancel()
        Task.stop(self)

    def meter(self):
        pass

#class PeriodicTaskLauncher(object):
#
#    def __init__(self, service, duration):
#        self.requestStop = False
#        self.service = service
#        self.start()
#
#    def start(self):
#        self.requestStop = False
#        self.run()
#
#    def requestStop(self):
#        self.requestStop = True
#
#    def run(self):
#        self.service.isRunning = True
#        returnValue = self.service.run()
#        self.service.notifyCallback(returnValue)
#        if self.requestStop == False and self.service.timerInterval > 0:
#            threading.Timer(self.service.timerInterval,self.run).start()
#        else:
#            self.service.isRunning = False
