import React from 'react';
import { AppBar, Toolbar, Button } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const NavBar: React.FC = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Button color="inherit" component={RouterLink} to="/">
          Home
        </Button>
        <Button color="inherit" component={RouterLink} to="/photos">
          Photos
        </Button>
        <Button color="inherit" component={RouterLink} to="/people">
          People
        </Button>
      </Toolbar>
    </AppBar>
  );
};

export default NavBar;