from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True, origins='*')

@app.route('/')
def home():
    return jsonify({"message": "API is running"}), 200

@app.route('/api/authenticate', methods=['GET'])
def authenticate():
    try:
        # Simple authentication response
        return jsonify({
            "status": "success",
            "message": "Authentication successful"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        leaderboard_db = []
        
        leaderboard_db.append({
            "profile_name": "ArtMaster",
            "drawing_name": "Sunset Beach",
            "score": 95
        })
        
        leaderboard_db.append({
            "profile_name": "PixelPro",
            "drawing_name": "Mountain Valley",
            "score": 88
        })
        
        return jsonify(leaderboard_db), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)