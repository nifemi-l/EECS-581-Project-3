import React from 'react'
import './components/Header.css';
import './App.css';

function App() {
  

  return (
    <div id="container">
      {/* Header text */}
      <div className="header">
        <h1>Welcome to the Spotify Project!</h1>
      </div>
      
      {/* Spotify login button */}
      <div className="oauth"> 
        <a href="http://127.0.0.1:5000/login" className="spotify-login-btn">
          Login with Spotify
        </a>
      </div>
    </div>
  )

}

export default App