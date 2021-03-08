from fastapi import FastAPI, Depends, Response, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from uuid import UUID

import model
import db
import server

api = FastAPI()

@api.get("/items", status_code=200, response_model=model.ItemBunch)
def get_item_bunch(order_by:str="title", offset:int=0, limit:int=20, sess:Session=Depends(db.session)):
    return server.get_item_bunch(order_by, offset, limit, sess)

@api.post("/items", status_code=201, response_model=model.Item)
def create_item(item:model.ItemCreate, sess:Session=Depends(db.session)):
    return server.create_item(item, sess)

@api.get("/items/{item_id}", status_code=200, response_model=model.Item)
def get_item(item_id:UUID, sess:Session=Depends(db.session)):
    return server.get_item(item_id, sess)

@api.patch("/items/{item_id}", status_code=200, response_model=model.Item)
def update_item(item_id:UUID, item:model.ItemUpdate, sess:Session=Depends(db.session)):
    return server.update_item(item_id, item, sess)

@api.delete("/items/{item_id}", status_code=204, response_class=Response)
def delete_item(item_id:UUID, sess:Session=Depends(db.session)):
    return server.delete_item(item_id, sess)

@api.get("/items/{item_id}/files", status_code=200, response_model=model.FileBunch)
def get_file_bunch(item_id:UUID, offset:int=0, limit:int=20, sess:Session=Depends(db.session)):
    return server.get_file_bunch(item_id, offset, limit, sess)

@api.delete("/items/{item_id}/files", status_code=204, response_class=Response)
def delete_file_bunch(item_id:UUID, sess:Session=Depends(db.session)):
    return server.delete_file_bunch(item_id, sess)

@api.post("/items/{item_id}/files", status_code=201, response_model=model.File)
def create_file(item_id:UUID, upload_file:UploadFile=File(...), sess:Session=Depends(db.session)):
    return server.create_file(item_id, upload_file, sess)

@api.get("/items/{item_id}/files/{file_name}", status_code=200, response_class=FileResponse)
def get_file(item_id:UUID, file_name:str, sess:Session=Depends(db.session)):
    return server.get_file(item_id, file_name, sess)

@api.delete("/items/{item_id}/files/{file_name}", status_code=204, response_class=Response)
def delete_file(item_id:UUID, file_name:str, sess:Session=Depends(db.session)):
    return server.delete_file(item_id, file_name, sess)

if __name__ == "__main__":
    import logging.config
    import uvicorn
    import config
    logging.config.dictConfig(config.get("log.config"))
    db.init()
    uvicorn.run(api, **config.get("run.args"))
