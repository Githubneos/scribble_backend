from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os

# Initialize a Flask application
app = Flask(__name__)
CORS(app, supports_credentials=True, origins='*')  # Allow all origins (*)

# In-memory storage for chat logs and user stats
chat_logs = []
user_stats = {}

# API endpoint to get all chat logs
@app.route('/api/guesses', methods=['GET'])
def get_guesses():
    return jsonify(chat_logs), 200

# API endpoint to add a guess and update user stats
@app.route('/api/submit_guess', methods=['POST'])
def save_guess():
    data = request.json  # Expecting JSON input
    required_keys = {'user', 'guess', 'is_correct', 'drawing_id'}
    if not data or not required_keys.issubset(data):
        return jsonify({"error": "Invalid data. 'user', 'guess', 'is_correct', and 'drawing_id' are required."}), 400

    user = data['user']
    guess = data['guess']
    is_correct = data['is_correct']
    drawing_id = data['drawing_id']
    timestamp = datetime.now().isoformat()

    # Initialize stats for the user if not present
    if user not in user_stats:
        user_stats[user] = {
            "correct": 0,
            "wrong": 0,
            "total_guesses": 0,
            "guesses": []
        }

    # Update user stats
    user_stats[user]["total_guesses"] += 1
    if is_correct:
        user_stats[user]["correct"] += 1
    else:
        user_stats[user]["wrong"] += 1

    user_stats[user]["guesses"].append({
        "guess": guess,
        "is_correct": is_correct,
        "drawing_id": drawing_id,
        "timestamp": timestamp
    })

    # Append new guess to chat logs
    chat_logs.append({
        "user": user,
        "guess": guess,
        "is_correct": is_correct,
        "drawing_id": drawing_id,
        "timestamp": timestamp
    })

    return jsonify({"status": "Guess and stats updated successfully."}), 201

# API endpoint to retrieve stats for a specific user
@app.route('/api/user_stats/<string:username>', methods=['GET'])
def get_user_stats(username):
    user_stat = user_stats.get(username)
    if not user_stat:
        return jsonify({"error": f"No stats found for user '{username}'."}), 404

    return jsonify(user_stat), 200

# HTML endpoint for a basic welcome page
@app.route('/')
def say_hello():
    html_content = """
    <html>
    <head>
        <title>Guessing Game API</title>
    </head>
    <body>
        <h2>Welcome to the Guessing Game API</h2>
        <p>Use the API to save and retrieve guesses and user statistics.</p>
        <p>Endpoints:</p>
        <ul>
            <li>GET /api/guesses - Retrieve all chat logs</li>
            <li>POST /api/submit_guess - Submit a guess</li>
            <li>GET /api/user_stats/&lt;username&gt; - Retrieve stats for a specific user</li>
        </ul>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    import sys
    # Use command-line argument for the port
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    app.run(host="0.0.0.0", port=port)
