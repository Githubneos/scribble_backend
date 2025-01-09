from flask import Flask, jsonify, request
from flask_cors import CORS
import os

# Initialize Flask app
app = Flask(__name__)

# Add max entries limit to prevent memory issues
MAX_LEADERBOARD_ENTRIES = 100

# Update CORS configuration
CORS(app, 
     supports_credentials=True, 
     origins=['http://localhost:4000', 'http://localhost:3000', 'http://0.0.0.0:4000', 'http://127.0.0.1:4000'],
     methods=['GET', 'POST'],
     allow_headers=['Content-Type'])

# Initialize with some example data
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

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        sorted_leaderboard = sorted(leaderboard_db, key=lambda x: x['score'], reverse=True)
        return jsonify(sorted_leaderboard[:MAX_LEADERBOARD_ENTRIES]), 200
    except Exception as e:
        app.logger.error(f"Error in get_leaderboard: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/leaderboard', methods=['POST'])
def add_leaderboard_entry():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        if not all(key in data for key in ['name', 'score']):
            return jsonify({"error": "Missing required fields: name and score"}), 400

        # Validate and sanitize name
        name = str(data['name']).strip()
        if not name:
            return jsonify({"error": "Name cannot be empty"}), 400
        
        if len(name) > 100:
            return jsonify({"error": "Name is too long"}), 400

        # Split and validate name parts (make more lenient to match frontend format)
        if ' - ' in name:
            name_parts = name.split(' - ', 1)
            profile_name = name_parts[0].strip()
            drawing_name = name_parts[1].strip()
        else:
            profile_name = name
            drawing_name = "Untitled"

        # Validate score (match frontend validation)
        try:
            score = int(float(data['score']))
            if not (0 <= score <= 100):
                return jsonify({"error": "Score must be between 0 and 100"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Score must be a valid number"}), 400

        new_entry = {
            "profile_name": profile_name,
            "drawing_name": drawing_name,
            "score": score
        }
        
        # Add new entry and maintain size limit
        if len(leaderboard_db) >= MAX_LEADERBOARD_ENTRIES:
            min_score_entry = min(leaderboard_db, key=lambda x: x['score'])
            if score > min_score_entry['score']:
                leaderboard_db.remove(min_score_entry)
            else:
                return jsonify({"error": "Leaderboard is full and score is too low"}), 400

        leaderboard_db.append(new_entry)
        
        # Return the updated leaderboard immediately
        return jsonify({
            "message": "Entry added successfully",
            "leaderboard": sorted(leaderboard_db, key=lambda x: x['score'], reverse=True)
        }), 201

    except Exception as e:
        app.logger.error(f"Error in add_leaderboard_entry: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Add a health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("FLASK_RUN_PORT", 5001))
    host = os.environ.get("FLASK_RUN_HOST", "0.0.0.0")
    debug = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    
    print(f"Starting server on {host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)