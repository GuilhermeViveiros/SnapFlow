import React, { useState, useEffect } from 'react';
import { DATABASE_URL } from '../constants';
import { LazyLoadImage } from 'react-lazy-load-image-component';
import PhotoGallery from './PhotoGallery';
import './People.css';
import './Photos.css';

function People() {
  const [people, setPeople] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPerson, setSelectedPerson] = useState(null);
  const [editingName, setEditingName] = useState(false);
  const [newName, setNewName] = useState('');
  const [personPhotos, setPersonPhotos] = useState([]);
  const [hasMore, setHasMore] = useState(false);

  useEffect(() => {
    fetchPeople();
  }, []);

  const fetchPeople = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${DATABASE_URL}/api/people`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setPeople(data);
    } catch (error) {
      console.error('Error fetching people:', error);
      setError('Failed to fetch people. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePersonClick = async (person) => {
    setSelectedPerson(person);
    setNewName(person.name || `Person ${person.id}`);
    await fetchPersonPhotos(person.id);
  };

  const fetchPersonPhotos = async (personId) => {
    try {
      setIsLoading(true);
      const response = await fetch(`${DATABASE_URL}/api/people/${personId}/photos`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log("Raw data from backend:", data);
      const formattedPhotos = data.map(photo => {
        console.log("Processing photo:", photo);
        return {
          src: `${process.env.REACT_APP_API_URL}${photo.file_path}`,
          thumbnail: `${process.env.REACT_APP_API_URL}${photo.file_path}`,
          thumbnailWidth: 300, // You can adjust this value
          thumbnailHeight: 300, // You can adjust this value
          caption: photo.filename,
        };
      });
      console.log("Formatted photos:", formattedPhotos);
      setPersonPhotos(formattedPhotos);
      setHasMore(false); // Assuming we load all photos at once for a person
    } catch (error) {
      console.error('Error fetching person photos:', error);
      setError('Failed to fetch person photos. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditName = () => {
    setEditingName(true);
  };

  const handleSaveName = async () => {
    try {
      const response = await fetch(`${DATABASE_URL}/api/person/${selectedPerson.id}`, {
        method: 'PUT',  // Ensure the method is PUT
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newName,  // Override the name if it's being edited
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Update the person's name in the local state
      setPeople(people.map(p => 
        p.id === selectedPerson.id ? { ...p, name: newName } : p
      ));
      setSelectedPerson({ ...selectedPerson, name: newName });
      setEditingName(false);
    } catch (error) {
      console.error('Error updating name:', error);
      // You might want to show an error message to the user here
    }
  };

  if (isLoading && !selectedPerson) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  console.log("People:", people);

  return (
    <div className="people-container">
      {!selectedPerson ? (
        <div className="people-grid">
          {people.length === 0 ? (
            <div>No people found.</div>
          ) : (
            people.filter(person => person.photo_count > 0).map(person => (
              <div key={person.id} className="person-item" onClick={() => handlePersonClick(person)}>
                <p className="person-name">{person.name || `Person ${person.id}`}</p>
                {person.filename && (
                  <div className="circular-image">
                    <LazyLoadImage 
                      src={`${process.env.REACT_APP_API_URL}${person.file_path}`}
                      alt={person.name || `Person ${person.id}`}
                      effect="blur"
                    />
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      ) : (
        <div className="person-details">
          <div className="person-header">
            {editingName ? (
              <div>
                <input 
                  type="text" 
                  value={newName} 
                  onChange={(e) => setNewName(e.target.value)}
                />
                <button onClick={handleSaveName}>Save</button>
              </div>
            ) : (
              <div>
                <h2>{selectedPerson.name || `Person ${selectedPerson.id}`}</h2>
                <button onClick={handleEditName}>Edit Name</button>
              </div>
            )}
            <p>{selectedPerson.photo_count} photos</p>
            <button onClick={() => setSelectedPerson(null)}>Back to People</button>
          </div>
          <PhotoGallery photos={personPhotos} isLoading={isLoading} hasMore={hasMore} />
        </div>
      )}
    </div>
  );
}

export default People;
