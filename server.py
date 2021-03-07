from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from uuid import UUID
import logging

import model
import db

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
        logging.error(e)
        raise HTTPException(500, detail=[{"msg": repr(e), "type": "unknown_error"}])
    return item_bunch

def create_item(item:model.ItemCreate, sess:Session):
    try:
        db_item = db.Item(**item.dict())
        sess.add(db_item)
        sess.commit()
        sess.refresh(db_item)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(e)
        raise HTTPException(500, detail=[{"msg": repr(e), "type": "unknown_error"}])
    return db_item

def get_item(item_id:UUID, sess:Session):
    try:
        db_item = sess.query(db.Item).filter(db.Item.id == item_id).first()
        if db_item is None:
            raise HTTPException(404, [{"msg": "item(id=%s) is not found" % (item_id), "type": "logic_error"}])
    except HTTPException:
        raise
    except Exception as e:
        logging.error(e)
        raise HTTPException(500, detail=[{"msg": repr(e), "type": "unknown_error"}])
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
    except Exception as e:
        logging.error(e)
        raise HTTPException(500, detail=[{"msg": repr(e), "type": "unknown_error"}])
    return db_item

def delete_item(item_id:UUID, sess:Session):
    try:
        db_item = sess.query(db.Item).filter(db.Item.id == item_id).first()
        if db_item is None:
            raise HTTPException(404, [{"msg": "item(id=%s) is not found" % (item_id), "type": "logic_error"}])
        sess.delete(db_item)
        sess.commit()
    except HTTPException:
        raise
    except Exception as e:
        logging.error(e)
        raise HTTPException(500, detail=[{"msg": repr(e), "type": "unknown_error"}])
    return None
