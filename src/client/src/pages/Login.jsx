// Prologue
// Name: login.jsx
// Description: Define the login page of our application and its functionality
// Programmer: Nifemi Lawal
// Creation date: 10/24/25
// Revisions: 1.0
// Pre/post conditions
//   - Pre: None. 
//   - Post: None.
// Errors: All known errors should be handled gracefully. 

// Login page (Login.jsx)
import React from 'react';

function Login() { 
    return ( 
        <div id="login-container">
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
    );
}

// Make the Login component available for use
export default Login;