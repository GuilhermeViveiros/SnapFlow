from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session
from typing import List
import numpy as np
import os
from constants import DATABASE_URL
from db.database import SessionLocal, engine
from db import models, schemas
from utils.image import process_image, extract_face_embedding
from decorators import log_route_call

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "assets")
app.mount("/assets", StaticFiles(directory=static_dir), name="assets")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

@app.post("/api/upload")
@log_route_call
async def upload_photo(photo: UploadFile = File(...), db: Session = Depends(get_db)):
    person_ids = process_image(photo.file)
    
    new_photo = models.Photo(filename=photo.filename)
    db.add(new_photo)
    
    if person_ids:
        for person_id in person_ids:
            person = db.query(models.Person).filter(models.Person.id == person_id).first()
            if not person:
                person = models.Person()
                db.add(person)
            new_photo.persons.append(person)
    
    db.commit()
    db.refresh(new_photo)
    
    return {"message": "Photo uploaded successfully"}

@app.post("/api/person")
@log_route_call
async def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    db_person = models.Person(**person.dict())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

@app.put("/api/person/{person_id}")
@log_route_call
async def update_person_name(person_id: int, person: schemas.PersonCreate, db: Session = Depends(get_db)):
    db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    setattr(db_person, "name", person.name)
    db.commit()
    db.refresh(db_person)
    return {"message": "Person updated successfully"}

@app.get("/api/photos")
async def get_photos(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):  
    # db.query(models.Photo).all()
    return models.Photo.get_paginated(db, page=page, per_page=per_page) 


@app.get("/api/people")
async def get_people(db: Session = Depends(get_db)):
    people = db.query(models.Person).all()
    return [person.to_dict() for person in people]

@app.get("/api/people/{id}/photos", response_model=List[schemas.Photo])
async def get_person_photos(id: int, db: Session = Depends(get_db)):
    person = db.query(models.Person).filter(models.Person.id == id).first()
    if person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return person.photos

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
