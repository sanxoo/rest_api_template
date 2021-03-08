from fastapi.testclient import TestClient
from pytest import fixture

import main
import db

@fixture
def test_list(test_sess):
    item = {"title": "item_1", "descr": "item 1"}
    db_item = db.Item(**item)
    test_sess.add(db_item)
    test_sess.commit()
    files = [
        {"name": "file_1", "item_id": db_item.id},
        {"name": "file_2", "item_id": db_item.id},
        {"name": "file_3", "item_id": db_item.id},
        {"name": "file_4", "item_id": db_item.id},
        {"name": "file_5", "item_id": db_item.id}
    ]
    for file in files:
        test_sess.add(db.File(**file))
    test_sess.commit()
    return str(db_item.id), files

client = TestClient(main.api)

def test_get_file_bunch(test_list):
    test_item_id, files = test_list
    test_list_count = len(files)
    res = client.get("/items/%s/files" % (test_item_id))
    assert res.status_code == 200
    res_bunch = res.json()
    assert res_bunch["item_id"] == test_item_id
    assert res_bunch["offset"] == 0
    assert res_bunch["limit"] == 20
    assert res_bunch["total_count"] == test_list_count
    assert res_bunch["count"] == test_list_count
    item_list = res_bunch["list"]
    assert len(item_list) == test_list_count

def test_get_file_bunch_with_offset(test_list):
    test_item_id, files = test_list
    test_list_count = len(files)
    offset = 2
    res = client.get("/items/%s/files" % (test_item_id), params={"offset": offset})
    assert res.status_code == 200
    res_bunch = res.json()
    assert res_bunch["item_id"] == test_item_id
    assert res_bunch["offset"] == 2
    assert res_bunch["limit"] == 20
    assert res_bunch["total_count"] == test_list_count
    assert res_bunch["count"] == test_list_count - offset
    item_list = res_bunch["list"]
    assert len(item_list) == test_list_count - offset

def test_get_file_bunch_with_limit(test_list):
    test_item_id, files = test_list
    test_list_count = len(files)
    limit = 2
    res = client.get("/items/%s/files" % (test_item_id), params={"limit": limit})
    assert res.status_code == 200
    res_bunch = res.json()
    assert res_bunch["item_id"] == test_item_id
    assert res_bunch["offset"] == 0
    assert res_bunch["limit"] == 2
    assert res_bunch["total_count"] == test_list_count
    assert res_bunch["count"] == limit
    item_list = res_bunch["list"]
    assert len(item_list) == limit

def test_delete_file_bunch(test_list):
    test_item_id, files = test_list
    test_list_count = len(files)
    res = client.get("/items/%s/files" % (test_item_id))
    assert res.status_code == 200
    res_bunch = res.json()
    assert res_bunch["total_count"] == test_list_count
    assert res_bunch["count"] == test_list_count
    item_list = res_bunch["list"]
    assert len(item_list) == test_list_count
    res = client.delete("/items/%s/files" % (test_item_id))
    assert res.status_code == 204
    assert res.text == ""
    res = client.get("/items/%s/files" % (test_item_id))
    assert res.status_code == 200
    res_bunch = res.json()
    assert res_bunch["total_count"] == 0
    assert res_bunch["count"] == 0
    item_list = res_bunch["list"]
    assert len(item_list) == 0
