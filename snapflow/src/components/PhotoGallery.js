import React from 'react';
import { Gallery } from "react-grid-gallery";
import './Photos.css';

const PhotoGallery = ({ photos, isLoading, hasMore }) => {
  console.log(photos);
  return (
    <div className="photos-container">
      <Gallery 
        images={photos}
        enableImageSelection={false}
        margin={5}
      />
      {isLoading && <div className="loading">Loading more photos...</div>}
      {!hasMore && <div className="no-more-photos">No more photos to load</div>}
    </div>
  );
};

export default PhotoGallery;
