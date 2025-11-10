// Prologue
// Name: Leaderboard.jsx
// Description: Create a leaderboard page which displays the leaderboard
// Programmer: Blake Carlson
// Creation date: 11/03/25
// Last revision date: 11/03/25
// Revisions: 1.0
// Pre/post conditions
//   - Pre: None. 
//   - Post: None.
// Errors: All known errors should be handled appropriately.


import React from "react";
import { Link } from "react-router-dom"
import TempDrawer from "./TempDrawer.jsx"
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';

function Leaderboard() {
    // State for drawer
        const [drawerOpen, setDrawerOpen] = React.useState(false);
    
        // State for whether the drawer is toggled or not.
        const toggleDrawer = () => {
            setDrawerOpen(!drawerOpen);
        };
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
    )
}

export default Leaderboard;