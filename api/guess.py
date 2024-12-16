from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# Initialize a Flask application
app = Flask(__name__)
CORS(app, supports_credentials=True, origins='*')  # Allow all origins (*)

# In-memory storage for chat logs and user stats
chat_logs = []
user_stats = {}

# API endpoint to get all chat logs
@app.route('/api/guess', methods=['GET'])
def get_guess():
    return jsonify(chat_logs)

# API endpoint to add a guess and update user stats
@app.route('/api/chatlogs', methods=['POST'])
def save_guess():
    data = request.json  # Expecting JSON input
    if not data or 'user' not in data or 'guess' not in data or 'is_correct' not in data:
        return jsonify({"error": "Invalid data. 'user', 'guess', and 'is_correct' are required."}), 400

    user = data['user']
    guess = data['guess']
    is_correct = data['is_correct']

    # Initialize stats for the user if not present
    if user not in user_stats:
        user_stats[user] = {
            "correct": 0,
            "wrong": 0,
            "guesses": []
        }

    # Update stats and save the guess
    if is_correct:
        user_stats[user]["correct"] += 1
    else:
        user_stats[user]["wrong"] += 1

    user_stats[user]["guesses"].append({
        "guess": guess,
        "is_correct": is_correct
    })

    # Append new guess to chat logs
    chat_logs.append({
        "user": user,
        "guess": guess,
        "is_correct": is_correct
    })

    return jsonify({"status": "Guess and stats updated successfully."}), 201


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
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    import sys
    # Use command-line argument for the port
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    app.run(host="0.0.0.0", port=port)
