from giraffe.common import Message_pb2

__author__ = 'marcus'

# (Marcus)TODO: Adapter bauen

class MessageAdapter(object):

#    TODO: Factory
    @staticmethod
    def host_cpu_avg(params):

        hostMsg = Message_pb2.MeterHostMessage()
#        (Marcus)TODO: replace MacBook with real hostname from config file
        hostMsg.hostID = "MacBook"

#        (Marcus)TODO: Whats about duration? Must depent on metering duration
        record1 = hostMsg.meters.add()
        record1.timestamp = "jetzt"
        record1.type = "CPU_AVG_1"
        record1.value = str(params[0])
        record1.duration = 60

        record2 = hostMsg.meters.add()
        record2.timestamp = "jetzt"
        record2.type = "CPU_AVG_5"
        record2.value = str(params[1])
        record2.duration = 300

        record3 = hostMsg.meters.add()
        record3.timestamp = "jetzt"
        record3.type = "CPU_AVG_15"
        record3.value = str(params[2])
        record3.duration = 1500

        return hostMsg.SerializeToString()
