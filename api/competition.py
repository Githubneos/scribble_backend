from flask import Flask, request, jsonify, make_response, g
from flask_restful import Api, Resource
from flask import Blueprint
from flask_cors import CORS
from __init__ import app, db
import threading
import os
import time
from model.competition import Time
from api.jwt_authorize import token_required
import random

# Initialize a Flask application
app = Flask(__name__)
CORS(app)

WORDS = [
    "cat", "dog", "house", "tree", "car", "flower", "sun", "moon", "star", "cloud",
    # Add more words as needed
]

competitors_api = Blueprint('competitors_api', __name__, url_prefix='/api')
api = Api(competitors_api)

# Global timer state
timer_state = {
    "time_remaining": 0,
    "is_active": False
}

# Change the timer_durations to store both duration and word
timer_durations = {}  # Will store {user_id: {'duration': int, 'word': str}}

def timer_thread(duration):
    """Background thread to handle the countdown."""
    global timer_state
    timer_state["is_active"] = True
    timer_state["time_remaining"] = duration

    while timer_state["time_remaining"] > 0 and timer_state["is_active"]:
        time.sleep(1)
        timer_state["time_remaining"] -= 1

    timer_state["is_active"] = False

class CompetitionAPI:
    """Define the API CRUD endpoints for the Competition model"""
    
    class _Timer(Resource):
        @token_required()
        def post(self):
            """Start a new timer"""
            current_user = g.current_user
            data = request.get_json()
            
            if not data or "duration" not in data:
                return {
                    "message": "Duration required",
                    "error": "Bad Request"
                }, 400

            try:
                duration = int(data['duration'])
                if duration <= 0:
                    return {
                        "message": "Invalid duration",
                        "error": "Bad Request"
                    }, 400

                # Store both duration and word for this user
                word = random.choice(WORDS)
                timer_durations[current_user.id] = {
                    'duration': duration,
                    'word': word
                }

                # Start timer thread
                thread = threading.Thread(target=timer_thread, args=(duration,))
                thread.start()

                return {
                    "message": "Timer started",
                    "duration": duration,
                    "word": word
                }, 200

            except Exception as e:
                return {
                    "message": "Failed to start timer",
                    "error": str(e)
                }, 500

        @token_required()
        def get(self):
            """Get current timer status"""
            try:
                return {
                    "time_remaining": timer_state["time_remaining"],
                    "is_active": timer_state["is_active"]
                }, 200
            except Exception as e:
                return {
                    "message": "Failed to get timer status",
                    "error": str(e)
                }, 500

        @token_required()
        def put(self):
            """Stop timer and save time entry"""
            current_user = g.current_user
            try:
                timer_data = timer_durations.get(current_user.id)
                if timer_data is None:
                    return {
                        "message": "No timer data found",
                        "error": "Bad Request"
                    }, 400

                duration = timer_data['duration']
                time_taken = duration - timer_state["time_remaining"]
                timer_state["is_active"] = False

                # Create time entry with word
                new_time = Time(
                    users_name=current_user.name,
                    timer_duration=duration,
                    time_taken=time_taken,
                    drawn_word=timer_data['word'],  # Add the word
                    created_by=current_user.id
                )
                
                new_time.create()
                del timer_durations[current_user.id]

                return {
                    "message": "Timer stopped and time saved",
                    "time_entry": new_time.read()
                }, 200

            except Exception as e:
                # Add logging for debugging
                print(f"Error in put method: {str(e)}")
                return {
                    "message": "Failed to stop timer",
                    "error": str(e)
                }, 500

    class _Times(Resource):
        def get(self):
            """Get all times ordered by fastest completion"""
            try:
                entries = Time.query.order_by(Time.time_taken.asc()).all()
                return [entry.read() for entry in entries]
            except Exception as e:
                return []

        @token_required()
        def delete(self):
            """Delete a time entry (Admin only)"""
            current_user = g.current_user
            if current_user.role != 'Admin':
                return {
                    "message": "Admin access required",
                    "error": "Forbidden"
                }, 403

            data = request.get_json()
            if not data or "id" not in data:
                return {
                    "message": "Missing entry ID",
                    "error": "Bad Request"
                }, 400

            try:
                entry = Time.query.get(data['id'])
                if not entry:
                    return {
                        "message": "Entry not found", 
                        "error": "Not Found"
                    }, 404

                entry.delete()
                return {
                    "message": "Entry deleted successfully"
                }, 200

            except Exception as e:
                return {
                    "message": "Failed to delete entry",
                    "error": str(e)
                }, 500

    # Register API endpoints
    api.add_resource(_Timer, '/competition/timer')
    api.add_resource(_Times, '/competition/times')

