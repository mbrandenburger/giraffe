__author__ = 'fbahr'


import __builtin__
import json
# from prettytable import PrettyTable

from giraffe.service.db import Host, Meter, MeterRecord  # , Base

# -----------------------------------------------------------------------------

#@[fbahr] - TODO: Come up with a better naming scheme; Formatter and
#                 FormattableObject - but serialize()?
#                 Also, pretty pointless design decisions - along the overall
#                 framework (so far).

class Formatter(object):
    """
    Abstract base class
    """

    @staticmethod
    def serialize(message, *args):
        """
        message = list of dictionaries
        """
        raise NotImplementedError


class FormattableObject(object):
    """
    Abstract base class
    """

#   def get_formatter(self):
#       return self.formatter

    @staticmethod
    def get_formatter():
        raise NotImplementedError


# Text formatters -------------------------------------------------------------

class Text(FormattableObject):
    """
    Marker interface
    """
#   def __init__(self, formatter=None):
#       if not(formatter and issubclass(formatter, Formatter)):
#           raise TypeError('Excepts Formatter class descriptor')
#       self.formatter = formatter

#   def get_formatter(self):
#       return self.formatter

    @staticmethod
    def get_formatter():
        return DEFAULT_FORMATTERS.get(Text)


class JsonFormatter(Formatter):
    @staticmethod
    def serialize(message, *args):
        return json.dumps(message, indent=4)


class CsvFormatter(Formatter):
    @staticmethod
    def serialize(message, *args):
        if isinstance(message, (dict)):
        #   UNIX_EPOCH = datetime(1970, 1, 1, 0, 0)
        #   for key, val in message.iteritems():
        #       if key == 'timestamp':
        #           dt = datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
        #           delta = UNIX_EPOCH - dt
        #           val = - delta.days * 24 * 3600 + delta.seconds
        #       row.append(val)
            return '\t'.join(message.values())

        elif isinstance(message, (tuple, list)):
            return '\t'.join(message)

        else:
            return message


class TabFormatter(Formatter):
    @staticmethod
    def serialize(message, *args):
        raise NotImplementedError("Warning: not yet implemented.")


# Object formatters -----------------------------------------------------------

class __Host(FormattableObject):
    """
    Marker interface
    """
#   def __init__(self):
#       self.formatter = HostFormatter
    pass


class HostFormatter(Formatter):
    @staticmethod
    def serialize(element, *args):
        try:
            host = Host()
            host.__dict__.update(dict((k, v)
                                 for (k, v) in element.iteritems() \
                                     if k in ['id', 'name']))

        except Exception as e:
            # logger.exception
            raise e

        finally:
            return host


class __Meter(FormattableObject):
    """
    Marker interface
    """
#   def __init__(self):
#       self.formatter = MeterFormatter
    pass


class MeterFormatter(Formatter):
    @staticmethod
    def serialize(element, *args):
        try:
            meter = Meter()
            meter.__dict__.update(dict((k, v)
                                  for (k, v) in element.iteritems() \
                                      if k in ['id', 'name', 'description', \
                                               'unit_name', 'data_type']))

        except Exception as e:
            # logger.exception
            raise e

        finally:
            return meter


class __MeterRecord(FormattableObject):
    """
    Marker interface
    """
#   def __init__(self):
#       self.formatter = MeterRecordFormatter
    pass


class MeterRecordFormatter(Formatter):
    @staticmethod
    def serialize(element, *args):
        catalog = args[0] if args else {}

        try:
            record = MeterRecord()
            record.id, record.host_id, record.resource_id, \
            record.project_id, record.user_id, record.meter_id, \
            record.timestamp, record.duration = \
                element['id'], element['host_id'], \
                element['resource_id'], element['project_id'], \
                element['user_id'], int(element['meter_id']), \
                element['timestamp'], element['duration']

            value_type = catalog.get(record.meter_id)
            record.value = getattr(__builtin__, value_type)(element['value']) \
                               if value_type \
                               else element['value']

        except Exception as e:
            # logger.exception
            raise e

        finally:
            return record


# -----------------------------------------------------------------------------

DEFAULT_FORMATTERS = dict([(Host, HostFormatter),
                           (Meter, MeterFormatter),
                           (MeterRecord, MeterRecordFormatter),
                           (Text, JsonFormatter)])
