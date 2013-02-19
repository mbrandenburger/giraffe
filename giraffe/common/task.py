__author__ = 'marcus'

from threading import Thread, Timer


class Task(Thread):

    def __init__(self, callback):
        Thread.__init__(self)

        self.isRunning = False
        self.requestStop = False
        self.callbacks = []

        self.registerCallback(callback)

    def registerCallback(self, listener):
        self.callbacks.append(listener)

    def notifyCallback(self, param):
        for listener in self.callbacks:
            listener(param)

    def run(self):
        pass

    def stop(self):
        self.isRunning = False
        self.requestStop = False
        self.callbacks = []
        self._Thread__stop()


class PeriodicMeterTask(Task):

    def __init__(self, callback, period):
        Task.__init__(self, callback)
        self.period = period
        self.timer = None

    def run(self):
        meter_msg = self.meter()
        self.notifyCallback(meter_msg)

        if not self.requestStop:
            self.timer = Timer(self.period, self.run)
            self.timer.start()
        else:
            self.isRunning = False

    def stop(self):
        self.timer.cancel()
        Task.stop(self)

    def meter(self):
        pass


# class PeriodicTaskLauncher(Task):
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
#    def run(self):
#        self.service.isRunning = True
#        returnValue = self.service.run()
#        self.service.notifyCallback(returnValue)
#
#        if not self.requestStop and self.service.timerInterval > 0:
#            Timer(self.service.timerInterval, self.run).start()
#        else:
#            self.service.isRunning = False
#
#    def requestStop(self):
#        self.requestStop = True
