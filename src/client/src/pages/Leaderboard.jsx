// Prologue
// Name: Leaderboard.jsx
// Description: Create a leaderboard page which displays the leaderboard
// Programmer: Blake Carlson, Jack Bauer
// Creation date: 11/03/25
// Last revision date: 11/23/25
// Revisions: 1.2
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

function sortUsers(users, filterMode) {
    // Sort array according to filter mode (default to diversity_score)
    if (filterMode === "Taste") {
        users.sort(function(a, b){
            return b.tasteScore - a.tasteScore;
        });
    } else {
        users.sort(function(a, b){
            return b.divScore - a.divScore;
        });
    }
}

function Leaderboard() {
    // State for drawer
    const [drawerOpen, setDrawerOpen] = React.useState(false);

    // State for whether the drawer is toggled or not.
    const toggleDrawer = () => {
        setDrawerOpen(!drawerOpen);
    };

    // State for filters (initialize to diversity score)
    const [filterMode, setFilterMode] = React.useState("Diversity");

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
        if (leaderboardData.length <= 0) {
            // This is not the ideal behavior, but works for now. This will usually happen
            // if an expired refresh token means we haven't successfully retrieved leaderboard data.
            // If that happens, this will appear. I'm sure there's a better way to do this, but this works
            // for now.
            return (
            <>
                <div className="error">
                    <p className="primary">ERROR - Cannot connect to Scorify servers.</p>
                    <p className="secondary">Please try logging in again or checking your internet connection.</p>
                    <a className="login" href="/login">Login</a>
                </div>
            </>);
        }

        // Split leaderboard data
        const profiles = leaderboardData.profiles;
        const scores = leaderboardData.scores;

        // Store all our user objects to make our leaderboard entries
        let users = [];

        // Collect data for a specific user
        for (let i =0; i < profiles.length; i++) {
            let key = i;
            let userName = profiles[i][1];
            let userProfilePicPath = profiles[i][2];
            
            // Set our scores
            let userScores = scores.find(item => String(item[0]) == profiles[i][0]); // Search for the score that matches the user
            let userDivScore;
            // If we found a score for the user, set it and multiply it by 100 (since the database values are clmaped between 0 and 1)
            if (typeof userScores !== 'undefined') {
                userDivScore = userScores[1] * 100;
            } else {
                // If we don't have a score, set it to 0
                userDivScore = 0;
            }
            let userTasteScore = Math.floor(Math.random() * 10);
            users[i] = {id:key, picPath:userProfilePicPath, username:userName, divScore:userDivScore, tasteScore:userTasteScore};
        }

        // Initially sort our array (defaults to diversity score)
        sortUsers(users, filterMode);
        
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
                <div className="leaderboard" id="leaderboard-container">
                    <h1 id="title">Leaderboard</h1>
                    <div className="filter">
                        <p>Rank by: </p>
                        <button onClick={() => {
                            if (filterMode === "Diversity") {
                                setFilterMode("Taste");
                            } else {
                                setFilterMode("Diversity");
                            }
                            sortUsers(users);
                        }}>{filterMode} Score</button>
                    </div>
                    <ul>
                        {filterMode === "Taste" 
                            ? 
                            users.map((entry) => 
                            <li key={entry.id}>
                                <div className="pic-container">
                                    <img src={entry.picPath} alt="Profile Picture"></img>
                                </div>
                                <p>{entry.username}</p>
                                <p>{entry.tasteScore}</p>
                            </li>) 
                            : 
                            users.map((entry) => 
                            <li key={entry.id}>
                                <div className="pic-container">
                                    <img src={entry.picPath} alt="Profile Picture"></img>
                                </div>
                                <p>{entry.username}</p>
                                <p>{entry.divScore}</p>
                            </li>) 
                        }
                    </ul>
                </div>
            </div>
        )
    }
}

export default Leaderboard;