from flask import Flask, request, jsonify, make_response, g
from flask_restful import Api, Resource
from flask import Blueprint
from flask_cors import CORS
from __init__ import app, db
import threading
import base64
import os
import time
from model.competition import Time

# Initialize a Flask application
app = Flask(__name__)
CORS(app)

competitors_api = Blueprint('competitors_api', __name__)
CORS(competitors_api, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Global variables for timer state and drawing storage
timer_state = {
    "time_remaining": 0,
    "is_active": False
}
drawings = []

def timer_thread(duration):
    """Background thread to handle the countdown."""
    global timer_state
    timer_state["is_active"] = True
    timer_state["time_remaining"] = duration

    while timer_state["time_remaining"] > 0 and timer_state["is_active"]:
        time.sleep(1)
        timer_state["time_remaining"] -= 1

    timer_state["is_active"] = False

@competitors_api.route('/api/start_timer', methods=['POST'])
def start_timer():
    """API endpoint to start the timer."""
    global timer_state
    data = request.json
    duration = data.get("duration")

    if not duration or not isinstance(duration, int) or duration <= 0:
        return jsonify({"error": "Invalid duration. Please provide a positive integer."}), 400

    timer_state["is_active"] = False
    thread = threading.Thread(target=timer_thread, args=(duration,))
    thread.start()

    return jsonify({"message": "Timer started", "duration": duration})

@competitors_api.route('/api/timer_status', methods=['GET'])
def timer_status():
    """API endpoint to get the current timer status."""
    return jsonify(timer_state)

@competitors_api.route('/api/save_drawing', methods=['POST'])
def save_drawing():
    data = request.json
    canvas_data = data.get("canvasData")

    if not canvas_data or not isinstance(canvas_data, str):
        return jsonify({"error": "Invalid data. Provide a valid Base64-encoded image."}), 400

    try:
        header, encoded = canvas_data.split(",", 1)
        image_data = base64.b64decode(encoded)
        timestamp = int(time.time())
        filename = f"drawing_{timestamp}.png"
        file_path = os.path.join("saved_drawings", filename)
        os.makedirs("saved_drawings", exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(image_data)

        return jsonify({"message": "Drawing saved on server", "filename": filename})
    except Exception as e:
        return jsonify({"error": f"Failed to save image: {str(e)}"}), 500

@competitors_api.route('/api/get_drawings', methods=['GET'])
def get_drawings():
    """API endpoint to fetch all saved drawings."""
    saved_drawings_path = "saved_drawings"
    drawing_details = []
    os.makedirs(saved_drawings_path, exist_ok=True)

    for filename in os.listdir(saved_drawings_path):
        file_path = os.path.join(saved_drawings_path, filename)
        if os.path.isfile(file_path):
            file_info = {
                "filename": filename,
                "path": file_path,
                "size_in_bytes": os.path.getsize(file_path),
                "last_modified": time.ctime(os.path.getmtime(file_path))
            }
            drawing_details.append(file_info)

    return jsonify({"status": "success", "total_drawings": len(drawing_details), "drawings": drawing_details})

@competitors_api.route('/api/times', methods=['GET', 'POST'])
def manage_times():
    if request.method == 'GET':
        times = Time.query.all()
        return jsonify([time.read() for time in times]), 200
    
    if request.method == 'POST':
        data = request.json
        new_time = Time(
            users_name=data.get('users_name'),
            timer=data.get('timer'),
            amount_drawn=data.get('amount_drawn')
        )
        db.session.add(new_time)
        db.session.commit()
        return jsonify({"message": "Time entry added successfully"}), 201

@competitors_api.route('/api/times/<int:time_id>', methods=['PUT', 'DELETE'])
def modify_time(time_id):
    time_entry = Time.query.get(time_id)
    if not time_entry:
        return jsonify({"error": "Time entry not found"}), 404
    
    if request.method == 'PUT':
        data = request.json
        time_entry.users_name = data.get('users_name', time_entry.users_name)
        time_entry.timer = data.get('timer', time_entry.timer)
        time_entry.amount_drawn = data.get('amount_drawn', time_entry.amount_drawn)
        db.session.commit()
        return jsonify({"message": "Time entry updated successfully"})
    
    if request.method == 'DELETE':
        db.session.delete(time_entry)
        db.session.commit()
        return jsonify({"message": "Time entry deleted successfully"})

if __name__ == '__main__':
    port = int(os.environ.get("FLASK_RUN_PORT", 8887))
    app.register_blueprint(competitors_api)
    app.run(host="0.0.0.0", port=port, debug=True)
