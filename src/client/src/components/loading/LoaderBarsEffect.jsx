// Prologue
// Name: LoaderBarsEffect.jsx
// Description: Define the loader bars effect component
// Programmer: Nifemi Lawal
// Creation date: 11/01/25
// Last revision date: 11/01/25
// Revisions: 1.0
// Pre/post conditions
//   - Pre: None. 
//   - Post: None.
// Errors: All known errors should be handled gracefully. 

import React from 'react';
import './LoaderBarsEffect.css';

export default function LoaderBarsEffect() { 
    return ( 
        <div className="loader-container">
            <span className="loader"></span>
        </div>
    )
}

