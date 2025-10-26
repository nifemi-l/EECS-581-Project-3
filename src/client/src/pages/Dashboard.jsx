// Dashboard page (Dashboard.jsx)
import React, { useState, useEffect } from 'react';

// Function to retrieve user informatino frome the backend API
// - Should not block the main thread
async function fetchUserInfo() { 
    try { 
        // Send GET request to backend API to get user information
        const response = await fetch('http://127.0.0.1:5000/api-get-user-info', {
            credentials: 'include',
            mode: 'cors',
        });
        // Get response code from response
        const responseCode = response.status;
        // Jsonify response from backend API
        const data = await response.json();

        // OK response
        if (responseCode === 200) {
            return data.user_info;
        }
        // Unauthorized response
        else if (responseCode === 401) {
            const responseError = data.error;
            return {
                'error': responseError
            }, responseCode;
        }
        // Unknown error response
        else {
            return {
                'error': 'Unknown error'
            }, responseCode;
        }
    } catch (error) { 
        console.error('Error fetching user information:', error);
    }
}

function Dashboard() { 
    // Set up state for user information
    const [userInfo, setUserInfo] = useState(null);

    // Fetch user information when the component mounts
    useEffect(() => { 
        const getUserInfo = async () => {
            const userInfo = await fetchUserInfo();
            // If user information is fetched, store it in the state
            if (userInfo) { 
                setUserInfo(userInfo);
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
                <h1>Hello, {userInfo.display_name}!</h1>
            </div>
        );
    }
}

export default Dashboard;