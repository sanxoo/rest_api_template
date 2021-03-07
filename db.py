from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime
from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config

Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(GUID, primary_key=True, default=GUID_DEFAULT_SQLITE)
    title = Column(String, nullable=False, unique=True)
    descr = Column(String)
    created = Column(DateTime, default=datetime.now)
    updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)

real_engine = create_engine(config.get("database.url").get("real"), connect_args={"check_same_thread": False})

def init(engine=real_engine):
    Base.metadata.create_all(bind=engine)

def drop(engine=real_engine):
    Base.metadata.drop_all(bind=engine)

Session = sessionmaker(bind=real_engine, autocommit=False, autoflush=False)

def session():
    sess = Session()
    try:
        yield sess
    finally:
        sess.close()
