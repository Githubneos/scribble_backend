from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask import Blueprint, request, jsonify, g
from flask_cors import CORS
import os
# Initialize a Flask application
app = Flask(__name__)
# It's better to specify allowed origins explicitly rather than using '*'

stats_api = Blueprint('stats_api', __name__)



statistics = {
    "correct_guesses": 76,
    "wrong_guesses": 52,
    "hints_used": 1,
    "total_rounds": 20,
    "current_streak": 3
}

# API endpoint to get statistics
@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    return jsonify(statistics)

# API endpoint to update statistics
@app.route('/api/statistics', methods=['POST'])
def update_statistics():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        correct_value = int(data.get('correct', 0))
        wrong_value = int(data.get('wrong', 0))

        statistics['correct_guesses'] += correct_value
        statistics['wrong_guesses'] += wrong_value
        statistics['total_rounds'] += (correct_value + wrong_value)

        return jsonify({
            "status": "Statistics updated successfully.",
            "current_stats": statistics
        }), 200
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid data provided. Ensure 'correct' and 'wrong' are integers."}), 400

if __name__ == '__main__':
    port = int(os.environ.get("FLASK_RUN_PORT", 8887))
    app.run(host="0.0.0.0", port=port, debug=True)