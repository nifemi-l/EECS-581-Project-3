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


import React from "react";
import TempDrawer from "./TempDrawer.jsx"
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import "../components/Leaderboard.css";
import { fetchUserInfo, fetchUserListeningHistory } from "./Dashboard.jsx";

function Leaderboard() {
    // Data needed for the leaderboard: 
    // -- user profile picture
    // -- username
    // -- diversity score
    // -- taste rating

    // Store all our user objects to make our leaderboard entries
    let users = [];

    // Collect data for a specific user
    for (let i =0; i < 4; i++) {
        let userProfilePicPath = "noise.png";
        let userName = "User" + i;
        let userDivScore = Math.floor(Math.random() * 10);
        let userTasteRating = Math.floor(Math.random() * 10);
        const ithUser = {picPath:userProfilePicPath, username:userName, divScore:userDivScore, tasteRating:userTasteRating};
        users[i] = ithUser;
    }

    // State for drawer
    const [drawerOpen, setDrawerOpen] = React.useState(false);

    // State for whether the drawer is toggled or not.
    const toggleDrawer = () => {
        setDrawerOpen(!drawerOpen);
    };

    // Finally, build our page
    return (
        <div>
            <div className="header">
                {/* Button toggling the temp drawer */}
            <IconButton onClick={toggleDrawer}>
                <MenuIcon fontSize="large"/>
            </IconButton>

            <TempDrawer open={drawerOpen} onClose={toggleDrawer} />
                <h1>Leaderboard</h1>
            </div>

            {/* Leaderboard */}
            <div className="leaderboard">
                <h1>Leaderboard</h1>
                <p>Profile Picture | Username | Diversity Score | Music Taste Rating</p>
                <ul>
                    {users.map((entry) => 
                        <li>
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

export default Leaderboard;