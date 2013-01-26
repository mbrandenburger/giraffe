__author__  = 'marcus, fbahr'
__version__ = '0.2'
__date__    = '2012-12-03'

from nova.openstack.common import jsonutils


class MeterMessage(object):
    def __init__(self, signature=None, hostMessage=None, instanceMessages=None):
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
    def __init__(self, type=None, value=0.0, duration=0):
        self.type = type
        self.value = value
        self.duration = duration

    def __repr__(self):
        repr_list = []
        repr_list.append('"type": "%s"'   % self.type)
        repr_list.append('"value": %f'    % self.value)
        repr_list.append('"duration": %d' % self.duration)
        return ', '.join(repr_list).join(['{', '}'])


measurement = MeterRecordMessage("CPU_AVG", 1.4, 60)
print measurement

primitive = jsonutils.to_primitive(measurement, convert_instances=True)
print primitive

dump = jsonutils.dumps(primitive)
print dump

load = jsonutils.loads(dump)
print load

measurement = MeterRecordMessage(**load)
print measurement
