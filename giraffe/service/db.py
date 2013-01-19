'''
Sets up database interaction with SQLAlchemy.

-- Usage example --
import giraffe.service.db as db
from giraffe.service.db import Meter, MeterRecord

# CREATE SESSION
db = db.connect('mysql://user:pwd@host/schema')
db.session_open()

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
db.session_close()
'''

from sqlalchemy import create_engine, Column, ForeignKey, desc, asc, and_
from sqlalchemy.orm import sessionmaker, relationship, class_mapper
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, VARCHAR, TIMESTAMP


def connect(connectStr):
    """
    Returns a Db object connected to the database.
    Expects the connection string in the format:
    "protocol://user:pwd@host/schema".
    """
    return Db(connectStr)


class Db(object):
    def __init__(self, connectStr):
        """
        Connects to the database using the given connection string of the
        format: protocol://user:pwd@host/schema
        """
        self._engine = create_engine(connectStr)
        self._Session = sessionmaker(bind=self._engine, autoflush=True,
                                     autocommit=False)
        self._session = None
        self._Session.configure(bind=self._engine)

    def session_open(self):
        '''
        Opens a database session.
        '''
        if self._session is None:
            self._session = self._Session()

    def session_close(self):
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

    def load(self, cls, args={}, limit=None, order=None, order_attr=None):
        """
        Loads all persistent objects of the given class that meet the given
        arguments.
        Meter objects are ordered by id descending.
        MeterRecord objects are ordered by timestamp descending.
        """
        query = None
        if cls == Meter:
            query = self._query_meter(args, order=order, order_attr=order_attr)
        elif cls == MeterRecord:
            query = self._query_meter_record(args, order=order,
                                             order_attr=order_attr)
        elif cls == Host:
            query = self._query_host(args, order=order, order_attr=order_attr)
        else:
            raise Exception('Db.load() cannot handle objects of class "%s"' %
                            cls)

        if query is not None:
            if limit is not None:
                query = query.limit(limit)
            #print query
            return query.all()
        else:
            return []

    def distinct_values(self, cls, column):
        """
        Returns a list of distinct values for the given object class and
        column.
        """
        values = self._session.query(getattr(cls, column)).distinct().all()
        return [tupl[0] for tupl in values]

    def delete(self, obj):
        """
        Deletes a single persistent object without committing.
        """
        self._session.delete(obj)

    def _query_meter_record(self, args, order='asc', order_attr='timestamp'):
        filter_args = {}
        start_time = None
        end_time = None
        for key in args:
            if key.lower() == 'timestamp':
                if type(args[key]) in (list, tuple):
                    start_time = args[key][0]
                    end_time = args[key][1]
                    continue
            if args[key] is not None:
                filter_args[key] = args[key]

        # no start and end time
        if start_time is None and end_time is None:
            query = self._session.query(MeterRecord).filter_by(**filter_args)
        # start and end time
        elif start_time is not None and end_time is not None:
            query = self._session.query(MeterRecord).filter_by(**filter_args).\
                        filter(and_(MeterRecord.timestamp >= start_time,
                               MeterRecord.timestamp <= end_time))

        if query is not None and order is not None:
            if order_attr is None:
                order_attr = 'timestamp'
            query = query.order_by(asc(getattr(MeterRecord, order_attr))
                           if order == 'asc'
                           else desc(getattr(MeterRecord, order_attr)))
        return query

    def _query_meter(self, args, order='asc', order_attr='id'):
        if order is not None:
            if order_attr is None:
                order_attr = 'id'
            return self._session.query(Meter).filter_by(**args).\
                        order_by(asc(getattr(Meter, order_attr))
                                 if order == 'asc'
                                 else desc(getattr(Meter, order_attr)))
        else:
            return self._session.query(Meter).filter_by(**args)

    def _query_host(self, args, order='asc', order_attr='id'):
        if order is not None:
            if order_attr is None:
                order_attr = 'id'
            return self._session.query(Host).filter_by(**args).\
                        order_by(asc(getattr(Host, order_attr))
                                 if order == 'asc'
                                 else desc(getattr(Host, order_attr)))
        else:
            return self._session.query(Host).filter_by(**args)


class GiraffeBase(object):

    def list_column_names(self, realname=True):
        """
        Returns a list of column names.
        If "realname" is True, the column names will be identical to the
        database table. If False, the colum names are the ones defined for the
        object.
        """
        if not realname:
            return [prop.key
                    for prop in class_mapper(type(self)).iterate_properties
                    if isinstance(prop, ColumnProperty)]
        else:
            return [name.key for name in type(self).__table__.columns]

    def to_dict(self):
        """
        Returns a dictionary of column names (as defined for the object) and
        their respective values.
        """
        columnNames = self.list_column_names(realname=False)
        columnDict = {}
        for name in columnNames:
            columnDict[name] = getattr(self, name)
            if isinstance(columnDict[name], object):
                columnDict[name] = str(columnDict[name])
        return columnDict


Base = declarative_base(cls=GiraffeBase)


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
        return "Meter(%s,'%s','%s','%s', '%s')" % (self.id,
                                                   self.name,
                                                   self.description,
                                                   self.unit_name,
                                                   self.data_type)


class Host(Base):
    __tablename__ = 'host'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mysql_charset': 'utf8'}

    id = Column(INTEGER(5, unsigned=True), primary_key=True)
    name = Column('host_name', VARCHAR(20), nullable=False,
                  doc='distinctive name of the physical machine, e.g. uncinus')
    activity = Column('activity', TIMESTAMP(), nullable=True, default=None)
    records = relationship('MeterRecord', backref='host')

    def __repr__(self):
        return "Host(%s,'%s')" % (self.id, self.name)


class MeterRecord(Base):
    __tablename__ = 'meter_record'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mysql_charset': 'utf8'}

    id = Column(INTEGER(unsigned=True), primary_key=True)
    meter_id = Column(TINYINT(2, unsigned=True),
                      ForeignKey('meter.id', name='fk_meter_record_meter_id',
                                 onupdate='CASCADE', ondelete='NO ACTION'),
                      nullable=False)
    host_id = Column(INTEGER(5, unsigned=True),
                     ForeignKey('host.id', name='fk_meter_record_host_id',
                                onupdate='CASCADE', ondelete='NO ACTION'),
                     nullable=False)
    user_id = Column(VARCHAR(40), nullable=True, default=None,
                     doc='keystone user ID')
    resource_id = Column(VARCHAR(40), nullable=True, default=None,
                     doc='nova instance ID')
    project_id = Column(VARCHAR(40), nullable=True, default=None)
    value = Column('meter_value', VARCHAR(255), nullable=False)
    duration = Column('meter_duration', INTEGER(unsigned=True),
                      nullable=False, default=0,
                      doc='duration of measurement in seconds')
    timestamp = Column('meter_timestamp', TIMESTAMP(), nullable=False,
                        default='CURRENT_TIMESTAMP')
    signature = Column('message_signature', VARCHAR(40),
                        nullable=True, default=None)

    def __repr__(self):
        return "MeterRecord(%s, %d,'%s','%s', %s)" % (self.id,
                                                      self.meter_id,
                                                      self.value,
                                                      self.duration,
                                                      self.timestamp)
