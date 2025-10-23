from flask import Flask
import curl 
import requests

# Flask app initialization
app = Flask(__name__)
# Random secret key for the app
app.secret_key = '234a5-789b6-012c3-456d7-890e1'

# Member API route
@app.route("/members")
def members():
    return { 
        "members": ["Nifemi Lawal"]
    }

if __name__ == "__main__":
    # Debug = True, since we're in development mode
    app.run(debug=True)