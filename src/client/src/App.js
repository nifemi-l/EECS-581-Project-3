// Prologue
// Name: App.js
// Description: Define the application's routes
// Programmer: Nifemi Lawal
// Creation date: 10/24/25
// Revisions: 1.0
// Pre/post conditions
//   - Pre: None. 
//   - Post: The application's routes are defined.
// Errors: None. 

import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './components/Header.css';
import './App.css';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import About from './pages/About';
import Leaderboard from "./pages/Leaderboard"
import { useParams } from "react-router-dom"


// Define our App component
function App() {
  // Define 3 routes:
  // 1. / for generic API access
  // 2. /login for the login page
  // 3. /dashboard for the dashboard page

  // 
  return (
    <Router>
      <Routes> 
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/dashboard/:viewedUserId?" element={<Dashboard />} />
        <Route path="/about" element={<About />} />
        <Route path="/leaderboard" element={<Leaderboard />} />
      </Routes>
    </Router>
  );
}

// Make the App component available
export default App;