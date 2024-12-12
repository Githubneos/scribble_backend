from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize a Flask application
app = Flask(__name__)
CORS(app, supports_credentials=True, origins='*')  # Allow all origins (*)

# In-memory storage for chat logs
chat_logs = []

# API endpoint to get all chat logs
@app.route('/api/chatlogs', methods=['GET'])
def get_chat_logs():
    return jsonify(chat_logs)

# API endpoint to add a chat message
@app.route('/api/chatlogs', methods=['POST'])
def save_chat_message():
    data = request.json  # Expecting JSON input
    if not data or 'user' not in data or 'message' not in data:
        return jsonify({"error": "Invalid data. 'user' and 'message' are required."}), 400

    # Append new message to chat logs
    chat_logs.append({
        "user": data['user'],
        "message": data['message']
    })
    return jsonify({"status": "Message saved successfully."}), 201

# HTML endpoint for a basic welcome page
@app.route('/')
def say_hello():
    html_content = """
    <html>
    <head>
        <title>Chat Logs API</title>
    </head>
    <body>
        <h2>Welcome to the Chat Logs API</h2>
        <p>Use the API to save and retrieve chat logs.</p>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    # Start Flask server on default port, http://127.0.0.1:5001
    app.run(port=8887)
