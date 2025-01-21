from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask import Blueprint, request, jsonify, g
from flask_cors import CORS  # Import CORS
import os
from model.leaderboard import LeaderboardEntry, db


app = Flask(__name__)
leaderboard_api = Blueprint('leaderboard_api', __name__)
CORS(app)  # Enable CORS for all routes
CORS(leaderboard_api)


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


@leaderboard_api.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        entries = LeaderboardEntry.query.order_by(
            LeaderboardEntry.score.desc()
        ).all()
        return jsonify([entry.read() for entry in entries]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@leaderboard_api.route('/api/leaderboard', methods=['POST'])
def add_leaderboard_entry():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        entry = LeaderboardEntry(
            profile_name=data.get('profile_name'),
            drawing_name=data.get('drawing_name'),
            score=int(data.get('score', 0))
        )
        
        if entry.create():
            return jsonify({"message": "Entry added successfully"}), 201
        return jsonify({"error": "Failed to add entry"}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("FLASK_RUN_PORT", 8887))
    app.run(host="0.0.0.0", port=port, debug=True)

