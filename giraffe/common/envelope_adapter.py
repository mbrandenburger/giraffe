import giraffe.common.Message_pb2.Envelope as Envelope

__author__ = 'marcus'

from giraffe.common.BulkMessage_pb2 import Envelop

class EnvelopeAdapter(object):

    def __init__(self, adaptee=None):
        # need to use self.__dict__ to avoid infinite recursion in __getattr__
        if isinstance(adaptee, Envelope):
            self.__dict__['_adaptee'] = adaptee
        elif isinstance(adaptee, str):
            self.__dict__['_adaptee'] = Envelope()
            self.deserialize_from_str(adaptee)
        else:
            self.__dict__['_adaptee'] = Envelope()

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
