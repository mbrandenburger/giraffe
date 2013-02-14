from datetime import datetime
from giraffe.common.message_adapter import MessageAdapter
from giraffe.common.envelope_adapter import EnvelopeAdapter
from giraffe.common.crypto import validateSignature
from giraffe.common.config import Config
from giraffe.common.rabbit_mq_connector import Connector, BasicConsumer
from giraffe.service import db
from giraffe.service.db import Host, Meter, MeterRecord
import MySQLdb

import logging
_logger = logging.getLogger("service.collector")


class Collector(object):
    def __init__(self):
        self.config = Config("giraffe.cfg")
        _RABBIT_USER = self.config.get("rabbit", "user")
        _RABBIT_PASS = self.config.get("rabbit", "pass")
        _RABBIT_HOST = self.config.get("rabbit", "host")
        _RABBIT_PORT = self.config.getint("rabbit", "port")
        self.connector = Connector(_RABBIT_USER, _RABBIT_PASS,
                                   _RABBIT_HOST, _RABBIT_PORT)

        self.queue = self.config.get("rabbit", "queue")
        self.exchange = self.config.get("rabbit", "exchange")
        self.routing_key = self.config.get("rabbit", "routing_key")
        self.shared_secret = self.config.get("collector", "shared_secret")
        self.consumer = BasicConsumer(self.connector, self.queue,
                                      self.exchange, self._collector_callback)

        # connect to giraffe database
        self.db = db.connect('%s://%s:%s@%s/%s'
                             % (self.config.get('db', 'vendor'),
                                self.config.get('db', 'user'),
                                self.config.get('db', 'pass'),
                                self.config.get('db', 'host'),
                                self.config.get('db', 'schema')))

        # known servers/instances
        self.known_instances = {}

    def launch(self):
        try:
            self.connector.connect()
            self.start_collecting()
        except KeyboardInterrupt:
            _logger.info("Ctrl-c received!")
        except:
            _logger.exception("Error: Unable to start collector service")
        finally:
            self.stop_collecting()
            _logger.info("Shutdown collector service")

    def start_collecting(self):
        _logger.debug("Start collecting from broker")
        self.consumer.consume()

    def stop_collecting(self):
        _logger.debug("Stop collecting from broker")
        self.consumer.stop_consuming()

    def _str_to_datetime(self, timestamp_str):
        return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

    def _datetime_to_str(self, datetime_obj):
        return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")

    def _collector_callback(self, params):
        envelope = EnvelopeAdapter()

        # check whether incorrectly formatted message
        try:
            envelope.deserialize_from_str(params)
        except:
            return

        message = MessageAdapter(envelope.message)
        # validate signature
        if not validateSignature(str(message), self.shared_secret,
                                 envelope.signature):
            return

        self.db.session_open()

        # load all meters now to avoid queries later
        meters = self.db.load(Meter)
        meter_dict = {}
        for meter in meters:
            meter_dict[meter.name] = meter

        # insert host if it does not exist
        hosts = self.db.load(Host, {'name': message.host_name}, limit=1)
        if not hosts:
            host = Host(name=message.host_name)
            self.db.save(host)
            self.db.commit()
        else:
            host = hosts[0]

        # insert all host records
        for r in message.host_records:
            if r.meter_name not in meter_dict:
                _logger.warning('Unknown meter_name "%s"' % r.meter_name)
                continue
            try:
                record = MeterRecord(meter_id=meter_dict[r.meter_name].id,
                                     host_id=host.id,
                                     user_id=None,
                                     resource_id=None,
                                     project_id=None,
                                     value=r.value,
                                     duration=r.duration,
                                     timestamp=r.timestamp)
                self.db.save(record)
                _logger.debug("New %s" % record)
                # update host activity
                record_timestamp = self._str_to_datetime(r.timestamp)
                if not host.activity or record_timestamp > host.activity:
                    host.activity = record_timestamp
            except Exception as e:
                _logger.exception(e)

        # insert all instance records
        for r in message.inst_records:
            if r.meter_name not in meter_dict:
                _logger.warning('Unknown meter_name "%s"' % r.meter_name)
                continue
            try:
                # @[fbahr] - TODO: `self.known_instances` grows over time
                #                  towards inf. - clean-up?
                if not r.inst_id in self.known_instances:
                    self.known_instances[r.inst_id] = self._metadata(uuid=r.inst_id)

                r.project_id, r.user_id = self.known_instances[r.inst_id]

                record = MeterRecord(meter_id=meter_dict[r.meter_name].id,
                                     host_id=host.id,
                                     user_id=r.user_id,
                                     resource_id=r.inst_id,
                                     project_id=r.project_id,
                                     value=r.value,
                                     duration=r.duration,
                                     timestamp=r.timestamp)
                self.db.save(record)
                _logger.debug("New %s" % record)
                # update host activity
                record_timestamp = self._str_to_datetime(r.timestamp)
                if not host.activity or record_timestamp > host.activity:
                    host.activity = record_timestamp
            except Exception as e:
                _logger.exception(e)

        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            _logger.exception(e)
        self.db.session_close()

    def _metadata(self, uuid):
        """
        (Low-level) connection to nova database; fetches a (project_id,
        user_id) tuple for a given instance uuid.

        TODO: Provide a more 'abstract' way to interact with the nova-db.
        """
        nova_db = MySQLdb.connect(self.config.get('nova-db', 'host'),
                                  self.config.get('nova-db', 'user'),
                                  self.config.get('nova-db', 'pass'),
                                  self.config.get('nova-db', 'schema'))

        cursor = nova_db.cursor()
        cursor.execute('SELECT project_id, user_id '
                       'FROM instances '
                       'WHERE uuid = "%s"' % uuid)

        return cursor.fetchone()
