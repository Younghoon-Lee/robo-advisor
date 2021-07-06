# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base
import os

dirname = os.path.abspath(os.path.dirname(__file__))

# db = SQLAlchemy()
print(dirname)

engine = create_engine(
    'sqlite+pysqlite:///'+dirname+'/main.db', future=True, echo=True)

with engine.connect() as conn:
    result = conn.execute(
        text("SELECT * FROM 안전추구형"))
    for row in result.mappings():
        print(row)

# Base = declarative_base()
# Base.metadata.create_all(engine)
# print(Base.metadata.tables)


# class Passive(Base):

#     __table__ = Base.metadata.tables['aggressive']


# if __name__ == '__main__':
#     from sqlalchemy.orm import scoped_session, sessionmaker, Query
#     db_session = scoped_session(sessionmaker(bind=engine))
#     for item in db_session.query(Passive.ticker, Passive.nameKo):
#         print(item)
