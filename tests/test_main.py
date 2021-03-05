from fastapi.testclient import TestClient
from pytest import fixture

from main import api

@fixture(scope="module", autouse=True)
def setup():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import config
    import db
    engine = create_engine(config.get("database.url").get("test"), connect_args={"check_same_thread": False})
    db.init(engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    def session():
        sess = Session()
        try:
            yield sess
        finally:
            sess.close()
    api.dependency_overrides[db.session] = session
    yield
    db.drop(engine)

client = TestClient(api)

def test_getItemList():
    res = client.get("/items")
    assert res.status_code == 200
