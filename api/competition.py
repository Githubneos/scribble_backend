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

# Initialize a Flask application
app = Flask(__name__)
CORS(app)

competitors_api = Blueprint('competitors_api', __name__, url_prefix='/api')
api = Api(competitors_api)

# Global timer state
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

class CompetitionAPI:
    """Define the API CRUD endpoints for the Competition model"""
    
    class _Timer(Resource):
        @token_required
        def post(self, current_user):
            """Start a new timer"""
            try:
                data = request.get_json()
                duration = data.get("duration")

                if not duration or not isinstance(duration, int) or duration <= 0:
                    return {'message': 'Invalid duration'}, 400

                global timer_state
                timer_state["is_active"] = False
                thread = threading.Thread(target=timer_thread, args=(duration,))
                thread.start()

                return {'message': 'Timer started', 'duration': duration}, 200
            except Exception as e:
                return {'error': str(e)}, 500

        @token_required
        def get(self, current_user):
            """Get current timer status"""
            return jsonify(timer_state)

    class _CRUD(Resource):
        @token_required
        def post(self, current_user):
            """Create a new time entry"""
            try:
                data = request.get_json()
                
                if not data:
                    return {'message': 'No input data provided'}, 400
                
                required_fields = ['users_name', 'timer', 'amount_drawn']
                if not all(field in data for field in required_fields):
                    return {'message': 'Missing required fields'}, 400

                new_time = Time(
                    users_name=data['users_name'],
                    timer=data['timer'],
                    amount_drawn=data['amount_drawn']
                )
                
                db.session.add(new_time)
                db.session.commit()
                
                return {'message': 'Time entry created successfully'}, 201
            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}, 500

        @token_required
        def get(self, current_user):
            """Get a specific time entry"""
            try:
                data = request.get_json()
                if not data or 'id' not in data:
                    return {'message': 'Time entry ID required'}, 400

                time_entry = Time.query.get(data['id'])
                if not time_entry:
                    return {'message': 'Time entry not found'}, 404

                return jsonify(time_entry.read())
            except Exception as e:
                return {'error': str(e)}, 500

        @token_required
        def put(self, current_user):
            """Update a time entry"""
            try:
                data = request.get_json()
                if not data or 'id' not in data:
                    return {'message': 'Time entry ID required'}, 400

                time_entry = Time.query.get(data['id'])
                if not time_entry:
                    return {'message': 'Time entry not found'}, 404

                time_entry.users_name = data.get('users_name', time_entry.users_name)
                time_entry.timer = data.get('timer', time_entry.timer)
                time_entry.amount_drawn = data.get('amount_drawn', time_entry.amount_drawn)
                
                db.session.commit()
                return {'message': 'Time entry updated successfully'}, 200
            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}, 500

        @token_required
        def delete(self, current_user):
            """Delete a time entry"""
            try:
                data = request.get_json()
                if not data or 'id' not in data:
                    return {'message': 'Time entry ID required'}, 400

                time_entry = Time.query.get(data['id'])
                if not time_entry:
                    return {'message': 'Time entry not found'}, 404

                db.session.delete(time_entry)
                db.session.commit()
                return {'message': 'Time entry deleted successfully'}, 200
            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}, 500

    class _List(Resource):
        @token_required
        def get(self, current_user):
            """Get all time entries"""
            try:
                times = Time.query.all()
                return jsonify([time.read() for time in times])
            except Exception as e:
                return {'error': str(e)}, 500

    # Register API endpoints
    api.add_resource(_Timer, '/competition/timer')
    api.add_resource(_CRUD, '/competition')
    api.add_resource(_List, '/competition/all')

if __name__ == '__main__':
    port = int(os.environ.get("FLASK_RUN_PORT", 8023))
    app.register_blueprint(competitors_api)
    app.run(host="0.0.0.0", port=port, debug=True)
