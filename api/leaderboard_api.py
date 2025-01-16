from flask import Flask, jsonify, request
from datetime import datetime
from datetime import datetime
from flask_restful import Api, Resource
from flask import Blueprint, request, jsonify, current_app
from flask_cors import CORS  # Import CORS
import os

app = Flask(__name__)
leaderboard_api = Blueprint('leaderboard_api', __name__)
CORS(app)  # Enable CORS for all routes

# In-memory database (replace with persistent storage in production)
leaderboard_db = [
    {
        "profile_name": "ArtMaster",
        "drawing_name": "Sunset Beach",
        "score": 95
    },
    {
        "profile_name": "PixelPro",
        "drawing_name": "Mountain Valley",
        "score": 88
    }
]

def get_leaderboard(leaderboard_db):
    """Retrieve the leaderboard entries."""
    try:
        sorted_leaderboard = sorted(leaderboard_db, key=lambda x: x['score'], reverse=True)
        return jsonify(sorted_leaderboard), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def add_leaderboard_entry(leaderboard_db):
    """Add a new entry to the leaderboard."""
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'score' not in data:
            return jsonify({"error": "Missing required fields"}), 400

        # Split name into profile_name and drawing_name
        name_parts = data['name'].split(' - ', 1)
        profile_name = name_parts[0]
        drawing_name = name_parts[1] if len(name_parts) > 1 else "Untitled"

        # Validate score
        try:
            score = int(data['score'])
            if score < 0 or score > 100:
                return jsonify({"error": "Score must be between 0 and 100"}), 400
        except ValueError:
            return jsonify({"error": "Score must be a valid number"}), 400

        new_entry = {
            "profile_name": profile_name,
            "drawing_name": drawing_name,
            "score": score
        }
        leaderboard_db.append(new_entry)  # Append to the shared leaderboard_db
        return jsonify({"message": "Entry added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("FLASK_RUN_PORT", 4887))
    app.run(host="0.0.0.0", port=port, debug=True)