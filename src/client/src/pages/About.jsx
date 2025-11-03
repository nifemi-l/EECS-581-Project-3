// Prologue
// Name: About.jsx
// Description: Create an "About" page which provides information about the service that may be of interest to users.
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

function About() {
    return (
        <div>
            <div className="header">
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
                    <h3>Music Taste Rating</h3>
                        <p>The Music Taste Rating is a metric that evaluates how "good" your music taste rating is.
                            The score is based on how closely your music taste matches the Scorify developers' tastes.
                            This metric is meant more for fun than to be a serious evaluation of your music taste.
                            The Music Taste Rating is calculated using the following formula:
                        </p>
                <h4>Thank you for using Scorify!</h4>
            <div style= {{textAlign: 'center' }}>
                <Link to="/dashboard">
                    <button className="to-dashboard-btn">
                        Back to Dashboard
                    </button>
                </Link>
            </div>
        </div>
    )
}

export default About;