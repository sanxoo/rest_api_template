from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class ItemBase(BaseModel):
    title:str
    descr:Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

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
