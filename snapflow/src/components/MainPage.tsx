import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const MainPage: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4, textAlign: 'center' }}>
        <img 
          src="/snapflow.png" 
          alt="Snapflow Logo" 
          style={{ maxWidth: '300px', marginBottom: '2rem' }}
        />
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome to Snapflow
        </Typography>
        <Typography variant="subtitle1">
          Your personal photo aggregation and management tool
        </Typography>
      </Box>
    </Container>
  );
};

export default MainPage;