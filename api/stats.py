from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
from flask import Blueprint, request, jsonify, g
from flask_cors import CORS
import os
from __init__ import db
from model.statistics_hiroshi import Stats


# Initialize a Flask application
app = Flask(__name__)
CORS(app)
# It's better to specify allowed origins explicitly rather than using '*'

stats_api = Blueprint('stats_api', __name__)
CORS(stats_api, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})


@stats_api.route('/api/statistics', methods=['GET'])
def get_statistics():
    try:
        stats = Stats.query.first()
        if not stats:
            return jsonify({
                "correct_guesses": 0,
                "wrong_guesses": 0,
                "total_rounds": 0
            }), 200
        return jsonify(stats.read()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@stats_api.route('/api/statistics', methods=['POST'])
def update_statistics():
    """Create or update user stats"""
    try:
        data = request.get_json()
        print(f"Received data: {data}")  # Debug log
        
        if not data or 'username' not in data:
            return jsonify({"error": "Username required"}), 400

        # Find or create user
        stats = Stats.query.filter_by(user_name=data['username']).first()
        if not stats:
            # Create new user
            stats = Stats(
                user_name=data['username'],
                correct_guesses=int(data.get('correct', 0)),
                wrong_guesses=int(data.get('wrong', 0)),
                total_rounds=1
            )
            db.session.add(stats)
            print(f"Created new user: {data['username']}")
        else:
            stats.correct_guesses += int(data.get('correct', 0))
            stats.wrong_guesses += int(data.get('wrong', 0))
            stats.total_rounds += 1
            print(f"Updated user: {data['username']}")

        db.session.commit()
        
        # Get fresh data for frontend table
        all_stats = Stats.query.all()
        stats_list = [{
            "username": stat.user_name,
            "correct_guesses": stat.correct_guesses,
            "wrong_guesses": stat.wrong_guesses
        } for stat in all_stats]
        
        return jsonify(stats_list), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@stats_api.route('/api/statistics/all', methods=['GET'])
def get_all_statistics():
    """Get all stats for table display"""
    try:
        all_stats = Stats.query.all()
        stats_list = [{
            "username": stat.user_name,
            "correct_guesses": stat.correct_guesses,
            "wrong_guesses": stat.wrong_guesses
        } for stat in all_stats]
        return jsonify(stats_list), 200
    except Exception as e:
        print(f"Error fetching stats: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("FLASK_RUN_PORT", 8887))
    app.run(host="0.0.0.0", port=port, debug=True)