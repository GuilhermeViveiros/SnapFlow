from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, PickleType, LargeBinary, func
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import pickle
import base64

Base = declarative_base()

class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=True)
    filename = Column(String(255))  # New field for person's image
    photos = relationship('Photo', back_populates='person')
    embeddings = Column(PickleType, nullable=False, default=pickle.dumps([]))  # Use PickleType to store arrays, not nullable with empty list as default
    cluster_id = Column(Integer, ForeignKey('cluster.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'photo_count': len(self.photos),
            'cluster_id': self.cluster_id,
            'filename': "/assets/images/" + self.filename,
            #'embeddings': pickle.loads(self.embeddings)
        }

    @classmethod
    def get_paginated(cls, session, page=1, per_page=10):
        query = session.query(cls)
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        return {
            'items': [item.to_dict() for item in items],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }

class Photo(Base):
    __tablename__ = 'photo'
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    # photo_data = Column(LargeBinary)
    upload_date = Column(DateTime, default=func.now())
    person_id = Column(Integer, ForeignKey('person.id'))
    person = relationship('Person', back_populates='photos')

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'upload_date': self.upload_date.isoformat(),
            'person_id': self.person_id,
            'file_path': "/assets/images/" + self.filename
            # self.file_path  # Include the file path
        }

    @classmethod
    def get_paginated(cls, session, page, per_page):
        query = session.query(cls)
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        return {
            'items': [item.to_dict() for item in items],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }

class Cluster(Base):
    __tablename__ = 'cluster'
    id = Column(Integer, primary_key=True)
    centroid = Column(JSON)  # Store centroid as JSON
    persons = relationship('Person', backref='cluster')

    def to_dict(self):
        return {
            'id': self.id,
            'person_count': len(self.persons)
        }

# delete all tables
def _drop_tables(engine):
    Base.metadata.drop_all(engine)

if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from constants import DATABASE_URL
    # Create an engine and add dummy data
    engine = create_engine(DATABASE_URL)
    # _drop_tables(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    # Add dummy data, Person, Photo, Cluster    
    # Read image and convert to binary
    with open("snapflow.png", "rb") as image_file:
        image_binary = image_file.read()
    
    photo = Photo(filename="snapflow.png", file_path="snapflow.png")
    person = Person(name="John Doe", filename="john_gui.jpg", embeddings=pickle.dumps([0.1, 0.2, 0.3]))
    cluster = Cluster(centroid=[0.1, 0.2, 0.3])
    session.add(photo)
    session.add(person)
    session.add(cluster)
    # Add relationships
    photo.person = person
    person.cluster = cluster
    # Commit and close
    session.commit()
    session.close()
