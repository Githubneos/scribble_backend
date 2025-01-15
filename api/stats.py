from flask import Flask, request, jsonify
from flask_cors import CORS
import os
# Initialize a Flask application
app = Flask(__name__)
# It's better to specify allowed origins explicitly rather than using '*'
CORS(app, supports_credentials=True, origins='*')  # Allow all origins (*)
    
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
    breakpoint()
    return jsonify(statistics)
# API endpoint to update statistics
@app.route('/api/statistics', methods=['POST'])
def update_statistics():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        if 'correct' not in data and 'wrong' not in data:
            return jsonify({"error": "Invalid data. 'correct' or 'wrong' are required."}), 400
        # Validate that the values are integers
        if 'correct' in data:
            try:
                correct_value = int(data['correct'])
                statistics['correct_guesses'] += correct_value
            except ValueError:
                return jsonify({"error": "'correct' value must be an integer"}), 400
        if 'wrong' in data:
            try:
                wrong_value = int(data['wrong'])
                statistics['wrong_guesses'] += wrong_value
            except ValueError:
                return jsonify({"error": "'wrong' value must be an integer"}), 400
        return jsonify({
            "status": "Statistics updated successfully.",
            "current_stats": statistics
        }), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# HTML endpoint for a basic welcome page


if __name__ == '__main__':
    # Set the port dynamically via environment variable or default to 5001
    port = int(os.environ.get("FLASK_RUN_PORT", 8887))
    # In production, set debug=False
    app.run(host="0.0.0.0", port=port, debug=True)


    