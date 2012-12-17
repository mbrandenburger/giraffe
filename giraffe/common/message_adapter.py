

from giraffe.common import Message_pb2
from giraffe.common import BulkMessage_pb2
from giraffe.common.config import Config
from giraffe.common.BulkMessage_pb2 import BulkMessage

from datetime import datetime


class MessageAdapter(object):
    """
    MessageAdapter exposes all attributes of the underlying adaptee object
    so all attributes of that object can be accessed by calling
    adapter.adaptee_attribute.
    """

    def __init__(self, adaptee=None):
        # need to use self.__dict__ to avoid infinite recursion in __getattr__
        if isinstance(adaptee, BulkMessage):
            self.__dict__['_adaptee'] = adaptee
        elif isinstance(adaptee, str):
            self.__dict__['_adaptee'] = BulkMessage_pb2.BulkMessage()
            self.deserialize_from_str(adaptee)
        else:
            self.__dict__['_adaptee'] = BulkMessage_pb2.BulkMessage()

    def __getattr__(self, name):
        if hasattr(self._adaptee, name):
            return self._adaptee.__getattribute__(name)
        else:
            raise AttributeError(('Neither adapter nor adaptee has the '
                                  'attribute "%s"') % name)

    def __setattr__(self, name, value):
        if hasattr(self._adaptee, name):
            self._adaptee.__setattr__(name, value)
        else:
            raise AttributeError(('Neither adapter nor adaptee has the '
                                  'attribute "%s"') % name)

    def add_host_record(self, timestamp, meter_type, value, duration):
        """
        Adds a host record to the underlying adaptee object.
        The host_id has to be set by accessing the attribute directly, i.e.
        by calling adapter.host_id = '...'
        """
        if self._adaptee.host_records is None:
            self._adaptee.host_records = []

        host_record = self._adaptee.host_records.add()
        host_record.timestamp = timestamp
        host_record.type = meter_type
        host_record.value = str(value)
        host_record.duration = duration

    def add_instance_record(self, project_id, user_id, instance_id, timestamp,
                          meter_type, value, duration):
        """
        Adds an instance record to the underlying adaptee object.
        """
        if self._adaptee.instance_records is None:
            self._adaptee.instance_records = []
        instance_record = self._adaptee.instance_records.add()
        instance_record.project_id = project_id
        instance_record.user_id = user_id
        instance_record.instance_id = instance_id
        instance_record.timestamp = timestamp
        instance_record.type = meter_type
        instance_record.value = str(value)
        instance_record.duration = duration

    def serialize_to_str(self):
        """
        Returns a string representation of this object.
        """
        return self._adaptee.SerializeToString()

    def deserialize_from_str(self, dataStr):
        """
        Deserializes data from a string into attributes of the adaptee object.
        """
        self._adaptee.ParseFromString(dataStr)

    # @deprecated: use add_host_record() and add_instance_record() instead
    @staticmethod
    def host_cpu_avg(params):

        time_now = str(datetime.now())

        hostMsg = Message_pb2.MeterHostMessage()
#        (Marcus)TODO: replace MacBook with real hostname from config file
        hostMsg.hostID = Config().get("agent", "hostname")

#        (Marcus)TODO: Whats about duration? Must depent on metering duration
        record1 = hostMsg.meters.add()
        record1.timestamp = time_now
        record1.type = "CPU_AVG_1"
        record1.value = str(params[0])
        record1.duration = 60

        record2 = hostMsg.meters.add()
        record2.timestamp = time_now
        record2.type = "CPU_AVG_5"
        record2.value = str(params[1])
        record2.duration = 300

        record3 = hostMsg.meters.add()
        record3.timestamp = time_now
        record3.type = "CPU_AVG_15"
        record3.value = str(params[2])
        record3.duration = 1500

        return hostMsg.SerializeToString()
