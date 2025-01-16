from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import threading
import time
import base64
import os
from flask import Blueprint, request, jsonify, current_app

app = Flask(__name__)
competitors_api = Blueprint('competitors_api', __name__)
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

@app.route('/api/start_timer', methods=['POST'])
def start_timer():
    """API endpoint to start the timer."""
    global timer_state

    data = request.json
    duration = data.get("duration")

    if not duration or not isinstance(duration, int) or duration <= 0:
        return jsonify({"error": "Invalid duration. Please provide a positive integer."}), 400

    # Stop any active timer before starting a new one
    timer_state["is_active"] = False

    # Start a new timer thread
    thread = threading.Thread(target=timer_thread, args=(duration,))
    thread.start()

    return jsonify({"message": "Timer started", "duration": duration})

@app.route('/api/timer_status', methods=['GET'])
def timer_status():
    """API endpoint to get the current timer status."""
    return jsonify(timer_state)

@app.route('/api/save_drawing', methods=['POST'])
def save_drawing():
    data = request.json
    canvas_data = data.get("canvasData")

    if not canvas_data or not isinstance(canvas_data, str):
        return jsonify({"error": "Invalid data. Provide a valid Base64-encoded image."}), 400

    try:
        # Decode the Base64 image
        header, encoded = canvas_data.split(",", 1)
        image_data = base64.b64decode(encoded)

        # Save the image on the server
        timestamp = int(time.time())
        filename = f"drawing_{timestamp}.png"
        file_path = os.path.join("saved_drawings", filename)

        # Ensure the directory exists
        os.makedirs("saved_drawings", exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(image_data)

        return jsonify({"message": "Drawing saved on server", "filename": filename})

    except Exception as e:
        # Catch decoding or file writing errors
        return jsonify({"error": f"Failed to save image: {str(e)}"}), 500

@app.route('/api/get_drawings', methods=['GET'])
def get_drawings():
    """API endpoint to fetch all saved drawings with enhanced details."""
    saved_drawings_path = "saved_drawings"
    drawing_details = []

    # Ensure the directory exists
    os.makedirs(saved_drawings_path, exist_ok=True)

    # Iterate through saved drawings and collect detailed info
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

    response = {
        "status": "success",
        "total_drawings": len(drawing_details),
        "drawings": drawing_details
    }

    # Log for debugging purposes
    print("Drawings Data:", response)

    return jsonify(response)


if __name__ == '__main__':
    port = int(os.environ.get("FLASK_RUN_PORT", 8887))
    app.run(host="0.0.0.0", port=port, debug=True)