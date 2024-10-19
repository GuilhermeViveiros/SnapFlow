import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Photos from './components/Photos';
import People from './components/People';
import './App.css'; // We'll create this file for styling

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="nav-buttons">
          <Link to="/people" className="nav-button">People</Link>
          <Link to="/photos" className="nav-button">All Photos</Link>
        </nav>

        <Routes>
          <Route path="/people" element={<People />} />
          <Route path="/photos" element={<Photos />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
