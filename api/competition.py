from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import threading
import time

app = Flask(__name__)
CORS(app, supports_credentials=True, origins='*')

# Global variable to track timer state
timer_state = {
    "time_remaining": 0,
    "is_active": False
}

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

@app.route('/api/data')
def get_data():
    """Demo endpoint for InfoDb."""
    InfoDb = [
        {
            "FirstName": "John",
            "LastName": "Mortensen",
            "DOB": "October 21",
            "Residence": "San Diego",
            "Email": "jmortensen@powayusd.com",
            "Owns_Cars": ["2015-Fusion", "2011-Ranger", "2003-Excursion", "1997-F350", "1969-Cadillac"]
        },
        {
            "FirstName": "Shane",
            "LastName": "Lopez",
            "DOB": "February 27",
            "Residence": "San Diego",
            "Email": "slopez@powayusd.com",
            "Owns_Cars": ["2021-Insight"]
        }
    ]

    return jsonify(InfoDb)

@app.route('/')
def serve_html():
    """Serve the drawing board HTML."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Drawing Board</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                background-color: #282c34;
                color: white;
                padding: 20px;
                height: 100vh;
                margin: 0;
            }

            #drawing-board {
                border: 2px solid white;
                background-color: #444;
                margin: 20px auto;
                display: block;
            }

            .controls {
                margin: 20px auto;
                display: flex;
                justify-content: center;
                gap: 10px;
            }

            .controls input, .controls button {
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
            }

            .controls input {
                width: 150px;
            }

            .controls button {
                background-color: #4CAF50;
                color: white;
                cursor: pointer;
            }

            .controls button:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <h1>Drawing Board</h1>
        <canvas id="drawing-board" width="600" height="400"></canvas>
        <div class="controls">
            <input type="number" id="timer-input" placeholder="Enter time (s)">
            <button id="start-button">Start Timer</button>
        </div>
        <p id="timer-display">Timer: Not started</p>

        <script>
            const canvas = document.getElementById('drawing-board');
            const ctx = canvas.getContext('2d');
            const timerInput = document.getElementById('timer-input');
            const timerDisplay = document.getElementById('timer-display');
            const startButton = document.getElementById('start-button');

            let drawingAllowed = false;

            // Setup drawing
            canvas.addEventListener('mousedown', () => drawingAllowed = true);
            canvas.addEventListener('mouseup', () => drawingAllowed = false);
            canvas.addEventListener('mousemove', draw);

            function draw(event) {
                if (!drawingAllowed) return;

                const rect = canvas.getBoundingClientRect();
                const x = event.clientX - rect.left;
                const y = event.clientY - rect.top;

                ctx.fillStyle = "white";
                ctx.beginPath();
                ctx.arc(x, y, 5, 0, Math.PI * 2);
                ctx.fill();
            }

            // Timer functionality
            startButton.addEventListener('click', async () => {
                const timeInSeconds = parseInt(timerInput.value);

                if (isNaN(timeInSeconds) || timeInSeconds <= 0) {
                    alert('Please enter a valid time in seconds.');
                    return;
                }

                try {
                    const response = await fetch('/api/start_timer', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ duration: timeInSeconds })
                    });

                    if (!response.ok) {
                        alert('Failed to start timer.');
                        return;
                    }

                    const timerCheck = setInterval(async () => {
                        const statusResponse = await fetch('/api/timer_status');
                        const status = await statusResponse.json();

                        if (status.is_active) {
                            timerDisplay.textContent = `Timer: ${status.time_remaining} seconds left`;
                        } else {
                            clearInterval(timerCheck);
                            timerDisplay.textContent = "Timer: Time's up!";
                            alert('Time is up! Thanks for drawing.');
                        }
                    }, 1000);

                } catch (error) {
                    console.error('Error starting timer:', error);
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

if __name__ == '__main__':
    app.run(port=5001)
    
