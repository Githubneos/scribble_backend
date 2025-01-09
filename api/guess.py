from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

# Initialize a Flask application
app = Flask(__name__)

# In-memory storage for chat logs and user stats
chat_logs = []
user_stats = {}

# Utility function to validate input data
def validate_request_data(data, required_keys):
    """Validates that the data contains all required keys."""
    if not data:
        return False, "Request data is missing."
    missing_keys = required_keys - data.keys()
    if missing_keys:
        return False, f"Missing required keys: {', '.join(missing_keys)}"
    return True, None

# API endpoint to get all chat logs
@app.route('/api/guesses', methods=['GET'])
def get_guesses():
    return jsonify(chat_logs), 200

# API endpoint to add a guess and update user stats
@app.route('/api/submit_guess', methods=['POST'])
def save_guess():
    data = request.json  # Expecting JSON input
    required_keys = {'user', 'guess', 'is_correct', 'drawing_id'}
    
    # Validate input data
    is_valid, error_message = validate_request_data(data, required_keys)
    if not is_valid:
        return jsonify({"error": error_message}), 400

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
