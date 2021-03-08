from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class ItemBase(BaseModel):
    descr:Optional[str] = None

class ItemCreate(ItemBase):
    title:str

class ItemUpdate(ItemBase):
    title:Optional[str] = None

class Item(ItemUpdate):
    id:UUID
    created:datetime
    updated:datetime
    class Config:
        orm_mode = True

class ItemBunch(BaseModel):
    order_by:str
    offset:int
    limit:int
    total_count:int
    count:int
    list:List[Item]

class File(BaseModel):
    name:str
    created:datetime
    updated:datetime
    item_id:UUID
    class Config:
        orm_mode = True

class FileBunch(BaseModel):
    item_id:UUID
    offset:int
    limit:int
    total_count:int
    count:int
    list:List[File]
