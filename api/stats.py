from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# Initialize a Flask application
app = Flask(__name__)
CORS(app, supports_credentials=True, origins='*')  # Allow all origins (*)

# In-memory storage for statistics
statistics = {
    "correct_guesses": 0,
    "wrong_guesses": 0
}

# API endpoint to get statistics
@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    return jsonify(statistics)

# API endpoint to update statistics
@app.route('/api/statistics', methods=['POST'])
def update_statistics():
    data = request.json  # Expecting JSON input
    if not data or ('correct' not in data and 'wrong' not in data):
        return jsonify({"error": "Invalid data. 'correct' or 'wrong' are required."}), 400

    # Update the statistics based on input
    if 'correct' in data:
        statistics['correct_guesses'] += int(data['correct'])
    if 'wrong' in data:
        statistics['wrong_guesses'] += int(data['wrong'])

    return jsonify({"status": "Statistics updated successfully.", "current_stats": statistics}), 200

# HTML endpoint for a basic welcome page
@app.route('/')
def say_hello():
    html_content = """
    <html>
    <head>
        <title>Statistics API</title>
    </head>
    <body>
        <h2>Welcome to the Statistics API</h2>
        <p>Use this API to manage and retrieve game statistics.</p>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    # Set the port dynamically via environment variable or default to 5001
    port = int(os.environ.get("FLASK_RUN_PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
