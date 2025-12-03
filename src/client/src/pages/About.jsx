// Prologue
// Name: About.jsx
// Description: Create an "About" page which provides information about the service that may be of interest to users.
// Programmer: Blake Carlson
// Creation date: 11/03/25
// Last revision date: 11/09/25
// Revisions: 1.1
// Pre/post conditions
//   - Pre: None. 
//   - Post: None.
// Errors: All known errors should be handled appropriately.

import React from "react";
import { Link } from "react-router-dom"
import TempDrawer from "./TempDrawer.jsx"
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import { MathJax, MathJaxContext } from "better-react-mathjax"
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@4/tex-mml-chtml.js"></script>

function About() {
    // State for drawer
        const [drawerOpen, setDrawerOpen] = React.useState(false);
    
        // State for whether the drawer is toggled or not.
        const toggleDrawer = () => {
            setDrawerOpen(!drawerOpen);
        };

        const diversity_score_formula = `H(X) = \\frac{-\\sum_{i=1}^{n} p(x_i) \\log_b p(x_i)}{\\log_2(N)}`;
        const taste_score_formula = `T = 1 - \\left| D_u - D_{dev} \\right|`
    return (
        <div>
            <div className="header">
                {/* Button toggling the temp drawer */}
            <IconButton onClick={toggleDrawer}>
                <MenuIcon fontSize="large"/>
            </IconButton>

            <TempDrawer open={drawerOpen} onClose={toggleDrawer} />
                <h1>About Scorify</h1>
            </div>
            <div class="about-content">
            <h2>What is Scorify?</h2>
            <p>Scorify connects to your Spotify account and evaluates multiple scores for users based off of your past listening history.
                These scores are then compared against other user's scores to determine various characteristics about your listening habits compared to others.
                Further details about these scores and how they are calculated can be found below.
            </p>
                <p></p>
                <h2>Leaderboard</h2>
                        <p>The leaderboard shows the rankings of all users who have used Scorify.
                        It shows all users from greatest to least based on either their Diversity Score or User Taste Ranking, can be changed by
                        clicking the green button at the top of the page.
                        </p>
                        <p>
                        The scores shown on the leaderboard are only determined by the listening history that Scorify has retrieved.
                        This means all songs listened to before connecting your account to Scorify will not be taken into account when calculating your scores.
                        </p>
                        <p>
                        The leaderboard can be accessed by clicking the "Leaderboard" link in the sidebar.
                        </p>
                <p></p>
                <h2>Types of Scores</h2>
                    <h3>Diversity Score</h3>
                        <p>The Diversity Score is a metric that evaluates how diverse your music taste is. Generally, the more genres of music you listen to, the higher your diversity score will be.
                            The Diversity Score is calculated using the following formula:
                        </p>
                        <div className="formula">
                        <MathJaxContext>
                            <MathJax>{"$$" + diversity_score_formula + "$$"}</MathJax>
                        </MathJaxContext>
                        </div>
                    <p></p>
                    <p></p>
                    <h3>Music Taste Rating</h3>
                        <p>The Music Taste Rating is a metric that evaluates how "good" your music taste rating is.
                            The score is based on how closely your music taste matches the Scorify developers' tastes.
                            This metric is meant more for fun than to be a serious evaluation of your music taste.
                            The Music Taste Rating is calculated using the following formula:
                        </p>
                        <div className="formula">
                        <MathJaxContext>
                            <MathJax>{"$$" + taste_score_formula + "$$"}</MathJax>
                        </MathJaxContext>
                        </div>
                <p></p>
                <h2>Dashboards</h2>
                    <p>Your dashboard is a centralized location where you can view all your metrics,
                        including your listening history Scorify has retrieved, your Diveristy Score, your Music Taste Rating, and today's "Song of the Day"
                    </p>
                    <p></p>
                    <p>If you are viewing your own dashboard, the "Fetch Listening History" button can be used to retrieve your current listening history.</p>
                <p></p>
                <h2>Viewing Other User's Profiles</h2>
                    <p>To view another user's dashboard, click on their username from the leadboard.
                        This will allow you to see their listening history and scores as if you were viewing your own dashboard.
                    </p>
                    <p>
                        You can then navigate back to the leaderboard or your own dashboard through the sidebar menu.
                    </p>

                <p></p>
                <h2>Song of the Day</h2>
                <p>Every day, a song will be randomly selected as the day's, "Song of the Day".
                    The current song can be viewed from any dashboard, regardless if it is your own or not.
                </p>
                <p>The songs that can be selected for the "Song of the Day" include any song in the listening history of the Scorify developers.
                    Listening to each day's song is encouraged to diversity your music taste and increase your scores. 
                </p>
                    <p></p>
                    <p></p>
                    <p></p>

                <h2>Thank you for using Scorify!</h2>
                <h4>Created by: Blake Carlson, Delroy Wright, Logan Smith, Nifemi Lawal, Jack Bauer</h4>
                </div>
        </div>
    )
}

export default About;