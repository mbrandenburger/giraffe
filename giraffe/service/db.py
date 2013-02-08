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

from sqlalchemy import create_engine, Column, ForeignKey, desc, asc, and_, func
from sqlalchemy.orm import sessionmaker, relationship, class_mapper
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, VARCHAR, TIMESTAMP

MIN_TIMESTAMP = '0000-01-01 00:00:00'
MAX_TIMESTAMP = '2999-12-31 23:59:59'


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
        """
        query = self._query(cls, args, limit, order, order_attr)
        return query.all()

    def distinct_values(self, cls, column, order=None):
        """
        Returns a list of distinct values for the given object class and
        column.
        """
        query = self._session.query(getattr(cls, column))
        query = self._order(cls, query, order, column)
        values = query.distinct().all()
        return [tupl[0] for tupl in values]

    def count(self, cls, args={}):
        """
        Returns the number of all rows for the given object class.

        An optional dictionary "args" can be passed that contains column values
        which have to be matched (test for equality): the key is the column
        name and the value the column value to match.
        """
        pk = class_mapper(cls).primary_key[0].name
        query = self._session.query(func.count(getattr(cls, pk)))
        query = self._filter(cls, query, args)
        return query.first()[0]

    def max(self, cls, column, args={}):
        """
        Returns the maximum of column "column" of all rows for the given object
        class.
        An optional dictionary "args" can be passed to filter rows (see
        count()).
        """
        query = self._session.query(func.max(getattr(cls, column)))
        query = self._filter(cls, query, args)
        return query.first()[0]

    def max_row(self, cls, column, args={}):
        """
        Same as max(), except that the object with the maximum column value is
        returned.
        """
        result = self.load(cls, args, limit=1, order='desc', order_attr=column)
        return result[0] if result else None

    def min(self, cls, column, args={}):
        """
        Returns the minimum of column "column" of all rows for the given object
        class.
        An optional dictionary "args" can be passed to filter rows (see
        count()).
        """
        query = self._session.query(func.min(getattr(cls, column)))
        query = self._filter(cls, query, args)
        return query.first()[0]

    def min_row(self, cls, column, args={}):
        """
        Same as min(), except that the object with the minimum column value is
        returned.
        """
        result = self.load(cls, args, limit=1, order='asc', order_attr=column)
        return result[0] if result else None

    def avg(self, cls, column, args={}):
        """
        Returns the average of column "column" of all rows for the given object
        class.
        An optional dictionary "args" can be passed to filter rows (see
        count()).
        """
        query = self._session.query(func.avg(getattr(cls, column)))
        query = self._filter(cls, query, args)
        return query.first()[0]

    def delete(self, obj):
        """
        Deletes a single persistent object without committing.
        """
        self._session.delete(obj)

    def _pk(self, cls, full=False):
        """
        Returns the primary key of the object class denoted by "cls".
        If the PK is a composite key and "full" is True, then all Columns will
        be returned. Otherwise only the name of the first PK column is
        returned.
        """
        pk = class_mapper(cls).primary_key
        if not full:
            return pk[0].name
        return pk

    def _query(self, cls, args, limit=None, order=None, order_attr=None):
        """
        Returns a query object for the given arguments.
        """
        query = self._session.query(cls)
        # apply filters
        query = self._filter(cls, query, args)
        # apply order
        query = self._order(cls, query, order, order_attr)
        # apply limit
        if limit is not None:
            return query.limit(limit)
        return query

    def _filter(self, cls, query, args):
        """
        Applies filters to the given query object and returns it again.
        Columns can be tested for equality only, except for
        MeterRecord.timestamp, which can be tested for an interval if a tuple
        is given as value.
        """
        if cls == MeterRecord:
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
                query = query.filter_by(**filter_args)
            # start and end time
            elif start_time is not None and end_time is not None:
                query = query.filter_by(**filter_args).\
                            filter(and_(MeterRecord.timestamp >= start_time,
                                   MeterRecord.timestamp <= end_time))
            return query
        else:
            return query.filter_by(**args)

    def _order(self, cls, query, order, order_attr):
        """
        Applies order function to the query object and returns it again.
        If "order" is not specified, the result set will be ordered in its
        natural order. The "order" parameter can be either "asc" or "desc".
        By default, the order_attr is the primary key (first column in case of
        composite keys) if not specified otherwise.
        """
        if order is None:
            return query
        if order_attr is None:
            order_attr = self._pk(cls)
        return query.order_by(asc(getattr(cls, order_attr))
                               if order == 'asc'
                               else desc(getattr(cls, order_attr)))


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
    name = Column('meter_name', VARCHAR(80), nullable=False)
    description = Column('meter_desc', VARCHAR(255), nullable=False,
                         default='', doc='meter description')
    unit_name = Column('unit_name', VARCHAR(20), nullable=False,
                       doc='name of the unit of measurement, e.g. kb')
    data_type = Column('data_type', VARCHAR(20), nullable=False,
                       doc=('name of the python data type for casting,'
                            ' e.g. int, float..'))
    type = Column('meter_type', VARCHAR(40), nullable=False, \
                  doc='meter type, either gauge, cumulative or delta')
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
#    signature = Column('message_signature', VARCHAR(40),
#                        nullable=True, default=None)

    def __repr__(self):
        return "MeterRecord(%s, %d, %s, %s, %s)" % (self.id,
                                                    self.meter_id,
                                                    str(self.host_id)\
                                                        if self.host_id
                                                        else 'None',
                                                    self.value,
                                                    self.timestamp)
