from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime
from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE
from datetime import datetime
from sqlalchemy.orm import sessionmaker

import config

engine = create_engine(config.get("database.url"), connect_args={"check_same_thread": False})

Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(GUID, primary_key=True, default=GUID_DEFAULT_SQLITE)
    title = Column(String)
    descr = Column(String)
    created = Column(DateTime, default=datetime.now)
    updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)

def init():
    Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def session():
    sess = Session()
    try:
        yield sess
    finally:
        sess.close()
