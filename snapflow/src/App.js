import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import Photos from './components/Photos';
import People from './components/People';
import './App.css'; // We'll create this file for styling

function App() {
  // const snapflowLogo = require('./snapflow.png');
  return (
    <Router>
      <div className="App">
        <main className="App-main">
          <Routes>
            <Route path="/" element={<Navigate to="/photos" replace />} />
            <Route path="/people" element={<People />} />
            <Route path="/photos" element={<Photos />} />
          </Routes>
        </main>
        <footer className="App-footer">
          <nav className="nav-buttons">
            <Link to="/people" className="nav-button">People</Link>
            <Link to="/photos" className="nav-button">All Photos</Link>
          </nav>
        </footer>
      </div>
    </Router>
  );
}

export default App;
