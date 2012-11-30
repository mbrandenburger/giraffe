__author__ = 'marcus'
import simplejson as json
import jsonutils

class MeterMessage(object):
    def __init__(self):
        self("","","")

    def __init__(self, signature, hostMessage, instanceMessages):
        self.signature = signature
        self.hostMessage = hostMessage
        self.instanceMessages = instanceMessages

class MeterHostMessage(object):
    def __init__(self):
        self.hostID = ""
        self.meters = []

class MeterInstanceMessage(object):
    def __init__(self):
        self.instanceID = ""
        self.projectID = ""
        self.userID = ""
        self.meters = []

class MeterRecordMessage(object):

    def __init__(self, type = "", value = "", duration = 0):
        self.type = type
        self.value = value
        self.duration = duration

    def buildString(self):
        return {
            "type": self.type,
            "value": self.value,
            "duration": self.duration,
                }

messwert = MeterRecordMessage("CPU_AVG", 1.4, 60)
messwert_string = messwert.buildString()
print messwert_string

primitiv = jsonutils.to_primitive(messwert)
print jsonutils.dumps(messwert)



#
#hostMessage = MeterHostMessage
#hostMessage.hostID = "Macbook"
#hostMessage.meters = None

#message = MeterMessage("hallo", hostMessage, None)
#print message.signature

#print json.dumps([message.__dict__])

