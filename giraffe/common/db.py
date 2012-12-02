'''
Sets up database interaction with SQLAlchemy.

-- Usage example --
from giraffe.common.db import Session, Meter, MeterRecord

# CREATE SESSION
session = Session()

# INSERT
# Id is set explicitly only for the sake of the example.
meter = Meter(id=99, name='test_meter', unit_name='kb', data_type='int')
record = MeterRecord(meter_id=99, host_id='fakehost', message_id='ABCDE',
                     value=10, timestamp='2012-12-01 12:00:00')

session.add(meter)
session.add(record)
# We could also turn off autoflush, call session.flush() instead of
# commit() and use just one transaction for the whole example.
# Continued use of session after commit() will create a new transaction.
session.commit()

# Exceptions could be thrown any time which could leave the database
# in an inconsistent state.
err_record = MeterRecord(meter_id=0)
try:
    session.add(err_record)
    session.commit()
except Exception:
    session.rollback()

# UPDATE
print meter, record
meter.name = 'test_meter_updated'
record.value = 20
session.commit()

# QUERY
meters = session.query(Meter).filter_by(name='test_meter_updated').all()
for m in meters:
    print m
    print m.records

record = session.query(MeterRecord).first()
print record
print record.meter

# DELETE
session.delete(meters[0])
session.delete(record)
session.commit()

# CLOSE SESSION
session.close()
'''

from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, VARCHAR, TIMESTAMP

# Session is supposed to be global to the application, see:
# http://docs.sqlalchemy.org/en/rel_0_7/orm/session.html#session-faq
Session = sessionmaker()

_engine = create_engine('mysql://giraffedbadmin:aff3nZo0@127.0.0.1/giraffe')

Session.configure(bind=_engine)

_Base = declarative_base()


class Meter(_Base):
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


class MeterRecord(_Base):
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

_Base.metadata.create_all(_engine)
