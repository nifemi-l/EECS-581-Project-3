// Prologue
// Name: login.jsx
// Description: Define the login page of our application and its functionality
// Programmer: Nifemi Lawal
// Creation date: 10/24/25
// Revisions: 1.1
// Last revision date: 11/05/25
// Pre/post conditions
//   - Pre: None. 
//   - Post: None.
// Errors: All known errors should be handled gracefully. 

// Login page (Login.jsx)
import React, { useEffect, useState } from 'react'; 
import { useSearchParams } from 'react-router-dom';
import { HiOutlineExclamationCircle } from 'react-icons/hi';
import '../components/Error.css';

function handleSpotifyLogin() { 
    // Redirect to the login endpoint --> Redirects to Spotify's OAuth2 page
    window.location.href = 'http://127.0.0.1:5000/login';
}

// Helper function to handle the error message from the login page
function handleErrorFromURL(searchParams, setSearchParams, setErrorMessage) { 
    // Get the error message from the URL
    const encodedErrorMessage = searchParams.get('error');
    if (encodedErrorMessage) { 
        // Decode the error message
        const decodedErrorMessage = decodeURIComponent(encodedErrorMessage);

        // Set the error message in the state
        setErrorMessage(decodedErrorMessage);

        // Remove the error parameter from the URL
        searchParams.delete('error');

        // Replace the current URL with the new URL (without the error parameter)
        setSearchParams(searchParams, { replace: true });
    }
}

function Login() { 
    const [searchParams, setSearchParams] = useSearchParams();
    const [errorMessage, setErrorMessage] = useState(null);

    useEffect(() => { 
        handleErrorFromURL(searchParams, setSearchParams, setErrorMessage);
    }, [searchParams, setSearchParams, setErrorMessage]);

    return ( 
        <div id="login-container">
            {/* Header text */}
            <div className="header">
                <h1>Welcome to Scorify</h1>
                {/* Spotify login button */}
                <div className="oauth"> 
                    <a href="#" onClick={handleSpotifyLogin} className="spotify-login-btn">
                        Login with Spotify
                    </a>
                </div>
            </div>
            
            {/* Error banner */}
            {errorMessage && (
                <div className="error-banner">
                    <div className="error-banner-content">
                        <HiOutlineExclamationCircle className="error-banner-icon" />
                        <p className="error-banner-text">
                            {errorMessage}
                        </p>
                    </div>
                    <button className="error-banner-close" onClick={() => setErrorMessage(null)} aria-label="Close error message">
                        <span className="error-banner-close-icon"></span>
                    </button>
                </div>
            )}
      </div>
    );
}

// Make the Login component available for use
export default Login;