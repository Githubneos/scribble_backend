from flask import Flask, request, jsonify, render_template
from datetime import datetime
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app


app = Flask(__name__)
guess_api = Blueprint('guess_api', __name__)


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

# Serve the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to get all chat logs
@app.route('/api/guesses', methods=['GET'])
def get_guesses():
    print("GET /api/guesses route was hit")  # Debugging line
    return jsonify(chat_logs), 200

# API endpoint to add a guess and update user stats
@app.route('/api/submit_guess', methods=['POST'])
def save_guess():
    try:
        # Debugging: Log the incoming request
        print("Incoming request data:", request.json)

        # Parse JSON input
        data = request.json  # Expecting JSON input
        required_keys = {'user', 'guess', 'is_correct'}

        # Validate input data
        is_valid, error_message = validate_request_data(data, required_keys)
        if not is_valid:
            print("Validation failed:", error_message)  # Debugging
            return jsonify({"error": error_message}), 400

        # Extract values from the request
        user = data['user']
        guess = data['guess']
        is_correct = data['is_correct']
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

        # Append guess details to the user's history
        user_stats[user]["guesses"].append({
            "guess": guess,
            "is_correct": is_correct,
            "timestamp": timestamp
        })

        # Append new guess to global chat logs
        chat_logs.append({
            "user": user,
            "guess": guess,
            "is_correct": is_correct,
            "timestamp": timestamp
        })

        # Return success response
        return jsonify({"status": "Guess and stats updated successfully."}), 201

    except KeyError as e:
        print("KeyError:", str(e))  # Log and handle missing keys
        return jsonify({"error": f"Missing key: {str(e)}"}), 400
    except TypeError as e:
        print("TypeError:", str(e))  # Log and handle type errors
        return jsonify({"error": f"Type error: {str(e)}"}), 400
    except Exception as e:
        # Log unexpected exceptions and provide better debugging info
        print("General Exception:", str(e))
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# API endpoint to retrieve stats for a specific user
@app.route('/api/user_stats/<string:username>', methods=['GET'])
def get_user_stats(username):
    try:
        user_stat = user_stats.get(username)

        if not user_stat:
            return jsonify({"error": f"No stats found for user '{username}'."}), 404

        return jsonify(user_stat), 202
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app on localhost with port 8887
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8887)
