import logging
import threading

from giraffe.common.message_adapter import MessageAdapter
from giraffe.common.config import Config
from giraffe.common.rabbit_mq_connector import Connector, BasicConsumer
from giraffe.service import db
from giraffe.service.db import Host, Meter, MeterRecord

logger = logging.getLogger("service.collector")

config = Config("giraffe.cfg")

_RABBIT_HOST = config.get("rabbit", "host")
_RABBIT_QUEUE = config.get("rabbit", "queue")
_RABBIT_EXCHANGE = config.get("rabbit", "exchange")
_RABBIT_ROUTING_KEY = config.get("rabbit", "routing_key")


class Collector(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.connector = Connector(_RABBIT_HOST)
        self.queue = _RABBIT_QUEUE
        self.exchange = _RABBIT_EXCHANGE
        self.routing_key = _RABBIT_ROUTING_KEY
        self.consumer = BasicConsumer(self.connector, self.queue,
                                      self.exchange, self._collector_callback)

        # connect to database
        self.db = db.connect('%s://%s:%s@%s/%s' % (config.get('db', 'vendor'),
                                                   config.get('db', 'user'),
                                                   config.get('db', 'pass'),
                                                   config.get('db', 'host'),
                                                   config.get('db', 'schema')))

    def run(self):
        self.start_collecting()

    def stop(self):
        self.stop_collecting()
        self._Thread__stop()

    def start_collecting(self):
        logger.debug("Start collecting from rabbit")
        self.consumer.consume()

    def stop_collecting(self):
        logger.debug("Stop collecting from rabbit")
        self.consumer.stop_consuming()

    def _collector_callback(self, params):

        message = MessageAdapter()
        message.deserialize_from_str(params)

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
            if r.type not in meter_dict:
                logger.debug('WARNING: unknown meter_type "%s"' % r.type)
                continue
            try:
                record = MeterRecord(meter_id=meter_dict[r.type].id,
                                     host_id=host.id,
                                     user_id=None,
                                     resource_id=None,
                                     project_id=None,
                                     value=r.value,
                                     duration=r.duration,
                                     timestamp=r.timestamp,
                                     signature=message.signature)
                self.db.save(record)
                logger.debug("Message from %s: %s" % (host.name,record))
            except Exception:
                logger.debug('WARNING: failed to insert host record %s' %
                             record)

        # insert all instance records
        for r in message.instance_records:
            if r.type not in meter_dict:
                logger.debug('WARNING: unknown meter_type "%s"' % r.type)
                continue
            try:
                record = MeterRecord(meter_id=meter_dict[r.type].id,
                                     host_id=host.id,
                                     user_id=r.user_id,
                                     resource_id=r.resource_id,
                                     project_id=r.project_id,
                                     value=r.value,
                                     duration=r.duration,
                                     timestamp=r.timestamp,
                                     signature=message.signature)
                self.db.save(record)
                logger.debug("Message from %s: %s" % (host.name,record))
            except Exception:
                logger.debug('WARNING: failed to insert instance record %s' %
                             record)

        self.db.commit()
        self.db.session_close()
