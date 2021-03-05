from fastapi import FastAPI, Depends, Response
from sqlalchemy.orm import Session
from uuid import UUID

import model
import db
import server

api = FastAPI()

db.init()

@api.get("/items", status_code=200, response_model=model.ItemBunch)
def getItemBunch(order_by:str="title", offset:int=0, limit:int=20, sess:Session=Depends(db.session)):
    return server.getItemBunch(order_by, offset, limit, sess)

@api.post("/items", status_code=201, response_model=model.Item)
def createItem(item:model.ItemCreate, sess:Session=Depends(db.session)):
    return server.createItem(item, sess)

@api.get("/items/{item_id}", status_code=200, response_model=model.Item)
def getItem(item_id:UUID, sess:Session=Depends(db.session)):
    return server.getItem(item_id, sess)

@api.put("/items/{item_id}", status_code=200, response_model=model.Item)
def updateItem(item_id:UUID, item:model.ItemUpdate, sess:Session=Depends(db.session)):
    return server.updateItem(item_id, item, sess)

@api.delete("/items/{item_id}", status_code=204, response_class=Response)
def deleteItem(item_id:UUID, sess:Session=Depends(db.session)):
    return server.deleteItem(item_id, sess)

if __name__ == "__main__":
    import logging.config
    import config
    logging.config.dictConfig(config.get("log.config"))
    import uvicorn
    uvicorn.run(api, **config.get("run.args"))
