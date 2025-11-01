// Prologue
// Name: dashboard.jsx
// Description: Define the dashboard page of our application and its functionality
// Programmer: Nifemi Lawal
// Creation date: 10/24/25
// Revisions: 1.0
// Pre/post conditions
//   - Pre: None. 
//   - Post: None.
// Errors: All known errors should be handled gracefully. 

// Dashboard page (Dashboard.jsx)
import React, { useState, useEffect } from 'react';

async function refreshUserToken() { 
    // Refresh the user's token
    const response = await fetch('http://127.0.0.1:5000/refresh-user-token', { 
        credentials: 'include',
        mode: 'cors'
    });
    
    // Grab response code and message
    const responseCode = response.status;
    const data = await response.json();
    const responseMessage = data.error || data.message || 'Unknown error';

    // Return response code and message
    return [responseCode, responseMessage];
}

// Function to retrieve user information frome the backend API
// - Should not block the main thread
async function fetchUserInfo() { 
    try { 
        // Send GET request to backend API to get user information
        const response = await fetch('http://127.0.0.1:5000/get-user-info', {
            credentials: 'include',
            mode: 'cors'
        });
        // Get response code from response
        const responseCode = response.status;
        // Jsonify response from backend API
        const data = await response.json();

        // OK response
        if (responseCode === 200) {
            return [{ 
                'message': 'User information successfully retrieved',
                'user_info': data.user_info
            }, responseCode];
        }

        // Unauthorized response
        else if (responseCode === 401) {
            // Return error message and redirect to login
            const responseErrorMessage = data.error;
            const needsRefresh = data.needs_refresh;

            // If user token is expired, try to refresh 
            if (needsRefresh === true) { 
                const [refreshResponseCode, refreshResponseErrorMessage] = await refreshUserToken();
                if (refreshResponseCode === 200) { 
                    return [{ 
                        'message': 'User access token has been refreshed',
                    }, refreshResponseCode];
                } else { 
                    return [{
                        'error': refreshResponseErrorMessage
                    }, refreshResponseCode];                    
                }
            } else { 
                window.location.href = 'http://127.0.0.1:3000/login';
                return [{
                    'error': responseErrorMessage
                }, responseCode];
            }
        }
        // Unknown error response
        else {
            return [{
                'error': 'Unknown error'
            }, responseCode];
        }
    } catch (error) { 
        console.error('Error fetching user information:', error);
        return [{ 'error': 'Error fetching user information' }, 500];
    }
}

function Dashboard() { 
    // Set up state for user information
    const [userInfo, setUserInfo] = useState(null);

    // Fetch user information when the component mounts
    useEffect(() => { 
        const getUserInfo = async () => {
            const [response, responseCode] = await fetchUserInfo();
            // If user information is fetched, store it in the state
            if (responseCode === 200) { 
                setUserInfo(response['user_info']);
            } else { // If user information is not fetched, redirect to login
                window.location.href = 'http://127.0.0.1:3000/login';
            } 
        };
        getUserInfo();
    }, []);

    // If user information is not loaded, show a loading message
    if (!userInfo) { 
        return <div>Loading...</div>;
    }

    // If user information is loaded, show the dashboard
    if (userInfo) { 
        return ( 
            <div id="dashboard-container">
                <div className="header">
                    <div className='profile-container'>
                        {/* Profile picture container */}
                        <div className="profile-picture-container">
                            {/* Profile picture */}
                            <div id="profile-picture">
                                {userInfo.images && userInfo.images.length > 0 ? (
                                    <img src={userInfo.images[0].url} alt="Profile Picture"/>
                                ) : (
                                    <svg width="64" height="64" viewBox="0 0 24 24" fill="currentColor">
                                        <path d="M10.165 11.101a2.5 2.5 0 0 1-.67 3.766L5.5 17.173A3 3 0 0 0 4 19.771v.232h16.001v-.232a3 3 0 0 0-1.5-2.598l-3.995-2.306a2.5 2.5 0 0 1-.67-3.766l.521-.626.002-.002c.8-.955 1.303-1.987 1.375-3.19.041-.706-.088-1.433-.187-1.727a3.7 3.7 0 0 0-.768-1.334 3.767 3.767 0 0 0-5.557 0c-.34.37-.593.82-.768 1.334-.1.294-.228 1.021-.187 1.727.072 1.203.575 2.235 1.375 3.19l.002.002zm5.727.657-.52.624a.5.5 0 0 0 .134.753l3.995 2.306a5 5 0 0 1 2.5 4.33v2.232H2V19.77a5 5 0 0 1 2.5-4.33l3.995-2.306a.5.5 0 0 0 .134-.753l-.518-.622-.002-.002c-1-1.192-1.735-2.62-1.838-4.356-.056-.947.101-1.935.29-2.49A5.7 5.7 0 0 1 7.748 2.87a5.77 5.77 0 0 1 8.505 0 5.7 5.7 0 0 1 1.187 2.043c.189.554.346 1.542.29 2.489-.103 1.736-.838 3.163-1.837 4.355m-.001.001"></path>
                                    </svg>
                                )}
                            </div>
                        </div>

                        {/* Display name container */}
                        <div id="display-name-container">
                            {/* Display name */}
                            <h1>{userInfo.display_name}</h1>
                        </div>
                    </div>
                </div>

                {/* Dashboard content */}
                <div className="dashboard-content">
                    <h1>Dashboard</h1>
                    <p>Welcome to the dashboard!</p>
                    <p>This is where a user can see their application content.</p>
                </div>
            </div>
        );
    }
}

// Make the Dashboard component available for use
export default Dashboard;
