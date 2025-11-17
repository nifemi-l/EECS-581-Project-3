// Prologue
// Name: Leaderboard.jsx
// Description: Create a leaderboard page which displays the leaderboard
// Programmer: Blake Carlson, Jack Bauer
// Creation date: 11/03/25
// Last revision date: 11/16/25
// Revisions: 1.1
// Pre/post conditions
//   - Pre: None. 
//   - Post: None.
// Errors: All known errors should be handled appropriately.

import React, { useEffect, useState, useRef } from "react";
import TempDrawer from "./TempDrawer.jsx"
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import LoaderBarsEffect from "../components/loading/LoaderBarsEffect.jsx";
import "../components/Leaderboard.css";

async function fetchLeaderboardData() {
    // Function to fetch the needed data to populate our leaderboard
    // See similar fetch functions in Dashboard.jsx

    // Fetch from the endpoint
    const response = await fetch('http://127.0.0.1:5000/get-leaderboard-data', {
        credentials: 'include',
        mode: 'cors'
    });

    // Gather response data
    const responseCode = response.status;
    const data = await response.json();
    const responseMessage = data.error || data.message || 'Else';

    // Return results
    return [responseCode, responseMessage, data];
}

function Leaderboard() {
    // State for drawer
    const [drawerOpen, setDrawerOpen] = React.useState(false);

    // State for whether the drawer is toggled or not.
    const toggleDrawer = () => {
        setDrawerOpen(!drawerOpen);
    };

    // Data needed for the leaderboard: 
    // -- user profile picture
    // -- username
    // -- diversity score
    // -- taste rating

    // Note: this process will be very similar to Dashboard.jsx. 
    // -- Gotta give credit where credit is due

    // For React strict mode, use ref to avoid extra fetches
    const hasFetchedRef = useRef(false);

    // Setup for leaderboard data
    const [leaderboardData, setLeaderboardData] = useState(null);

    // Fetch leaderboard data on component mount
    useEffect(() => {
        // Add React strict mode compatability 
        if (hasFetchedRef.current) {
            return;
        }
        hasFetchedRef.current = true;

        // Define the loader function
        const loadLeaderboardData = async () => {
            // Set a timeout to show loading screen
            await new Promise(resolve => setTimeout(resolve, 700));

            try {
                // Fetch and set leaderboard data
                const result = await fetchLeaderboardData();

                // Unpack result
                const [resultResponseCode, resultMessage, resultData] = result;

                // Set leaderboard data
                if (resultResponseCode === 200) {
                    setLeaderboardData(resultData);
                } else {
                    console.error('Failed to fetch leaderboard data:', resultResponseCode, " ", resultMessage);
                    setLeaderboardData([]);
                }
            } catch (error) {
                console.error("Error loading leaderboard data:", error);
                setLeaderboardData([]);
            }
        };

        // Load the data
        loadLeaderboardData();
    }, []);

    // If we're waiting on data, show the loading screen
    if (!leaderboardData) {
        return <LoaderBarsEffect />;
    }

    // Otherwise, if we've had success...
    if (leaderboardData) {
        // Store all our user objects to make our leaderboard entries
        let users = [];

        // Collect data for a specific user
        for (let i =0; i < leaderboardData.length; i++) {
            let key = i;
            let userName = leaderboardData[i][0];
            let userProfilePicPath = leaderboardData[i][1];
            let userDivScore = Math.floor(Math.random() * 10);
            let userTasteRating = Math.floor(Math.random() * 10);
            users[i] = {id:key, picPath:userProfilePicPath, username:userName, divScore:userDivScore, tasteRating:userTasteRating};
        }

        // Finally, build our page
        return (
            <div>
                <div className="header">
                {/* Button toggling the temp drawer */}
                <IconButton onClick={toggleDrawer}>
                    <MenuIcon fontSize="large"/>
                </IconButton>

                {/* TempDrawer with header text */}
                <TempDrawer open={drawerOpen} onClose={toggleDrawer} />
                    <h1>Leaderboard</h1>
                </div>

                {/* Leaderboard */}
                <div className="leaderboard">
                    <h1>Leaderboard</h1>
                    <p>Profile Picture | Username | Diversity Score | Music Taste Rating</p>
                    <ul>
                        {users.map((entry) => 
                            <li key={entry.id}>
                                <div className="pic-container">
                                    <img src={entry.picPath} alt="Profile Picture"></img>
                                </div>
                                <div className="spacer"></div>
                                <p>{entry.username}</p>
                                <div className="spacer"></div>
                                <p>{entry.divScore}</p>
                                <div className="spacer"></div>
                                <p>{entry.tasteRating}</p>
                            </li>)}
                    </ul>
                </div>

                {/*About text*/}
                <div>
                <p>This is where the leaderboard will be displayed
                </p>
                    <h2>Things to do</h2>
                        <h3>Query the leaderboard / data from the database</h3>
                            <p>Assuming scores are calculated when the listening history gets updated and stored in the database,
                                the leaderboard should be able to be queried using a SQL command sorting the scores relation from highest to lowest score
                            </p>
                        <h3>Clicking / Viewing Other Profiles</h3>
                            <p>You should be able to click on other users in the leaderboard to see their listening histories. This might require the username to be at the end of the link / path.
                            </p>
                    <h4>Thank you for using Scorify!</h4>
                </div>
            </div>
        )
    }
}

export default Leaderboard;