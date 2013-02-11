import json
import logging
import re
from giraffe.service.rest_server import Rest_Server
from giraffe.common.config import Config
import giraffe.service.db as db
from giraffe.service.db import Host, Meter, MeterRecord
from giraffe.service.db import MIN_TIMESTAMP, MAX_TIMESTAMP,\
                               ORDER_ASC, ORDER_DESC


_logger = logging.getLogger("service.rest_api")
_config = Config("giraffe.cfg")


class Rest_API(object):
    def __init__(self):
        self.PARAM_START_TIME = 'start_time'
        self.PARAM_END_TIME = 'end_time'
        self.PARAM_AGGREGATION = 'aggregation'
        self.PARAM_CHART = 'chart'
        self.PARAM_LIMIT = 'limit'
        self.PARAM_ORDER = 'order'
        self.RESULT_LIMIT = 2500
        self.AGGREGATION_COUNT = 'count'
        self.AGGREGATION_MAX = 'max'
        self.AGGREGATION_MIN = 'min'
        self.AGGREGATION_AVG = 'avg'
        self.server = None
        self.db = None
        self._param_patterns = {self.PARAM_START_TIME:
                                    re.compile('^(\d{4})-(\d{2})-(\d{2})_'
                                               '(\d{2})-(\d{2})-(\d{2})$'),
                                self.PARAM_END_TIME:
                                    re.compile('^(\d{4})-(\d{2})-(\d{2})_'
                                               '(\d{2})-(\d{2})-(\d{2})$'),
                                self.PARAM_AGGREGATION: re.compile('^\w+$'),
                                self.PARAM_LIMIT: re.compile('^\d+$'),
                                self.PARAM_ORDER: re.compile('^(%s|%s)$' %\
                                                             (ORDER_ASC,
                                                              ORDER_DESC))}
        self._param_defaults = {self.PARAM_START_TIME: None,
                                self.PARAM_END_TIME: None,
                                self.PARAM_AGGREGATION: None,
                                self.PARAM_LIMIT: self.RESULT_LIMIT,
                                self.PARAM_ORDER: ORDER_ASC}
        self._pattern_timestamp = re.compile(
            '^(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})$')

    def launch(self):
        try:
            self.db = db.connect('%s://%s:%s@%s/%s' % (
                _config.get('db', 'vendor'),
                _config.get('db', 'user'),
                _config.get('db', 'pass'),
                _config.get('db', 'host'),
                _config.get('db', 'schema')))

            conf = dict(log_name='Auth',
                        auth_host=_config.get('rest_api', 'auth_host'),
                        auth_port=_config.getint('rest_api', 'auth_port'),
                        auth_protocol=_config.get('rest_api', 'auth_protocol'),
                        admin_token=_config.get('rest_api', 'admin_token'),
                        delay_auth_decision=_config.getint('rest_api',
                                                           'delay_auth_decision'),
                        rest_api=self,
                        host=_config.get('rest_api', 'host'),
                        port=_config.getint('rest_api', 'port'),
                        )

            self.server = Rest_Server(conf)
            self.server.start()

        except KeyboardInterrupt:
            _logger.info("Ctrl-c received!")
        except:
            _logger.exception("Error: Unable to start API service")
        finally:
            _logger.info("Shutdown API service")

    def _query_params(self, query_string):
        """
        Returns the query parameters for the current request as a dictionary.
        Values of the format "YYYY-MM-DD_HH-ii-ss" are converted to the format
        "YYYY-MM-DD HH:ii:ss".
        All parameters are set with a at least a default value (see
        self._params_defaults).
        """
        query_parts = query_string.split('&')
        params = self._param_defaults.copy()
        for query_part in query_parts:
            try:
                key, value = query_part.split('=', 2)
                if key in params:
                    matches = self._param_patterns[key].match(value)
                    if matches:
                        params[key] = value
                        if key in [self.PARAM_START_TIME, self.PARAM_END_TIME]:
                            params[key] = '%s-%s-%s %s:%s:%s' % \
                                            (matches.group(1),
                                             matches.group(2),
                                             matches.group(3),
                                             matches.group(4),
                                             matches.group(5),
                                             matches.group(6))
            except Exception:
                continue
        return params

    def _aggregate(self, cls, aggregation, args, column="value"):
        """
        Returns an aggregation of an attribute of the given object class
        according to the 'aggregation' parameter:
        - count: returns the number of rows that match the args parameters.
        - max: returns the object that contains the maximum value for "column"
        - min: returns the object that contains the minimum value for "column"
        - avg: returns the average for "column" of all the rows that match the
        args parameters.
        """
        if aggregation == self.AGGREGATION_COUNT:
            count = self.db.count(cls, args)
            return int(count) if count else 0
        elif aggregation == self.AGGREGATION_MAX:
            record = self.db.max_row(cls, column, args)
            return record.to_dict() if record else None
        elif aggregation == self.AGGREGATION_MIN:
            record = self.db.min_row(cls, column, args)
            return record.to_dict() if record else None
        elif aggregation == self.AGGREGATION_AVG:
            avg = self.db.avg(cls, column, args)
            return float(avg) if avg else 0.0
        return None

    def route_root(self):
        """
        Route: /
        Returns: Welcome message (string)
        Query params: -
        """
        return json.dumps('Welcome to Giraffe REST API')

    def route_hosts(self, query_string=''):
        """
        Returns a list of all available Host objects.

        Route: hosts
        Returns: List of Host objects, JSON-formatted
        Query params: aggregation=[count], order
        """
        query = self._query_params(query_string)
        _logger.debug(query)
        self.db.session_open()
        if query[self.PARAM_AGGREGATION] == self.AGGREGATION_COUNT:
            result = self._aggregate(Host, query[self.PARAM_AGGREGATION], {})
            result = json.dumps(result)
        else:
            hosts = self.db.load(Host, order=query[self.PARAM_ORDER],
                                 order_attr='name')
            result = json.dumps([host.to_dict() for host in hosts])
        self.db.session_close()
        return result

    def route_hosts_hid(self, host_id, query_string):
        """
        Returns the Host object where the host_id matches. The host_id can be
        the ID (int) or the NAME (string).

        Route: hosts/<host_id>
        Returns: Host object, JSON-formatted
        Query params: -
        """
        #query = self._query_params(query_string)
        try:
            args = {'id': int(host_id)}
        except ValueError:
            args = {'name': host_id}
        self.db.session_open()
        try:
            host = self.db.load(Host, args=args, limit=1)[0]
        except Exception:
            host = None
        self.db.session_close()
        return json.dumps(host.to_dict()) if host else None

    def route_hosts_hid_meters(self, host_id, query_string):
        """
        Returns a list of Meter objects for which MeterRecords are available
        for the given host.

        Route: hosts/<host_id>/meters
        Returns: List of Meter objects, JSON-formatted
        Query params: -
        """
