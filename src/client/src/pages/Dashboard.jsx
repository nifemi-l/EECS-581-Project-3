// Prologue
// Name: dashboard.jsx
// Description: Define the dashboard page of our application and its functionality
// Programmer: Nifemi Lawal
// Creation date: 10/24/25
// Last revision date: 11/05/25
// Revisions: 1.2
// Pre/post conditions
//   - Pre: None. 
//   - Post: None.
// Errors: None. 

// Dashboard page (Dashboard.jsx)
import React, { useState, useEffect, useRef } from 'react';
import LoaderBarsEffect from '../components/loading/LoaderBarsEffect';
import { Link } from "react-router-dom"

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
            return [{ 'message': 'User information successfully retrieved', 'user_info': data.user_info }, responseCode];
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
                    // Retry the original request with the new token
                    return await fetchUserInfo();
                } else { 
                    return [{ 'error': refreshResponseErrorMessage }, refreshResponseCode];                    
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
            return [{ 'error': 'Unknown error' }, responseCode];
        }
    } catch (error) { 
        console.error('Error fetching user information:', error);
        return [{ 'error': 'Error fetching user information' }, 500];
    }
}

async function fetchUserListeningHistory() { 
    try { 
        const response = await fetch('http://127.0.0.1:5000/get-user-listening-history', {
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
                'message': 'User listening history successfully retrieved', 
                'user_listening_history': data.user_listening_history 
            }, responseCode];
        }

        // Unauthorized response
        else if (responseCode === 401) {
            const responseErrorMessage = data.error;
            const needsRefresh = data.needs_refresh;

            // If user token is expired, try to refresh 
            if (needsRefresh === true) { 
                const [refreshResponseCode, refreshResponseErrorMessage] = await refreshUserToken();
                if (refreshResponseCode === 200) { 
                    // Retry the original request with the new token
                    return await fetchUserListeningHistory();
                } else { 
                    return [{ 'error': refreshResponseErrorMessage }, refreshResponseCode];
                }
            } else { 
                window.location.href = 'http://127.0.0.1:3000/login';
                return [{ 'error': responseErrorMessage }, responseCode];
            }
        }
        // Unknown error response
        else {
            return [{ 'error': 'Unknown error'}, responseCode];
        }

    } catch (error) { 
        console.error('Error fetching user listening history:', error);
        return [{ 'error': 'Error fetching user listening history' }, 500];
    }
}

function Dashboard() { 
    // Set up state for user information and listening history
    const [userInfo, setUserInfo] = useState(null);
    const [userListeningHistory, setUserListeningHistory] = useState(null);
    
    // Use ref to prevent duplicate fetches in React StrictMode (dev)
    const hasFetchedRef = useRef(false);

    // Fetch user information and listening history concurrently when component mounts
    useEffect(() => { 
        // Prevent double fetch in React StrictMode
        if (hasFetchedRef.current) {
            return;
        }
        hasFetchedRef.current = true;
        
        const loadDashboardData = async () => {
            // Wait 700ms to ensure loader bars effect is visible
            await new Promise(resolve => setTimeout(resolve, 700));
            
            try {
                // Fetch both user info and listening history in parallel
                const [userInfoResult, listeningHistoryResult] = await Promise.all([
                    fetchUserInfo(),
                    fetchUserListeningHistory()
                ]);

                // Destructure results
                const [userInfoResponse, userInfoResponseCode] = userInfoResult;
                const [listeningHistoryResponse, listeningHistoryResponseCode] = listeningHistoryResult;

                // Handle user info response
                if (userInfoResponseCode === 200) { 
                    setUserInfo(userInfoResponse['user_info']);
                } else {
                    // If user info fetch fails, redirect to login
                    window.location.href = 'http://127.0.0.1:3000/login';
                    return;
                }

                // Handle listening history response (can fail independently)
                if (listeningHistoryResponseCode === 200) { 
                    setUserListeningHistory(listeningHistoryResponse['user_listening_history']);
                } else {
                    // Log error but don't block dashboard since user info is more critical
                    console.error('Failed to fetch listening history:', listeningHistoryResponse['error']);
                    setUserListeningHistory([]); // Set empty array on failure
                }
            } catch (error) {
                console.error('Error loading dashboard data:', error);
                window.location.href = 'http://127.0.0.1:3000/login';
            }
        };
        loadDashboardData();
    }, []);

    // If user information is not loaded, show a loading message
    if (!userInfo) { 
        return <LoaderBarsEffect />;
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
                    <h1>Your Listening History</h1>
                    {userListeningHistory && Array.isArray(userListeningHistory) && userListeningHistory.length > 0 ? (
                        <div className="tracks-list">
                            {userListeningHistory.map((track) => (
                                <div key={track.id} className="track-card">
                                    {track.album_image && (
                                        <img src={track.album_image} alt={track.track_name} className="album-art" />
                                    )}
                                    <div className="track-info">
                                        <h3 className="track-name">
                                            {track.spotify_url ? (
                                                <a href={track.spotify_url} target="_blank" rel="noopener noreferrer">
                                                    {track.track_name}
                                                </a>
                                            ) : (
                                                track.track_name
                                            )}
                                        </h3>
                                        <p className="track-artists">{track.artists}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p>No listening history available yet.</p>
                    )}
                </div>

                {/* Button to "About" Page */ }
                <div style= {{textAlign: 'center' }}>
                    <Link to="/about">
                        <button className="to-about-btn">
                        About Scorify
                        </button>
                    </Link>
                </div>
            </div>
        );
    }
}

// Make the Dashboard component available for use
export default Dashboard;
