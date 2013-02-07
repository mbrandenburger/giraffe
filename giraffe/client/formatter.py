__author__ = 'fbahr'

import json
from datetime import datetime
# from prettytable import PrettyTable

from giraffe.service.db \
    import Base, Host, Meter, MeterRecord
from giraffe.client.formatter \
    import Text, JsonFormatter, CsvFormatter, HostFormatter, MeterFormatter, \
           MeterRecordFormatter

# -----------------------------------------------------------------------------

DEFAULT_FORMATTERS = dict((Host, HostFormatter),
                          (Meter, MeterFormatter),
                          (MeterRecord, MeterRecordFormatter),
                          (Text, JsonFormatter))


# -----------------------------------------------------------------------------

#@[fbahr] - TODO: Come up with a better naming scheme; Formatter and 
#                 FormattableObject - but serialize()?
#                 Also, pretty pointless design decisions - along the overall
#                 framework (so far).

class Formatter(object):
    @staticmethod
    def serialize(message):
        """
        message = list of dictionaries
        """
        raise NotImplementedError


class FormattableObject(object):
    """
    Abstract base clase.
    """

#   def get_formatter(self):
#       return self.formatter

    @staticmethod
    def get_formatter():
        raise NotImplementedError


# Text formatters -------------------------------------------------------------

class Text(FormattableObject):
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
    def serialize(message):
        return json.dumps(message, indent=4)


class CsvFormatter(Formatter):
    @staticmethod
    def serialize(message):
        if not message:
            return 'Empty result set.'

        if not isinstance(message, (tuple, list, dict)):
            return str(message)

        UNIX_EPOCH = datetime(1970, 1, 1, 0, 0)
        for dct in list(message):
            row = []
            for key, val in dct.iteritems():
                if key == 'timestamp':
                    dt = datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
                    delta = UNIX_EPOCH - dt
                    val = - delta.days * 24 * 3600 + delta.seconds
                row.append(str(val))
            str += '\t'.join(row)

        return str


class TableFormatter(Formatter):
    @staticmethod
    def serialize(message):
        raise NotImplementedError("Warning: not yet implemented.")


# Object formatters -----------------------------------------------------------

class __Host(FormattableObject):
#   def __init__(self):
#       self.formatter = HostFormatter
    pass


class HostFormatter(Formatter):
    @staticmethod
    def serialize(element):
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
#   def __init__(self):
#       self.formatter = MeterFormatter
    pass


class MeterFormatter(Formatter):
    @staticmethod
    def serialize(element):
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
#   def __init__(self):
#       self.formatter = MeterRecordFormatter
    pass


class MeterRecordFormatter(Formatter):
    @staticmethod
    def serialize(element):
        try:
            record = MeterRecord()
            record.id, record.host_id, record.resource_id, \
            record.project_id, record.user_id, record.meter_id, \
            record.timestamp, record.value, record.duration = \
                element['id'], element['host_id'], \
                element['resource_id'], element['project_id'], \
                element['user_id'], int(element['meter_id']), \
                element['timestamp'], element['value'], \
                element['duration']

        except Exception as e:
            # logger.exception
            raise e

        finally:
            return record
