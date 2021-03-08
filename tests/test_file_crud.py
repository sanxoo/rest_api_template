from fastapi.testclient import TestClient
from pytest import fixture
from datetime import datetime
import os

import main
import db
import config

@fixture
def test_item_id(test_sess):
    item = {"title": "item_1", "descr": "item 1"}
    db_item = db.Item(**item)
    test_sess.add(db_item)
    test_sess.commit()
    return str(db_item.id)

@fixture
def test_file():
    import tempfile
    with tempfile.TemporaryFile() as file:
        yield file

client = TestClient(main.api)

def test_file_basic_crud(test_item_id, test_file):
    # create
    file_name = "test.csv"
    test_data = b"1,2,3,4"
    test_file.write(test_data)
    test_file.seek(0)
    res = client.post("/items/%s/files" % (test_item_id), files={"upload_file": (file_name, test_file)})
    assert res.status_code == 201
    created_file = res.json()
    assert created_file["name"] == file_name
    assert datetime.fromisoformat(created_file["created"])
    assert datetime.fromisoformat(created_file["updated"])
    assert created_file["item_id"] == test_item_id
    fullname = os.path.join(config.get("file.path"), file_name)
    assert os.path.exists(fullname)
    # get
    res = client.get("/items/%s/files/%s" % (test_item_id, file_name))
    assert res.status_code == 200
    assert res.content == test_data
    # delete
    res = client.delete("/items/%s/files/%s" % (test_item_id, file_name))
    assert res.status_code == 204
    assert res.text == ""
    assert not os.path.exists(fullname)
