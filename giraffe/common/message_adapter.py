

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

    def len(self):
        return len(self._adaptee.host_records) + len(
            self._adaptee.instance_records)

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

    def add_instance_record(
            self, project_id, user_id, instance_id, timestamp, meter_type,
            value, duration):
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
