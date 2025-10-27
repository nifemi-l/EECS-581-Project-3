/* Prologue
  // Name: index.js
  // Description: The entry point of our application. 
  // Programmer: Nifemi Lawal
  // Creation date: 10/23/25
  // Revisions: 1.0
  // Pre/post conditions
  //   - Pre: None. 
  //   - Post: The application will be displayed
  // Errors: None. 
*/

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import reportWebVitals from './reportWebVitals';

// The entry point of our React application (the "root"). 
// The rest of our application logic is handled elsewhere
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
      <App />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
