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


@leaderboard_api.route('/api/leaderboard', methods=['PUT'])
def update_leaderboard_entry():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Find existing entry
        existing_entry = LeaderboardEntry.query.filter_by(
            profile_name=data.get('profile_name'),
            drawing_name=data.get('drawing_name')
        ).first()

        new_score = int(data.get('score', 0))

        # If entry exists, update it regardless of score
        if existing_entry:
            existing_entry.score = new_score  # Always update score
            db.session.commit()
            return jsonify({"message": "Score updated successfully"}), 200

        # If no existing entry, create new one
        entry = LeaderboardEntry(
            profile_name=data.get('profile_name'),
            drawing_name=data.get('drawing_name'),
            score=new_score
        )
        
        if entry.create():
            return jsonify({"message": "New entry created"}), 201
        return jsonify({"error": "Failed to create entry"}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@leaderboard_api.route('/api/leaderboard/<profile_name>/<drawing_name>', methods=['DELETE'])
def delete_leaderboard_entry(profile_name, drawing_name):
    try:
        entry = LeaderboardEntry.query.filter_by(
            profile_name=profile_name,
            drawing_name=drawing_name
        ).first()
        
        if not entry:
            return jsonify({"error": "Entry not found"}), 404
            
        entry.delete()
        return jsonify({"message": "Entry deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

