from pydantic import BaseModel
from datetime import datetime
from typing import List

class PhotoBase(BaseModel):
    filename: str
    person_id: int

class PhotoCreate(PhotoBase):
    pass

class Photo(PhotoBase):
    id: int
    upload_date: datetime

    class Config:
        orm_mode = True

class PersonBase(BaseModel):
    name: str

class PersonCreate(PersonBase):
    pass

class Person(PersonBase):
    id: int
    photo_count: int

    class Config:
        orm_mode = True

class PersonWithPhotos(Person):
    photos: List[Photo]