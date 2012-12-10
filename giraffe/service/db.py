'''
Sets up database interaction with SQLAlchemy.

Tests located in test_db.py

-- Usage example --
from giraffe.common.db import Connection, Meter, MeterRecord

# CREATE SESSION
db = Connection('mysql://user:pwd@host/schema')
db.sessionOpen()

# INSERT
# Id is set explicitly only for the sake of the example.
meter = Meter(id=99, name='test_meter', unit_name='kb', data_type='int')
record = MeterRecord(meter_id=99, host_id='fakehost', message_id='ABCDE',
                     value=10, timestamp='2012-12-01 12:00:00')

db.save(meter)
db.save(record)
db.commit()

# Exceptions could be thrown any time which could leave the database
# in an inconsistent state.
err_record = MeterRecord(meter_id=0)
try:
    db.save(err_record)
    db.commit()
except Exception:
    db.rollback()

# UPDATE
print meter, record
meter.name = 'test_meter_updated'
record.value = 20
db.commit()

# QUERY
meters = db.load(Meter, {'name': 'test_meter_updated'})
for m in meters:
    print m
    print m.records

record = db.load(MeterRecord, limit=1)[0]
print record
print record.meter

# DELETE
db.delete(meters[0])
db.delete(record)
db.commit()

# CLOSE SESSION
db.sessionClose()
'''

from sqlalchemy import create_engine, Column, ForeignKey, desc
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, VARCHAR, TIMESTAMP


class Connection(object):
    def __init__(self, connectString):
        '''
        Connects to the database using the given connection string.
        The connection string should be of the format:
        protocol://user:pwd@host/schema
        '''
        self._engine = create_engine(connectString)
        self._Session = sessionmaker(bind=self._engine, autoflush=True,
                                     autocommit=False)
        self._session = None
        self._Session.configure(bind=self._engine)

    def sessionOpen(self):
        '''
        Opens a database session.
        '''
        if self._session is None:
            self._session = self._Session()

    def sessionClose(self):
        '''
        Closes a database session.
        '''
        self._session.close()

    def commit(self):
        '''
        Commits the current transaction.
        '''
        self._session.commit()

    def rollback(self):
        '''
        Rolls back the current transaction.
        '''
        self._session.rollback()

    def save(self, obj):
        '''
        Inserts or updates a single persistent object without committing.
        The object is only updated if it previously was retrieved from the
        database.
        '''
        self._session.add(obj)

    def load(self, cls, args={}, limit=None):
        """
        Loads all persistent objects of the given class that meet the given
        arguments.
        Meter objects are ordered by id descending.
        MeterRecord objects are ordered by timestamp descending.
        """
        query = None
        if cls == Meter:
            query = self._query_meter(args)
        elif cls == MeterRecord:
            query = self._query_meter_record(args)

        if query is not None:
            if limit is not None:
                query = query.limit(limit)
            return query.all()
        else:
            return []

    def delete(self, obj):
        """
        Deletes a single persistent object without committing.
        """
        self._session.delete(obj)

    def _query_meter_record(self, args):
        filter_args = {}
        start_time = None
        end_time = None
        for key in args:
            if key.lower() == 'timestamp':
                if not isinstance(key, basestring):
                    start_time = args[0]
                    end_time = args[1]
                    continue
            if args[key] is not None:
                filter_args[key] = args[key]

        query = None
        # no start and end time
        if start_time is None and end_time is None:
            query = self._session.query(MeterRecord).filter_by(**filter_args)
        # either a start or an end end time or both
        elif start_time is not None and end_time is not None:
            query = self._session.query(MeterRecord).filter_by(**args).\
                        filter(MeterRecord.timestamp >= start_time,
                               MeterRecord.timestamp <= end_time)
        elif start_time is not None:
            query = self._session.query(MeterRecord).filter_by(**args).\
                        filter(MeterRecord.timestamp >= start_time)
        elif end_time is not None:
            query = self._session.query(MeterRecord).filter_by(**args).\
                            filter(MeterRecord.timestamp <= end_time)

        if query is not None:
            query.order_by(desc(MeterRecord.timestamp))
        return query

    def _query_meter(self, args):
        return self._session.query(Meter).filter_by(**args).\
                        order_by(desc(Meter.id))


class GiraffeBase(object):
    pass


Base = declarative_base(cls=GiraffeBase)
#Base.metadata.create_all(_engine)


class Meter(Base):
    __tablename__ = 'meter'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mysql_charset': 'utf8'}

    id = Column(TINYINT(2, unsigned=True), primary_key=True)
    name = Column('meter_name', VARCHAR(20), nullable=False)
    description = Column('meter_desc', VARCHAR(255), nullable=False,
                         default='', doc='meter description')
    unit_name = Column('unit_name', VARCHAR(20), nullable=False,
                       doc='name of the unit of measurement, e.g. kb')
    data_type = Column('data_type', VARCHAR(20), nullable=False,
                       doc=('name of the python data type for casting,'
                            ' e.g. int, float..'))
    records = relationship('MeterRecord', backref='meter')

    def __repr__(self):
        return "<Meter(%s,'%s','%s','%s', '%s')" % (self.id,
                                                    self.name,
                                                    self.description,
                                                    self.unit_name,
                                                    self.data_type)


class MeterRecord(Base):
    __tablename__ = 'meter_record'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mysql_charset': 'utf8'}

    id = Column(INTEGER(unsigned=True), primary_key=True)
    meter_id = Column(TINYINT(2, unsigned=True),
                      ForeignKey('meter.id', name='fk_meter_record_meter_id',
                                 onupdate='CASCADE', ondelete='NO ACTION'),
                      nullable=False)
    host_id = Column(VARCHAR(40), nullable=False,
                     doc='distinctive name of the physical machine')
    user_id = Column(VARCHAR(40), nullable=True, default=None,
                     doc='keystone user ID')
    resource_id = Column(VARCHAR(40), nullable=True, default=None,
                     doc='nova instance ID')
    project_id = Column(VARCHAR(40), nullable=True, default=None)
    message_id = Column(VARCHAR(40), nullable=False,
                        doc='RabbitMQ message identifier')
    value = Column('meter_value', VARCHAR(255), nullable=False)
    duration = Column('meter_duration', INTEGER(unsigned=True),
                      nullable=False, default=0,
                      doc='duration of measurement in seconds')
    timestamp = Column('meter_timestamp', TIMESTAMP(), nullable=False,
                        default='CURRENT_TIMESTAMP')
    signature = Column('message_signature', VARCHAR(40),
                        nullable=True, default=None)

    def __repr__(self):
        return "<MeterRecord(%s, %d,'%s','%s', %s)" % (self.id,
                                                       self.meter_id,
                                                       self.value,
                                                       self.duration,
                                                       self.timestamp)
