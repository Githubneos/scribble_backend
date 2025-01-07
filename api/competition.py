from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import threading
import time
import base64
import os

app = Flask(__name__)
CORS(app, supports_credentials=True, origins='*')

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
    """API endpoint to save drawing data."""
    data = request.json
    canvas_data = data.get("canvasData")

    if not canvas_data or not isinstance(canvas_data, str):
        return jsonify({"error": "Invalid data. Provide a valid Base64-encoded image."}), 400

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

@app.route('/api/get_drawings', methods=['GET'])
def get_drawings():
    """API endpoint to fetch all saved drawings."""
    return jsonify(drawings)

@app.route('/')
def serve_html():
    """Serve the drawing board HTML."""
    html_content = """
    ---
layout: post
title: Competition
search_exclude: true
description: Competition
permalink: /competition
Author: Ian
---
<div>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Arial', sans-serif;
        }
        body {
            background-color: #282c34;
            color: white;
            text-align: center;
            height: 100vh;
        }
         h1 {
            margin: 20px 0;
            font-size: 2.5em;
            color: #61dafb;
        }
         #drawing-board {
            border: 3px solid #61dafb;
            background-color: #444;
            display: block;
            margin: 20px auto;
            border-radius: 10px;
        }
        .controls {
            margin: 20px auto;
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
        }
         .controls input, .controls button, .controls select {
            padding: 10px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
        }
        .controls input[type="color"] {
            height: 40px;
            width: 60px;
            padding: 0;
            cursor: pointer;
            border: 2px solid #61dafb;
            border-radius: 5px;
        }
        .controls button {
            background-color: #4CAF50;
            color: white;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        .controls button:hover {
            background-color: #45a049;
        }
        #timer-display {
            margin: 15px auto;
            font-size: 1.2em;
        }
        .footer {
            margin-top: 20px;
            font-size: 0.9em;
            color: #aaa;
        }
    </style>
    <h1>🎨 Welcome to Scribble Art 🎨</h1>
    <canvas id="drawing-board" width="800" height="500"></canvas>
    <div class="controls">
        <input type="color" id="color-picker" value="#ffffff" title="Choose a color">
        <select id="line-width" title="Brush size">
            <option value="2">Thin</option>
            <option value="5" selected>Medium</option>
            <option value="10">Thick</option>
            <option value="15">Extra Thick</option>
        </select>
        <button id="erase-button">Erase</button>
        <button id="clear-button">Clear Board</button>
        <input type="number" id="timer-input" placeholder="Time (s)">
        <button id="start-button">Start Timer</button>
    </div>
    <p id="timer-display">Timer: Not started</p>
    <div class="footer">Enjoy your time creating art and having fun!</div>
</div>
<button id="save-button">Save Drawing</button>

<script>
    const canvas = document.getElementById('drawing-board');
    const ctx = canvas.getContext('2d');
    const colorPicker = document.getElementById('color-picker');
    const lineWidthPicker = document.getElementById('line-width');
    const eraseButton = document.getElementById('erase-button');
    const clearButton = document.getElementById('clear-button');
    const timerInput = document.getElementById('timer-input');
    const timerDisplay = document.getElementById('timer-display');
    const startButton = document.getElementById('start-button');

    let drawingAllowed = false;
    let currentColor = colorPicker.value;
    let lineWidth = parseInt(lineWidthPicker.value);
    let erasing = false;

    let interval = null; // Reference for the interval (setInterval)
    let timerStarted = false; // Track if the timer has already started

    // Setup drawing
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mousemove', draw);

    // Getting button from html
    document.getElementById('save-button').addEventListener('click', saveDrawing);

    function startDrawing() {
        // If timer hasn't started yet, start it automatically
        if (!timerStarted) {
            let timeInSeconds = parseInt(timerInput.value);

            if (isNaN(timeInSeconds) || timeInSeconds <= 0) {
                // If no valid timer value entered, pick a random value between 20-100 seconds
                timeInSeconds = Math.floor(Math.random() * (30 - 20 + 1)) + 20;
            }

            startTimer(timeInSeconds);
        }
        drawingAllowed = true;
        ctx.beginPath();
    }

    function stopDrawing() {
        drawingAllowed = false;
        ctx.beginPath(); // Reset path
    }

    function draw(event) {
        if (!drawingAllowed) return;

        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        ctx.lineWidth = lineWidth;
        ctx.lineCap = "round";

        if (erasing) {
            ctx.strokeStyle = "#444"; // Match background color
        } else {
            ctx.strokeStyle = currentColor;
        }

        ctx.lineTo(x, y);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(x, y);
    }

    // Color Picker
    colorPicker.addEventListener('input', () => {
        currentColor = colorPicker.value;
        erasing = false; // Stop erasing if a new color is chosen
    });

    // Line Width Picker
    lineWidthPicker.addEventListener('change', () => {
        lineWidth = parseInt(lineWidthPicker.value);
    });

    // Erase Button
    eraseButton.addEventListener('click', () => {
        erasing = true;
    });

    // Clear Button
    clearButton.addEventListener('click', () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        erasing = false;
    });

    // Timer functionality (handles both random and user-defined time)
    function startTimer(timeInSeconds) {
        // Start timer only if it's not already started
        if (timerStarted) return;

        timerStarted = true;
        startButton.disabled = true;  // Disable the start button after the timer starts
        timerDisplay.textContent = `Timer: ${timeInSeconds} seconds left`;

        let timeRemaining = timeInSeconds;

        // Start a new interval for the countdown
        interval = setInterval(() => {
            timeRemaining--;
            timerDisplay.textContent = `Timer: ${timeRemaining} seconds left`;

            if (timeRemaining <= 0) {
                clearInterval(interval);
                drawingAllowed = false;  // Disable drawing after the timer ends
                timerDisplay.textContent = "Timer: Time's up!";
                alert('Time is up! Hope you enjoyed drawing!');

                // Disable drawing and prevent re-enabling of the timer
                canvas.style.pointerEvents = "none";  // Disable canvas interaction
                startButton.disabled = true;  // Disable the timer button again after the timer ends
                eraseButton.disabled = true;  // Disable the erase button
                clearButton.disabled = true;  // Disable the clear board button
            }
        }, 1000);
    }
    function saveDrawing() {
        const canvasData = canvas.toDataURL(); // Base64 string of the canvas

        // Step 1: Save the drawing on the server
        fetch('/api/save_drawing', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ canvasData })
        })
            .then(response => response.json())
            .then(data => console.log("Saved on server:", data))
            .catch(error => console.error("Error saving on server:", error));

        // Step 2: Prompt the user to save the drawing locally
        const link = document.createElement('a');
        link.href = canvasData;
        link.download = 'drawing.png'; // Default filename
        link.click(); // Trigger the download
    }
</script>
    """
    return render_template_string(html_content)

if __name__ == '__main__':
    app.run(port=5001)