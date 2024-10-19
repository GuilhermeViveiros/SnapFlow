from sqlalchemy import create_engine, inspect
from db.models import Base, Person, Photo, Cluster
from constants import DATABASE_URL

engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

# Get table names
print("Tables:", inspector.get_table_names())

# Inspect each table
for table_name in inspector.get_table_names():
    print(f"\nTable: {table_name}")
    for column in inspector.get_columns(table_name):
        print(f"  Column: {column['name']}, Type: {column['type']}")

# Query data
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

"""
print("\nPerson data:")
for person in session.query(Person).all():
    print(person.to_dict())

print("\nCluster data:")
for cluster in session.query(Cluster).all():
    print(cluster.to_dict())
"""
print("\nPhoto data:")
for photo in session.query(Photo).all():
    print(photo.to_dict())
session.close()