#        query = self._query_params(query_string)
        try:
            args = {'id': int(host_id)}
        except ValueError:
            args = {'name': host_id}
        self.db.session_open()
        try:
            host = self.db.load(Host, args=args, limit=1)
        except Exception:
            host = None
        meters = []
        if host:
            host = host[0]
            meter_ids = self.db.distinct_values(MeterRecord, 'meter_id',
                                                args={'host_id': host.id},
                                                order=ORDER_ASC)
            meters = self.db.load(Meter, args={'id': meter_ids})
        self.db.session_close()
        return json.dumps([m.to_dict() for m in meters])

    def route_hosts_hid_meters_mid_records(self, host_id, meter_id,
                                           query_string):
        """
        Returns a list of MeterRecord objects for the given Host ID and Meter
        ID.

        Route: hosts/<host_id>/meters/<meter_id>
        Returns: List of MeterRecord objects, JSON-formatted
        Query params: start_time, end_time, aggregation=[count], order, limit
        """
        query = self._query_params(query_string)
        try:
            host_args = {'id': int(host_id)}
        except ValueError:
            host_args = {'name': host_id}
        self.db.session_open()
        try:
            meter_args = {'id': int(meter_id)}
        except ValueError:
            meter_args = {'name': meter_id}
        try:
            host = self.db.load(Host, args=host_args, limit=1)[0]
            meter = self.db.load(Meter, args=meter_args, limit=1)[0]
        except Exception:
            host = None
            meter = None
        result = None
        if host and meter:
            record_args = {'host_id': host.id, 'meter_id': meter.id}
            if query[self.PARAM_START_TIME] or query[self.PARAM_END_TIME]:
                record_args['timestamp'] = [MIN_TIMESTAMP, MAX_TIMESTAMP]
                if query[self.PARAM_START_TIME]:
                    record_args['timestamp'][0] = query[self.PARAM_START_TIME]
                if query[self.PARAM_END_TIME]:
                    record_args['timestamp'][1] = query[self.PARAM_END_TIME]
                record_args['timestamp'] = (record_args['timestamp'][0],
                                            record_args['timestamp'][1])
            _logger.debug('record_args = %s' % record_args)
            try:
                # aggregation
                if query[self.PARAM_AGGREGATION]:
                    result = self._aggregate(MeterRecord,
                                             query[self.PARAM_AGGREGATION],
                                             args=record_args,
                                             column='value')
                    result = json.dumps(result)
                # no aggregation
                else:
                    records = self.db.load(MeterRecord,
                                           args=record_args,
                                           limit=query[self.PARAM_LIMIT],
                                           order=query[self.PARAM_ORDER],
                                           order_attr='timestamp')
                    result = json.dumps([r.to_dict() for r in records])
            except Exception:
                pass
        self.db.session_close()
        return result

    def route_projects(self, query_string=''):
        """
        Returns a list of project name strings.

        Route: projects
        Returns: List of project names (string), JSON-formatted
        Query params: aggregation=[count], order
        """
        query = self._query_params(query_string)
        self.db.session_open()
        values = self.db.distinct_values(MeterRecord, column='project_id',
                                         order=query[self.PARAM_ORDER])
        self.db.session_close()

        # remove null values
        if None in values:
            values.remove(None)

        # do count aggregation
        # note: this is a work-around until Project objects are available
        if query[self.PARAM_AGGREGATION] == self.AGGREGATION_COUNT:
            return json.dumps(str(len(values)))
        return json.dumps(values)

    def route_projects_pid(self, project_id, query_string=''):
        """
        Route: projects/<project_id>
        Returns: -
        Query params: -
        """
        raise NotImplementedError('Route projects/<project_id> not yet '\
                                  'implemented')

    def route_projects_pid_meters(self, project_id, query_string=''):
        """
        Returns a list of Meter objects for which MeterRecords are available
        for the given project.

        Route: projects/<project_id>/meters
        Returns: List of Meter objects, JSON-formatted
        Query params: -
        """
