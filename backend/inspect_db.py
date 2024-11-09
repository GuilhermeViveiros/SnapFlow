from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from db.models import Base, Person, Photo, Cluster
from constants import DATABASE_URL

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def get_table_names():
    inspector = inspect(engine)
    return inspector.get_table_names()

def inspect_tables():
    inspector = inspect(engine)
    for table_name in inspector.get_table_names():
        print(f"\nTable: {table_name}")
        for column in inspector.get_columns(table_name):
            print(f"  Column: {column['name']}, Type: {column['type']}")

def print_photo_data():
    session = Session()
    print("\nPhoto data:")
    for photo in session.query(Photo).all():
        print(photo.to_dict())
    session.close()

def get_person_photos(person_id):
    session = Session()
    person = session.query(Person).filter(Person.id == person_id).first()
    if person:
        photos = [photo.to_dict() for photo in person.photos]
        session.close()
        return photos
    session.close()
    return None

def main():
    print("Tables:", get_table_names())
    inspect_tables()
    print_photo_data()

    # Example usage of get_person_photos
    person_id = 1  # Replace with an actual person_id
    person_photos = get_person_photos(person_id)
    if person_photos:
        print(f"\nPhotos for person with id {person_id}:")
        for photo in person_photos:
            print(photo)
    else:
        print(f"\nNo photos found for person with id {person_id}")

if __name__ == "__main__":
    main()