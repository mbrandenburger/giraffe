__author__ = 'fbahr, omihelic'

import sys
import unittest
import re
from giraffe.common.config import Config
from giraffe.common.auth import AuthProxy
from giraffe.client.api import GiraffeClient
from giraffe.client.formatter import Text, CsvFormatter
from giraffe.service.db import Host, Meter, MeterRecord
import requests


class ClientTestCases(unittest.TestCase):

    python_version = int(''.join([str(i) for i in sys.version_info[0:3]]))

    @classmethod
    def setUpClass(cls):
        cls.config = Config('../../bin/giraffe.cfg')

        cls.gc = GiraffeClient(username=cls.config.get('client', 'user'),
                               password=cls.config.get('client', 'pass'),
                               tenant_name=cls.config.get('client', 'tenant_name'),
                               tenant_id=cls.config.get('client', 'tenant_id'),
                               auth_url=cls.config.get('auth', 'auth_url'))

    def setUp(self):
        if ClientTestCases.python_version < 270:
            self.config = Config('../../bin/giraffe.cfg')

            self.gc = GiraffeClient(username=self.config.get('client', 'user'),
                                    password=self.config.get('client', 'pass'),
                                    tenant_name=self.config.get('client', 'tenant_name'),
                                    tenant_id=self.config.get('client', 'tenant_id'),
                                    auth_url=self.config.get('auth', 'auth_url'))

    def test_get_set_auth_token(self):
        auth_token = self.gc.auth_token
        self.gc.auth_token = auth_token
        self.assertEqual(auth_token, self.gc.auth_token)

    def test_get_root(self):
        root = self.gc.get_root()
        self.assertIsNotNone(root)
        self.assertTrue(isinstance(root, (str, unicode)))

    def test_get_meters(self):
        meters = self.gc.get_meters()  # tuple (ResultSet) of dicts
        self.assertIsNotNone(meters)
        self.assertTrue(isinstance(meters, (tuple)))

        meters = meters.as_(Meter)  # tuple of Meter objects
        self.assertIsNotNone(meters)
        self.assertTrue(isinstance(meters[0], (Meter)))

    def test_get_hosts(self):
        hosts = self.gc.get_hosts()  # tuple (ResultSet) of dicts
        # for h in hosts:
        #     print h
        self.assertIsNotNone(hosts)
        self.assertTrue(isinstance(hosts, (tuple)))

        hosts = hosts.as_(Host)  # tuple of Host objects
        self.assertIsNotNone(hosts)
        self.assertTrue(isinstance(hosts[0], (Host)))

    def test_get_host_by_id(self):
        # host_id = 'uncinus'
        host_id = 600

        host = self.gc.get_host(host=host_id)      # remember: tuple (ResultSet)
        self.assertIsNotNone(host)                 #           of dicts
        self.assertTrue(isinstance(host, (tuple)))

        host = host.as_(Host)  # also: tuple of Host objects
        self.assertTrue(isinstance(host[0], (Host)))

    def test_get_host_meters(self):
        # host_id = 'uncinus'
        host_id = 603

        meters = self.gc.get_host_meters(host_id)  # tuple (ResultSet) of dicts
        # for h in hosts:
        #     print h
        self.assertIsNotNone(meters)
        self.assertTrue(isinstance(meters, (tuple)))

        meters = meters.as_(Meter)  # tuple of Host objects
        self.assertIsNotNone(meters)
        self.assertTrue(isinstance(meters[0], (Meter)))

    def test_get_host_meter_records(self):
        meter_records = self.gc.get_host_meter_records( \
                                    host='uncinus',
                                    meter="host.loadavg_15m")
                                    # ^ tuple (ResultSet) of dicts
        self.assertIsNotNone(meter_records)
        self.assertTrue(isinstance(meter_records, (tuple)))

        meter_records = meter_records.as_(MeterRecord)
                                    # ^ tuple of MeterRecord objects
        self.assertIsNotNone(meter_records)
        self.assertTrue(isinstance(meter_records[0], (MeterRecord)))

    def test_get_host_meter_records_with_display_limit(self):
        limit = 2

        meter_records = self.gc.get_host_meter_records( \
                                    host='uncinus', \
                                    meter="host.loadavg_15m", \
                                    params={'limit': limit})
        self.assertEqual(len(meter_records), limit)

    def test_count_host_meter_records(self):
        len_meter_records = len(self.gc.get_host_meter_records( \
                                            host='uncinus', \
                                            meter="host.loadavg_15m"))
                            # ^ int

        count = self.gc.get_host_meter_records( \
                            host='uncinus', \
                            meter="host.loadavg_15m", \
                            params={'aggregation': 'count'})
                            # ^ int
        self.assertFalse(isinstance(count, (tuple)))
        self.assertTrue(isinstance(count, (int)))
        self.assertEqual(count, len_meter_records)

    def test_count_host_meter_records_with_time_limits(self):
        start_time = '2013-02-07_12-00-00'
        end_time   = '2013-02-07_23-59-59'

        count = self.gc.get_host_meter_records( \
                            host='uncinus', \
                            meter="host.loadavg_15m", \
                            params={'aggregation': 'count'})
                            # ^ int
        self.assertFalse(isinstance(count, (tuple)))
        self.assertTrue(isinstance(count, (int)))

        num_all_records = count

        count = self.gc.get_host_meter_records( \
                            host='uncinus', \
                            meter="host.loadavg_15m", \
                            params={'start_time': start_time, \
                                    'end_time': end_time, \
                                    'aggregation': 'count'})
                                    # ^ int
        self.assertFalse(isinstance(count, (tuple)))
        self.assertTrue(isinstance(count, (int)))

        self.assertLess(count, num_all_records)

    def test_get_min_max_host_meter_record(self):
        _min = self.gc.get_host_meter_records( \
                           host='uncinus', \
                           meter="host.loadavg_15m", \
                           params={'aggregation': 'min'}) \
                           # ^ tuple (ResultSet) of dicts
        self.assertTrue(isinstance(_min, (tuple)))
        self.assertEqual(len(_min), 1)
        _min = _min.as_(MeterRecord)[0]  # MeterRecord object
        self.assertTrue(isinstance(_min, (MeterRecord)))

        _max = self.gc.get_host_meter_records( \
                          host='uncinus', \
                          meter="host.loadavg_15m", \
                          params={'aggregation': 'max'}) \
                          # ^ tuple (ResultSet) of dicts
        self.assertTrue(isinstance(_max, (tuple)))
        self.assertEqual(len(_max), 1)
        _max = _max.as_(MeterRecord)[0]  # MeterRecord object
        self.assertTrue(isinstance(_max, (MeterRecord)))

        self.assertLessEqual(_min.value, _max.value)

    def test_get_host_meter_records_with_time_limits(self):
        start_time = '2013-02-07_12-00-00'
        end_time   = '2013-02-07_23-59-59'

        regex = re.compile('^(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})$')
        matches = regex.match(start_time)
        start_time_repr = '%s-%s-%s %s:%s:%s' % \
                              (matches.group(1), matches.group(2), \
                               matches.group(3), matches.group(4), \
                               matches.group(5), matches.group(6))
        matches = regex.match(end_time)
        end_time_repr = '%s-%s-%s %s:%s:%s' % \
                              (matches.group(1), matches.group(2), \
                               matches.group(3), matches.group(4), \
                               matches.group(5), matches.group(6))

        meter_records = self.gc.get_host_meter_records( \
                                    host='uncinus', \
                                    meter="host.loadavg_15m", \
                                    params={'start_time': start_time, \
                                            'end_time': end_time, \
                                            'order': 'asc'})
                                    # ^ tuple (ResultSet) of dicts
        self.assertTrue(isinstance(meter_records, (tuple)))
        meter_records = meter_records.as_(MeterRecord)
        self.assertTrue(isinstance(meter_records[0], (MeterRecord)))

        start_asc = meter_records[0]
        end_asc = meter_records[-1]
        self.assertLessEqual(start_time_repr, start_asc.timestamp)
        self.assertLessEqual(end_asc.timestamp, end_time_repr)
        self.assertLessEqual(start_asc.timestamp, end_asc.timestamp)

        meter_records = self.gc.get_host_meter_records( \
                                    host='uncinus', \
                                    meter="host.loadavg_15m", \
                                    params={'start_time': start_time, \
                                            'end_time': end_time, \
                                            'order': 'desc'})
                                    # ^ tuple (ResultSet) of dicts
        self.assertTrue(isinstance(meter_records, (tuple)))
        meter_records = meter_records.as_(MeterRecord)
        self.assertTrue(isinstance(meter_records[0], (MeterRecord)))

        start_desc = meter_records[0]
        end_desc = meter_records[-1]
        self.assertEqual(start_asc.timestamp, end_desc.timestamp)
        self.assertTrue(start_desc.timestamp, end_asc.timestamp)
        self.assertTrue(start_desc.timestamp >= end_desc.timestamp)

    def test_get_min_max_host_meter_record_within_time_limits(self):
        start_time = '2013-02-07_20-15-00'
        end_time   = {}
        end_time[0] = '2013-02-07_20-25-59'
        end_time[1] = '2013-02-07_20-40-59'

        abs_min = self.gc.get_host_meter_records( \
                              host='uncinus', \
                              meter="host.loadavg_15m", \
                              params={'aggregation': 'min'}) # tuple (ResultSet) of dicts
        self.assertEqual(len(abs_min), 1)
        abs_min = abs_min.as_(MeterRecord)[0]  # MeterRecord object
        # print abs_min.value, abs_min

        for _, endtime in end_time.iteritems():
            rel_min = self.gc.get_host_meter_records( \
                                  host='uncinus', \
                                  meter="host.loadavg_15m", \
                                  params={'start_time': start_time, \
                                          'end_time': endtime, \
                                          'aggregation': 'min'})  # tuple (ResultSet) of dicts
            if isinstance(rel_min, (tuple)):
                self.assertEqual(len(rel_min), 1)
                rel_min = rel_min.as_(MeterRecord)[0]  # MeterRecord object
                # print rel_min.value, rel_min
                # print abs_min.value, '<=', rel_min.value
                self.assertLessEqual(abs_min.value, rel_min.value)
            else:
                self.assertIsNone(rel_min)

        abs_max = self.gc.get_host_meter_records( \
                              host='uncinus', \
                              meter="host.loadavg_15m", \
                              params={'aggregation': 'max'}) # tuple (ResultSet) of dicts
        self.assertEqual(len(abs_max), 1)
        abs_max = abs_max.as_(MeterRecord)[0]  # MeterRecord object

        for _, endtime in end_time.iteritems():
            rel_max = self.gc.get_host_meter_records( \
                                  host='uncinus', \
                                  meter="host.loadavg_15m", \
                                  params={'start_time': start_time, \
                                          'end_time': endtime, \
                                          'aggregation': 'max'}) \
                                  # ^ tuple (ResultSet) of dicts
            if isinstance(rel_max, (tuple)):
                self.assertEqual(len(rel_max), 1)
                rel_max = rel_max.as_(MeterRecord)[0]  # MeterRecord object
                self.assertGreaterEqual(abs_max.value, rel_max.value)
            else:
                self.assertIsNone(rel_max)

    def test_get_instances_as_Text_CsvFormatted(self):
        instances = self.gc.get_instances()  # tuple (ResultSet) of dicts
        self.assertIsNotNone(instances)
        self.assertTrue(isinstance(instances, (tuple)))

        instances = instances.as_(Text, formatter=CsvFormatter)
        # for i in instances:
        #     print type(i), i
        #     self.assertTrue(isinstance(i, unicode))  # unicoded string
        self.assertTrue(isinstance(instances[0], unicode))

    def test_get_inst_meter_records(self):
        uuid = 'd2b24038-9dee-45d3-876f-d736ddd02d84'

        meter_records = self.gc.get_inst_meter_records( \
                                    inst=uuid,
                                    meter="inst.uptime")
                                    # ^ tuple (ResultSet) of dicts
        self.assertIsNotNone(meter_records)
        self.assertTrue(isinstance(meter_records, (tuple)))

        meter_records = meter_records.as_(MeterRecord)
                                    # ^ tuple of MeterRecord objects
        self.assertIsNotNone(meter_records)
        self.assertTrue(isinstance(meter_records[0], (MeterRecord)))
        self.assertEqual(meter_records[0].resource_id, uuid)

    def test_avg_inst_meter_records(self):
        uuid = 'd2b24038-9dee-45d3-876f-d736ddd02d84'

        avg = self.gc.get_inst_meter_records( \
                          inst=uuid, \
                          meter="inst.uptime", \
                          params={'aggregation': 'avg'}) # float
        self.assertTrue(isinstance(avg, (float)))

    def test_get_records(self):
        meter_records = self.gc.get_records()  # tuple (ResultSet) of dicts
        self.assertIsNotNone(meter_records)
        self.assertTrue(isinstance(meter_records, (tuple)))

        meter_records = meter_records.as_(MeterRecord)  # tuple of MeterRecord objects
        self.assertIsNotNone(meter_records)
        self.assertTrue(isinstance(meter_records[0], (MeterRecord)))

    def test_get_record(self):
        record_ids = [1000, 346607]

        for record_id in record_ids:
            try:
                meter_records = self.gc.get_record(record_id)
            except Exception as e:
                self.assertTrue(isinstance(e, requests.exceptions.HTTPError))
                continue

            self.assertIsNotNone(meter_records)
            self.assertTrue(isinstance(meter_records, (tuple)))
                            # ^ tuple (ResultSet) of dicts
            meter_records = meter_records.as_(MeterRecord)
                            # ^ tuple of MeterRecord objects
            self.assertIsNotNone(meter_records)
            self.assertEqual(len(meter_records), 1)
            self.assertTrue(isinstance(meter_records[0], (MeterRecord)))

    def test_count_records(self):
        meter_records = self.gc.get_records()  # tuple (ResultSet) of dicts
        self.assertIsNotNone(meter_records)
        self.assertTrue(isinstance(meter_records, (tuple)))
        len_result_set = len(meter_records)

        meter_records = meter_records.as_(MeterRecord)  # tuple of MeterRecord objects
        self.assertIsNotNone(meter_records)
        self.assertTrue(isinstance(meter_records[0], (MeterRecord)))
        len_tuple = len(meter_records)

        self.assertEqual(len_result_set, len_tuple)

        count = self.gc.get_records(params={'aggregation': 'count'})

        self.assertEqual(count, len_result_set)

    def test_get_proj_meter_records(self):
        project = 1
        meter   = 'host.loadavg_15m'

        proj_meter_records = self.gc.get_proj_meter_records(project, meter)
        self.assertIsNotNone(proj_meter_records)
        self.assertTrue(isinstance(proj_meter_records, (tuple)))

    def test_with_giraffe_user(self):
        # auth_token = AuthProxy.get_token()
        pass


if __name__ == '__main__':
    unittest.main()