#        query = self._query_params(query_string)
        self.db.session_open()
        try:
            meters = self.db.distinct_values(MeterRecord, 'meter_id',
                                             args={'project_id': project_id},
                                             order=ORDER_ASC)
        except Exception:
            meters = []
        self.db.session_close()
        return json.dumps([m.to_dict() for m in meters])

    def route_projects_pid_meters_mid_records(self, project_id, meter_id,
                                              query_string=''):
        """
        Route: projects/<project_id>/meters/<meter_id>/records
        Returns: List of MeterRecord objects, JSON-formatted
        Query params: start_time, end_time, aggregation=[count], order, limit
        """
        query = self._query_params(query_string)
        self.db.session_open()
        try:
            meter_args = {'id': int(meter_id)}
        except ValueError:
            meter_args = {'name': meter_id}
        try:
            meter = self.db.load(Meter, args=meter_args, limit=1)[0]
        except Exception:
            meter = None

        result = None
        if meter:
            args = {'project_id': project_id, 'meter_id': meter.id}
            if query[self.PARAM_START_TIME] or query[self.PARAM_END_TIME]:
                args['timestamp'] = [MIN_TIMESTAMP, MAX_TIMESTAMP]
                if query[self.PARAM_START_TIME]:
                    args['timestamp'][0] = query[self.PARAM_START_TIME]
                if query[self.PARAM_END_TIME]:
                    args['timestamp'][1] = query[self.PARAM_END_TIME]
                args['timestamp'] = (args['timestamp'][0],
                                     args['timestamp'][1])

            if query[self.PARAM_AGGREGATION]:
                result = self._aggregate(MeterRecord,
                                         query[self.PARAM_AGGREGATION],
                                         args)
                result = json.dumps(result)
            else:
                records = self.db.load(MeterRecord, args,
                                       limit=query[self.PARAM_LIMIT],
                                       order=query[self.PARAM_ORDER],
                                       order_attr='timestamp')
                result = json.dumps([r.to_dict() for r in records])
        self.db.session_close()
        return result

    def route_meters(self, query_string=''):
        """
        Route: meters
        Returns: List of Meter objects, JSON-formatted
        Query params: aggregation=[count], order
        """
        query = self._query_params(query_string)
        self.db.session_open()
        if query[self.PARAM_AGGREGATION] == self.AGGREGATION_COUNT:
            result = self._aggregate(Meter, query[self.PARAM_AGGREGATION], {})
            result = json.dumps(result)
        else:
            meters = self.db.load(Meter, order_attr='name',
                                  order=query[self.PARAM_ORDER])
            result = json.dumps([meter.to_dict() for meter in meters])
        self.db.session_close()
        return result

    def route_meters_mid(self, meter_id, query_string=''):
        """
        Returns a Meter object. The meter_id can either be the ID or the NAME.

        Route: meters/<meter_id>
        Returns: Meter object, JSON-formatted
        Query params: -
        """
        try:
            args = {'id': int(meter_id)}
        except Exception:
            args = {'name': meter_id}
        self.db.session_open()
        try:
            meter = self.db.load(Meter, args=args, limit=1)[0]
        except Exception:
            meter = None
        self.db.session_close()
        return json.dumps(meter.to_dict()) if meter else None

    def route_users(self, query_string=''):
        """
        Route: users
        Returns: List of user names (string), JSON-formatted
        Query params: aggregation=[count], order
        """
        query = self._query_params(query_string)
        self.db.session_open()
        values = self.db.distinct_values(MeterRecord, column='user_id',
                                         order=query[self.PARAM_ORDER])
        self.db.session_close()

        # remove null values
        if None in values:
            values.remove(None)

        # do count aggregation
        # note: this is a work-around until User objects are available
        if query[self.PARAM_AGGREGATION] == self.AGGREGATION_COUNT:
            return json.dumps(str(len(values)))
        return json.dumps(values)

    def route_users_uid_meters_mid_records(self, user_id, meter_id,
                                           query_string=''):
        """
        Route: users/<user_id>/meters/<meter_id>/records
        Returns: List of MeterRecord objects, JSON-formatted
        Query params: start_time, end_time, aggregation=[count], order, limit
        """
        query = self._query_params(query_string)
        self.db.session_open()
        try:
            meter_args = {'id': int(meter_id)}
        except ValueError:
            meter_args = {'name': meter_id}
        try:
            meter = self.db.load(Meter, args=meter_args, limit=1)[0]
        except Exception:
            meter = None

        result = None
        if meter:
            args = {'user_id': user_id, 'meter_id': meter.id}
            if query[self.PARAM_START_TIME] or query[self.PARAM_END_TIME]:
                args['timestamp'] = [MIN_TIMESTAMP, MAX_TIMESTAMP]
                if query[self.PARAM_START_TIME]:
                    args['timestamp'][0] = query[self.PARAM_START_TIME]
                if query[self.PARAM_END_TIME]:
                    args['timestamp'][1] = query[self.PARAM_END_TIME]
                args['timestamp'] = (args['timestamp'][0],
                                     args['timestamp'][1])

            if query[self.PARAM_AGGREGATION]:
                result = self._aggregate(MeterRecord,
                                         query[self.PARAM_AGGREGATION],
                                         args)
                result = json.dumps(result)
            else:
                records = self.db.load(MeterRecord, args,
                                       limit=query[self.PARAM_LIMIT],
                                       order=query[self.PARAM_ORDER],
                                       order_attr='timestamp')
                result = json.dumps([r.to_dict() for r in records])
        self.db.session_close()
        return result

    def route_instances(self, query_string=''):
        """
        Route: instances
        Returns: List of instance names (string), JSON-formatted
        Query params: aggregation=[count], order
        """
        query = self._query_params(query_string)
        self.db.session_open()
        values = self.db.distinct_values(MeterRecord, column='resource_id',
                                         order=query[self.PARAM_ORDER])
        self.db.session_close()

        # remove null values
        if None in values:
            values.remove(None)

        # do count aggregation
        # note: this is a work-around until Instance objects are available
        if query[self.PARAM_AGGREGATION] == self.AGGREGATION_COUNT:
            return json.dumps(str(len(values)))
        return json.dumps(values)

    def route_instances_iid_meters_mid_records(self, instance_id, meter_id,
                                               query_string=''):
        """
        Route: instances/<instance_id>/meters/<meter_id>/records
        Returns: List of MeterRecord objects, JSON-formatted
        Query params: start_time, end_time, aggregation=[count], order, limit
        """
        query = self._query_params(query_string)
        self.db.session_open()
        try:
            meter_args = {'id': int(meter_id)}
        except ValueError:
            meter_args = {'name': meter_id}
        try:
            meter = self.db.load(Meter, args=meter_args, limit=1)[0]
        except Exception:
            meter = None

        result = None
        if meter:
            args = {'resource_id': instance_id, 'meter_id': meter.id}
            if query[self.PARAM_START_TIME] or query[self.PARAM_END_TIME]:
                args['timestamp'] = [MIN_TIMESTAMP, MAX_TIMESTAMP]
                if query[self.PARAM_START_TIME]:
                    args['timestamp'][0] = query[self.PARAM_START_TIME]
                if query[self.PARAM_END_TIME]:
                    args['timestamp'][1] = query[self.PARAM_END_TIME]
                args['timestamp'] = (args['timestamp'][0],
                                     args['timestamp'][1])

            if query[self.PARAM_AGGREGATION]:
                result = self._aggregate(MeterRecord,
                                         query[self.PARAM_AGGREGATION],
                                         args)
                result = json.dumps(result)
            else:
                records = self.db.load(MeterRecord, args,
                                       limit=query[self.PARAM_LIMIT],
                                       order=query[self.PARAM_ORDER],
                                       order_attr='timestamp')
                result = json.dumps([r.to_dict() for r in records])
        self.db.session_close()
        return result
