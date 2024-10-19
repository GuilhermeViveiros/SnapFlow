from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class PersonBase(BaseModel):
    name: Optional[str] = None
    embedding: Optional[str] = None

class PersonCreate(PersonBase):
    pass

class Person(PersonBase):
    id: int

    class Config:
        orm_mode = True

class PhotoBase(BaseModel):
    filename: str

class PhotoCreate(PhotoBase):
    person_ids: Optional[List[int]] = None

class Photo(PhotoBase):
    id: int
    upload_date: datetime
    persons: Optional[List[Person]] = None

    class Config:
        orm_mode = True