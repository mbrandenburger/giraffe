from giraffe.common.Message_pb2 import BulkMessage
from google.protobuf.text_format import MessageToString

class MessageAdapter(object):
    """
    MessageAdapter exposes all attributes of the underlying adaptee object
    so all attributes of that object can be accessed by calling
    adapter.adaptee_attribute.
    """

    def __init__(self, adaptee=None):  # @[fbahr]: r/dataStr/adaptee/
        # need to use self.__dict__ to avoid infinite recursion in __getattr__
        if isinstance(adaptee, BulkMessage):
            self.__dict__['_adaptee'] = adaptee
        elif isinstance(adaptee, str):
            self.__dict__['_adaptee'] = BulkMessage()
            self.deserialize_from_str(adaptee)  # @[fbahr]: r/dataStr/adaptee/
        else:
            self.__dict__['_adaptee'] = BulkMessage()

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
            self._adaptee.inst_records)

    def add_host_record(self, timestamp, meter_name, value, duration):
        """
        Adds a host record to the underlying adaptee object.
        The host_id has to be set by accessing the attribute directly, i.e.
        by calling adapter.host_id = '...'
        """
        if self._adaptee.host_records is None:
            self._adaptee.host_records = []

        host_record = self._adaptee.host_records.add()
        host_record.timestamp = timestamp
        host_record.meter_name = meter_name
        host_record.value = str(value)
        host_record.duration = duration

    def add_inst_record(self, project_id, user_id, inst_id, timestamp,
                        meter_name, value, duration):
        """
        Adds an instance record to the underlying adaptee object.
        """
        if self._adaptee.inst_records is None:
            self._adaptee.inst_records = []

        inst_record = self._adaptee.inst_records.add()
        inst_record.project_id = project_id
        inst_record.user_id = user_id
        inst_record.inst_id = inst_id
        inst_record.timestamp = timestamp
        inst_record.meter_name = meter_name
        inst_record.value = str(value)
        inst_record.duration = duration

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

    def __str__(self):
        return MessageToString(self._adaptee)

