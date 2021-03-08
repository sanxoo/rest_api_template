from fastapi.testclient import TestClient
from pytest import fixture

import main
import db

@fixture
def test_list(test_sess):
    items = [
        {"title": "item_1", "descr": "item 5"},
        {"title": "item_2", "descr": "item 4"},
        {"title": "item_3", "descr": "item 3"},
        {"title": "item_4", "descr": "item 2"},
        {"title": "item_5", "descr": "item 1"}
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
    test_title_list = [item["title"] for item in test_list]
    order_by = "descr desc"
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

def test_get_item_bunch_with_offset(test_list):
    test_list_count = len(test_list)
    test_title_list = [item["title"] for item in test_list]
    offset = 2
    res = client.get("/items", params={"offset": offset})
    assert res.status_code == 200
    res_bunch = res.json()
    assert res_bunch["order_by"] == "title"
    assert res_bunch["offset"] == 2
    assert res_bunch["limit"] == 20
    assert res_bunch["total_count"] == test_list_count
    assert res_bunch["count"] == test_list_count - offset
    item_list = res_bunch["list"]
    assert len(item_list) == test_list_count - offset
    assert [item["title"] for item in item_list] == test_title_list[offset:]

def test_get_item_bunch_with_limit(test_list):
    test_list_count = len(test_list)
    test_title_list = [item["title"] for item in test_list]
    limit = 2
    res = client.get("/items", params={"limit": limit})
    assert res.status_code == 200
    res_bunch = res.json()
    assert res_bunch["order_by"] == "title"
    assert res_bunch["offset"] == 0
    assert res_bunch["limit"] == 2
    assert res_bunch["total_count"] == test_list_count
    assert res_bunch["count"] == limit
    item_list = res_bunch["list"]
    assert len(item_list) == limit
    assert [item["title"] for item in item_list] == test_title_list[:limit]
