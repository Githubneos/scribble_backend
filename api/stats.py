from flask import Flask, request, jsonify
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
CORS(stats_api)


@stats_api.route('/api/statistics', methods=['GET'])
def get_statistics():
    try:
        # Get the most recent stats entry
        stats = Stats.query.first()
        if not stats:
            # Return default values if no stats exist
            return jsonify({
                "correct_guesses": 0,
                "wrong_guesses": 0,
                "total_rounds": 0
            })
        return jsonify(stats.read())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@stats_api.route('/api/statistics', methods=['POST'])
def update_statistics():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Get or create stats entry
        stats = Stats.query.first()
        if not stats:
            stats = Stats(user_name="default")
            db.session.add(stats)
            
        correct = int(data.get('correct', 0))
        wrong = int(data.get('wrong', 0))
        
        if stats.update(correct_increment=correct, wrong_increment=wrong):
            db.session.commit()
            return jsonify({
                "status": "success",
                "message": "Statistics updated successfully",
                "current_stats": stats.read()
            }), 200
        
        db.session.rollback()
        return jsonify({"error": "Failed to update statistics"}), 500
            
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("FLASK_RUN_PORT", 8887))
    app.run(host="0.0.0.0", port=port, debug=True)