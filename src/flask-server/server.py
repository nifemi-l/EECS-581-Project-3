from flask import Flask
import curl 

app = Flask(__name__)

# Member API route
@app.route("/members")
def members():
    return { 
        "members": ["Nifemi Lawal"]
    }

if __name__ == "__main__":
    # Debug = True, since we're in development mode
    app.run(debug=True)