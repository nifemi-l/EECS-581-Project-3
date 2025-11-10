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
            

            <p>Scorify connects to your Spotify account and evaluates multiple scores for users based off of your past listening history.
                These scores are then compared against other user's scores to determine various characteristics about your listening habits compared to others.
                Further details about these scores and how they are calculated can be found below.
            </p>
                <h2>Types of Scores</h2>
                    <h3>Diversity Score</h3>
                        <p>The Diversity Score is a metric that evaluates how diverse your music taste is. Generally, the more genres of music you listen to, the higher your diversity score will be.
                            The Diversity Score is calculated using the following formula:
                        </p>
                        <MathJaxContext>
                            <MathJax>{"$$" + diversity_score_formula + "$$"}</MathJax>
                        </MathJaxContext>
                    <h3>Music Taste Rating</h3>
                        <p>The Music Taste Rating is a metric that evaluates how "good" your music taste rating is.
                            The score is based on how closely your music taste matches the Scorify developers' tastes.
                            This metric is meant more for fun than to be a serious evaluation of your music taste.
                            The Music Taste Rating is calculated using the following formula:
                        </p>
                        <MathJaxContext>
                            <MathJax>{"$$" + taste_score_formula + "$$"}</MathJax>
                        </MathJaxContext>
                <h4>Thank you for using Scorify!</h4>
        </div>
    )
}

export default About;