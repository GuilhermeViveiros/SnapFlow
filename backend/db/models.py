from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, PickleType, LargeBinary, func
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import pickle
import base64
from sqlalchemy import Table

Base = declarative_base()

# Define the association table
person_photo = Table(
    'person_photo', Base.metadata,
    Column('person_id', Integer, ForeignKey('person.id')),
    Column('photo_id', Integer, ForeignKey('photo.id'))
)

class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=True)
    file_path = Column(String(255), nullable=False)
    photos = relationship('Photo', secondary=person_photo, back_populates='persons')
    embeddings = Column(PickleType, nullable=False, default=pickle.dumps([]))
    cluster_id = Column(Integer, ForeignKey('cluster.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'photo_count': len(self.photos),
            'cluster_id': self.cluster_id,
            'file_path': self.file_path,
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
    upload_date = Column(DateTime, default=func.now())
    persons = relationship('Person', secondary=person_photo, back_populates='photos')

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'upload_date': self.upload_date.isoformat(),
            'person_count': len(self.persons),
            'file_path': "/assets/images/" + self.filename,
            'person_ids': [person.id for person in self.persons]  # Add this line
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
    person = relationship('Person', backref='cluster')

    def to_dict(self):
        return {
            'id': self.id,
            'person_count': len(self.persons)
        }

# Function to delete all tables
def _drop_tables(engine):
    Base.metadata.drop_all(engine)

if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from constants import DATABASE_URL
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    
    # Add dummy data
    photo1 = Photo(filename="snapflow.png", file_path="assets/images/snapflow.png")
    person1 = Person(name="John Doe", filename="john.jpg", embeddings=pickle.dumps([0.1, 0.2, 0.3]))
    cluster = Cluster(centroid=[0.1, 0.2, 0.3])
    
    session.add_all([photo1, person1, cluster])
    
    # Set up relationships
    photo1.persons.append(person1)
    person1.cluster = cluster
    
    session.commit()
    session.close()
