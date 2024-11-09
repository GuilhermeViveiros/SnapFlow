# curl @app.get("/api/people/{id}/photos", response_model=List[schemas.Photo])

curl -X GET http://localhost:8000/api/people/1/photos