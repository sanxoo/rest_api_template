from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from uuid import UUID
import logging
import os

import model
import db
import config

def get_item_bunch(order_by:str, offset:int, limit:int, sess:Session):
    try:
        db_item_list = sess.query(db.Item).order_by(text(order_by)).offset(offset).limit(limit).all()
        item_bunch = model.ItemBunch(
            order_by = order_by,
            offset = offset,
            limit = limit,
            total_count = sess.query(func.count(db.Item.id)).scalar(),
            count = len(db_item_list),
            list = db_item_list
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(e); raise HTTPException(500, detail=[{"msg": repr(e), "type": "unknown_error"}])
    return item_bunch

def create_item(item:model.ItemCreate, sess:Session):
    try:
        db_item = db.Item(**item.dict())
        sess.add(db_item)
        sess.commit()
        sess.refresh(db_item)
    except HTTPException:
        raise
    except DBAPIError as e:
        logging.error(e); raise HTTPException(409, detail=[{"msg": repr(e), "type": "db_error"}])
    except Exception as e:
        logging.error(e); raise HTTPException(500, detail=[{"msg": repr(e), "type": "unknown_error"}])
    return db_item

def get_item(item_id:UUID, sess:Session):
    try:
        db_item = sess.query(db.Item).filter(db.Item.id == item_id).first()
        if db_item is None:
            raise HTTPException(404, [{"msg": "item(id=%s) is not found" % (item_id), "type": "logic_error"}])
    except HTTPException:
        raise
    except Exception as e:
        logging.error(e); raise HTTPException(500, detail=[{"msg": repr(e), "type": "unknown_error"}])
    return db_item

def update_item(item_id:UUID, item:model.ItemUpdate, sess:Session):
    try:
        db_item = sess.query(db.Item).filter(db.Item.id == item_id).first()
        if db_item is None:
            raise HTTPException(404, [{"msg": "item(id=%s) is not found" % (item_id), "type": "logic_error"}])
        for key, value in item.dict().items():
            if value is not None: setattr(db_item, key, value)
        sess.commit()
        sess.refresh(db_item)
    except HTTPException:
        raise
    except DBAPIError as e:
        logging.error(e); raise HTTPException(409, detail=[{"msg": repr(e), "type": "db_error"}])
    except Exception as e:
        logging.error(e); raise HTTPException(500, detail=[{"msg": repr(e), "type": "unknown_error"}])
    return db_item

def delete_item(item_id:UUID, sess:Session):
    try:
        db_item = sess.query(db.Item).filter(db.Item.id == item_id).first()
        if db_item is None:
            raise HTTPException(404, [{"msg": "item(id=%s) is not found" % (item_id), "type": "logic_error"}])
        db_file_count = sess.query(db.File).filter(db.File.item_id == item_id).count()
        if 0 < db_file_count:
            raise HTTPException(409, [{"msg": "must delete file(item_id=%s)s first" % (item_id), "type": "logic_error"}])
        sess.delete(db_item)
        sess.commit()
    except HTTPException:
        raise
    except Exception as e:
        logging.error(e); raise HTTPException(500, detail=[{"msg": repr(e), "type": "unknown_error"}])
    return None

def get_file_bunch(item_id:UUID, offset:int, limit:int, sess:Session):
    try:
        db_file_list = sess.query(db.File).filter(db.File.item_id == item_id).order_by(db.File.name).offset(offset).limit(limit).all()
        file_bunch = model.FileBunch(
            item_id = item_id,
            offset = offset,
            limit = limit,
            total_count = sess.query(db.File).filter(db.File.item_id == item_id).count(),
            count = len(db_file_list),
            list = db_file_list
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(e); raise HTTPException(500, detail=[{"msg": repr(e), "type": "unknown_error"}])
    return file_bunch

def delete_file_bunch(item_id:UUID, sess:Session):
    try:
        db_item = sess.query(db.Item).filter(db.Item.id == item_id).first()
        if db_item is None:
            raise HTTPException(404, [{"msg": "item(id=%s) is not found" % (item_id), "type": "logic_error"}])
        db_file_list = sess.query(db.File).filter(db.File.item_id == item_id).all()
        for db_file in db_file_list:
            fullname = os.path.join(config.get("file.path"), db_file.name)
            if os.path.exists(fullname): os.remove(fullname)
            sess.delete(db_file)
        sess.commit()
    except HTTPException:
        raise
    except DBAPIError as e:
        logging.error(e); raise HTTPException(409, detail=[{"msg": repr(e), "type": "db_error"}])
    except Exception as e:
        logging.error(e); raise HTTPException(500, detail=[{"msg": repr(e), "type": "unknown_error"}])
    return None

def create_file(item_id:UUID, upload_file:UploadFile, sess:Session):
    try:
        db_item = sess.query(db.Item).filter(db.Item.id == item_id).first()
        if db_item is None:
            raise HTTPException(404, [{"msg": "item(id=%s) is not found" % (item_id), "type": "logic_error"}])
        fullname = os.path.join(config.get("file.path"), upload_file.filename)
        if os.path.exists(fullname):
            raise HTTPException(409, detail=[{"msg": "file %s is already exists" % (upload_file.filename), "type": "logic_error"}])
        with open(fullname, "wb") as file:
            file.write(upload_file.file.read())
        db_file = db.File(item_id=item_id, name=upload_file.filename)
        sess.add(db_file)
        sess.commit()
        sess.refresh(db_file)
    except HTTPException:
        raise
    except DBAPIError as e:
        logging.error(e); raise HTTPException(409, detail=[{"msg": repr(e), "type": "db_error"}])
    except Exception as e:
        logging.error(e); raise HTTPException(500, detail=[{"msg": repr(e), "type": "unknown_error"}])
    return db_file

def get_file(item_id:UUID, file_name:str, sess:Session):
    try:
        db_file = sess.query(db.File).filter(db.File.item_id == item_id).filter(db.File.name == file_name).first()
        if db_file is None:
            raise HTTPException(404, [{"msg": "file(item_id=%s, name=%s) is not found" % (item_id, file_name), "type": "logic_error"}])
        fullname = os.path.join(config.get("file.path"), file_name)
        if not os.path.exists(fullname):
            raise HTTPException(409, detail=[{"msg": "file %s is not exists" % (file_name), "type": "logic_error"}])
    except HTTPException:
        raise
    except Exception as e:
        logging.error(e); raise HTTPException(500, detail=[{"msg": repr(e), "type": "unknown_error"}])
    return FileResponse(fullname, filename=file_name)

def delete_file(item_id:UUID, file_name:str, sess:Session):
    try:
        db_file = sess.query(db.File).filter(db.File.item_id == item_id).filter(db.File.name == file_name).first()
        if db_file is None:
            raise HTTPException(404, [{"msg": "file(item_id=%s, name=%s) is not found" % (item_id, file_name), "type": "logic_error"}])
        fullname = os.path.join(config.get("file.path"), file_name)
        if os.path.exists(fullname): os.remove(fullname)
        sess.delete(db_file)
        sess.commit()
    except HTTPException:
        raise
    except Exception as e:
        logging.error(e); raise HTTPException(500, detail=[{"msg": repr(e), "type": "unknown_error"}])
    return None
