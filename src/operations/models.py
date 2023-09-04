from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP

from database import metadata

operation = Table(
    'operation',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('quantity', String),
    Column('figi', String),
    Column('instrument_type', String, nullable=True),
    Column('data', TIMESTAMP),
    Column('type', String),
)
