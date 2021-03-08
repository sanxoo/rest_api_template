from fastapi.testclient import TestClient
from pytest import fixture
from uuid import UUID, uuid4
from datetime import datetime

import main
import db

client = TestClient(main.api)

def test_item_basic_crud(test_sess):
    # create
    create_data = {"title": "item_1", "descr": "item 1"}
    res = client.post("/items", json=create_data)
    assert res.status_code == 201
    created_item = res.json()
    assert created_item["title"] == create_data["title"]
    assert created_item["descr"] == create_data["descr"]
    assert UUID(created_item["id"])
    assert datetime.fromisoformat(created_item["created"])
    assert datetime.fromisoformat(created_item["updated"])
    # get
    item_id = created_item["id"]
    res = client.get("/items/%s" % (item_id))
    assert res.status_code == 200
    assert res.json() == created_item
    # update
    patch_data = {"descr": "item 1 patch 1"}
    res = client.patch("/items/%s" % (item_id), json=patch_data)
    assert res.status_code == 200
    patched_item = res.json()
    assert patched_item["title"] == created_item["title"]
    assert patched_item["descr"] == patch_data["descr"]
    assert patched_item["id"] == item_id
    assert patched_item["created"] == created_item["created"]
    assert datetime.fromisoformat(patched_item["updated"]) > datetime.fromisoformat(created_item["updated"])
    # delete
    res = client.delete("/items/%s" % (item_id))
    assert res.status_code == 204
    assert res.text == ""

def test_item_create_with_duplicate(test_sess):
    create_data = {"title": "item_1", "descr": "item 1"}
    res = client.post("/items", json=create_data)
    assert res.status_code == 201
    res = client.post("/items", json=create_data)
    assert res.status_code == 409
    detail = res.json()["detail"][0]
    assert detail["msg"] != ""
    assert detail["type"] == "db_error"

def test_item_get_with_invalid_uuid(test_sess):
    item_id = "1"
    res = client.get("/items/%s" % (item_id))
    assert res.status_code == 422
    detail = res.json()["detail"][0]
    assert detail["msg"] != ""
    assert detail["type"] == "type_error.uuid"

def test_item_get_with_not_found_id(test_sess):
    item_id = str(uuid4())
    res = client.get("/items/%s" % (item_id))
    assert res.status_code == 404
    detail = res.json()["detail"][0]
    assert detail["msg"] != ""
    assert detail["type"] == "logic_error"

def test_item_update_with_duplicate(test_sess):
    create_data = {"title": "item_1", "descr": "item 1"}
    res = client.post("/items", json=create_data)
    assert res.status_code == 201
    create_data = {"title": "item_2", "descr": "item 2"}
    res = client.post("/items", json=create_data)
    assert res.status_code == 201
    item_id = res.json()["id"]
    patch_data = {"title": "item_1"}
    res = client.patch("/items/%s" % (item_id), json=patch_data)
    assert res.status_code == 409
    detail = res.json()["detail"][0]
    assert detail["msg"] != ""
    assert detail["type"] == "db_error"

def test_item_delete_with_not_found_id(test_sess):
    create_data = {"title": "item_1", "descr": "item 1"}
    res = client.post("/items", json=create_data)
    assert res.status_code == 201
    item_id = res.json()["id"]
    res = client.delete("/items/%s" % (item_id))
    assert res.status_code == 204
    assert res.text == ""
    res = client.delete("/items/%s" % (item_id))
    assert res.status_code == 404
    detail = res.json()["detail"][0]
    assert detail["msg"] != ""
    assert detail["type"] == "logic_error"

def test_item_delete_with_file(test_sess):

    item = {"title": "item_1", "descr": "item 1"}
    db_item = db.Item(**item)
    test_sess.add(db_item)
    test_sess.commit()
    test_sess.add(db.File(name="file_1", item_id=db_item.id))    
    test_sess.commit()

    res = client.delete("/items/%s" % (db_item.id))
    assert res.status_code == 409
    detail = res.json()["detail"][0]
    assert detail["msg"] != ""
    assert detail["type"] == "logic_error"
