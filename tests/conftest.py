from pytest import fixture
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import main
import db
import config

@fixture
def test_sess():
    test_engine = create_engine(config.get("database.url").get("test"), connect_args={"check_same_thread": False})
    db.init(test_engine)
    Session = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)
    def session():
        sess = Session()
        try:
            yield sess
        finally:
            sess.close()
    main.api.dependency_overrides[db.session] = session
    sess = Session()
    yield sess
    sess.close()
    db.drop(test_engine)
