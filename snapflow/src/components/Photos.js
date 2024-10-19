import React, { useState, useEffect, useCallback, useRef } from 'react';
import { DATABASE_URL } from '../constants';
import { LazyLoadImage } from 'react-lazy-load-image-component';
import 'react-lazy-load-image-component/src/effects/blur.css';

const PhotoImage = ({ photo, style }) => {

  const [error, setError] = useState(false);

  return (
    <LazyLoadImage
    src={`${process.env.REACT_APP_API_URL}${photo.file_path}`}
      alt={`Photo ${photo.id}`}
      effect="blur"
      style={style}
      onError={(e) => {
        console.error(`Error loading image: ${photo.file_path}`);
        setError(true);
      }}
    />
  );
};

const Photos = () => {
  const [photos, setPhotos] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const loadingRef = useRef(false);
  const columns = useRef(5);
  const img_width = useRef(250);
  
  const [dimensions, setDimensions] = useState(() => ({ 
    width: window.innerWidth,
    height: window.innerHeight 
  }));


  const updateDimensionsAndColumns = useCallback(() => {
    const width = window.innerWidth;
    const height = window.innerHeight;
    // given the width, calculate the number of columns to fit images
    img_width.current = (width / columns.current) - 15;
    setDimensions({ width, height });
  }, []);

  useEffect(() => {
    updateDimensionsAndColumns();
    window.addEventListener('resize', updateDimensionsAndColumns);
    return () => window.removeEventListener('resize', updateDimensionsAndColumns);
  }, [updateDimensionsAndColumns]);

  const fetchPhotos = useCallback(async () => {
    if (loadingRef.current || !hasMore) return;
    loadingRef.current = true;
    setIsLoading(true);
    try {
      const response = await fetch(`${DATABASE_URL}/api/photos?page=${page}&per_page=50`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (!data || data.items.length === 0) {
        setHasMore(false);
      } else {
        setPhotos(prevPhotos => [...prevPhotos, ...data.items]);
        setPage(prevPage => prevPage + 1);
        setHasMore(data.page < data.total_pages);
      }
    } catch (error) {
      console.error('Error fetching photos:', error);
    } finally {
      setIsLoading(false);
      loadingRef.current = false;
    }
  }, [page]);

  useEffect(() => {
    fetchPhotos();
  }, [fetchPhotos]);

  useEffect(() => {
    const handleResize = () => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleScroll = useCallback((event) => {
    const { scrollTop, clientHeight, scrollHeight } = event.currentTarget;
    if (scrollHeight - scrollTop <= clientHeight * 1.5 && !loadingRef.current && hasMore) {
      fetchPhotos();
    }
  }, [fetchPhotos, hasMore]);

  const photoElements = photos.map((photo) => (
    <PhotoImage
      key={photo.id}
      photo={photo}
      style={{
        ...styles.image,
        width: img_width.current,
        height: `${dimensions.width / 5}px`,
      }}
    />
  ));

  return (
    <div 
      style={styles.container} 
      onScroll={handleScroll}
    >
      <div style={styles.photoGrid}>
        {photoElements}
      </div>
      {isLoading && <div>Loading...</div>}
      {!hasMore && <div>No more photos to load</div>}
    </div>
  );
};

const styles = {
  container: {
    width: '100%',
    height: '100vh',
    overflowY: 'auto',
    overflowX: 'auto',
  },
  photoGrid: {
    display: 'flex',
    flexWrap: 'wrap',
    justifyContent: 'flex-start',
    gap: '8px',
    paddingLeft: '15px', // Added padding at the top to create a gap at the beginning of the page
  },
  image: {
    objectFit: 'cover',
    border: '1px solid #ddd',
    borderRadius: '8px',
  },
};

export default Photos;

