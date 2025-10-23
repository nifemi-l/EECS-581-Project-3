import React from 'react'
import './components/Header.css';
import './App.css';
import { GoogleLogin } from "@react-oauth/google"

function App() {
  

  return (
    <div id="container">
      {/* Header text */}
      <div class="header">
        <h1>Welcome to the Spotify Project!</h1>
      </div>
      
      {/* OAuth login */}
      <div class="oauth"> 
        <GoogleLogin class="oauth-login"
        onSuccess={(credentialResponse) => 
          console.log(credentialResponse)
        }
        onError={() => console.log("Login failed")}
        />
      </div>
    </div>
  )

}

export default App