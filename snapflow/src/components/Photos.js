import React, { useState, useEffect, useCallback } from 'react';
import { DATABASE_URL } from '../constants';
import PhotoGallery from './PhotoGallery';
import './Photos.css';

const Photos = () => {
  const [photos, setPhotos] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  const fetchPhotos = useCallback(async () => {
    if (isLoading || !hasMore) return;
    setIsLoading(true);
    try {
      const response = await fetch(`${DATABASE_URL}/api/photos?page=${page}&per_page=60`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (!data || data.items.length === 0) {
        setHasMore(false);
      } else {
        const newPhotos = data.items.map(photo => ({
          src: `${process.env.REACT_APP_API_URL}${photo.file_path}`,
          thumbnail: `${process.env.REACT_APP_API_URL}${photo.file_path}`,
          thumbnailWidth: photo.width,
          thumbnailHeight: photo.height,
          caption: photo.date,
        }));
        setPhotos(prevPhotos => [...prevPhotos, ...newPhotos]);
        setPage(prevPage => prevPage + 1);
        setHasMore(data.page < data.total_pages);
      }
    } catch (error) {
      console.error('Error fetching photos:', error);
    } finally {
      setIsLoading(false);
    }
  }, [page, isLoading, hasMore]);

  useEffect(() => {
    fetchPhotos();
  }, []);

  const handleScroll = useCallback(() => {
    if (window.innerHeight + document.documentElement.scrollTop !== document.documentElement.offsetHeight) return;
    fetchPhotos();
  }, [fetchPhotos]);

  useEffect(() => {
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [handleScroll]);

  return <PhotoGallery photos={photos} isLoading={isLoading} hasMore={hasMore} />;
};

export default Photos;
