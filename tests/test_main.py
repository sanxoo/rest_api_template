from fastapi.testclient import TestClient
from pytest import fixture
from uuid import UUID
from datetime import datetime

import main
import db

@fixture
def test_sess():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import config
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

@fixture
def test_list(test_sess):
    items = [
        {"title": "item1", "descr": "item 5 description"},
        {"title": "item2", "descr": "item 4 description"},
        {"title": "item3", "descr": "item 3 description"},
        {"title": "item4", "descr": "item 2 description"},
        {"title": "item5", "descr": "item 1 description"}
    ]
    for item in items:
        test_sess.add(db.Item(**item))
    test_sess.commit()
    return items

client = TestClient(main.api)

def test_get_item_bunch(test_list):
    test_list_count = len(test_list)
    test_title_list = [item["title"] for item in test_list]
    res = client.get("/items")
    assert res.status_code == 200
    res_bunch = res.json()
    assert res_bunch["order_by"] == "title"
    assert res_bunch["offset"] == 0
    assert res_bunch["limit"] == 20
    assert res_bunch["total_count"] == test_list_count
    assert res_bunch["count"] == test_list_count
    item_list = res_bunch["list"]
    assert len(item_list) == test_list_count
    assert [item["title"] for item in item_list] == test_title_list

def test_get_item_bunch_with_order_by(test_list):
    test_list_count = len(test_list)
    test_title_list = [item["title"] for item in reversed(test_list)]
    order_by = "descr"
    res = client.get("/items", params={"order_by": order_by})
    assert res.status_code == 200
    res_bunch = res.json()
    assert res_bunch["order_by"] == order_by
    assert res_bunch["offset"] == 0
    assert res_bunch["limit"] == 20
    assert res_bunch["total_count"] == test_list_count
    assert res_bunch["count"] == test_list_count
    item_list = res_bunch["list"]
    assert len(item_list) == test_list_count
    assert [item["title"] for item in item_list] == test_title_list

def test_crud_item(test_sess):
    create_data = {"title": "item_1", "descr": "item 1"}
    res = client.post("/items", json=create_data)
    assert res.status_code == 201
    created_item = res.json()
    assert created_item["title"] == create_data["title"]
    assert created_item["descr"] == create_data["descr"]
    assert UUID(created_item["id"])
    assert datetime.fromisoformat(created_item["created"])
    assert datetime.fromisoformat(created_item["updated"])
    item_id = created_item["id"]
    res = client.get("/items/%s" % (item_id))
    assert res.status_code == 200
    assert res.json() == created_item
    patch_data = {"descr": "item 1 patch 1"}
    res = client.patch("/items/%s" % (item_id), json=patch_data)
    assert res.status_code == 200
    patched_item = res.json()
    assert patched_item["title"] == created_item["title"]
    assert patched_item["descr"] == patch_data["descr"]
    assert patched_item["id"] == item_id
    assert patched_item["created"] == created_item["created"]
    assert datetime.fromisoformat(patched_item["updated"]) > datetime.fromisoformat(created_item["updated"])
    res = client.delete("/items/%s" % (item_id))
    assert res.status_code == 204
    assert res.text == ""
