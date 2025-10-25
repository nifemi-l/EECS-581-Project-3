import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './components/Header.css';
import './App.css';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

function App() {

  return (
    <Router>
      <Routes> 
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Router>
  );
}

export default App;