from flask import Flask, request, jsonify, make_response, g
from flask_restful import Api, Resource
from flask import Blueprint
from flask_cors import CORS
from __init__ import app, db
import threading
import base64
import os
import time
from model.competition import UserAttempts

# Initialize a Flask application
app = Flask(__name__)
CORS(app)

competitors_api = Blueprint('competitors_api', __name__)
CORS(competitors_api)

class _UserAttemptsCRUD(Resource):
    def post(self):
        """Create a new user attempt"""
        try:
            data = request.get_json()
            if not data:
                return {'message': 'No data provided'}, 400

            new_user_attempt = UserAttempts(
                user_name=data.get('user_name'),
                attempts_made=data.get('attempts_made'),
                time_taken=data.get('time_taken')
            )
            
            db.session.add(new_user_attempt)
            db.session.commit()
            return {'message': 'User attempt added successfully'}, 201

        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def get(self):
        """Retrieve all user attempts"""
        try:
            users = UserAttempts.query.all()
            return jsonify([user.read() for user in users]), 200
        except Exception as e:
            return {'error': str(e)}, 500

    def put(self):
        """Update a user attempt"""
        try:
            data = request.get_json()
            if not data:
                return {'message': 'No data provided'}, 400

            user_attempt = UserAttempts.query.get(data.get('user_id'))
            if not user_attempt:
                return {'message': 'User attempt not found'}, 404

            user_attempt.user_name = data.get('user_name', user_attempt.user_name)
            user_attempt.attempts_made = data.get('attempts_made', user_attempt.attempts_made)
            user_attempt.time_taken = data.get('time_taken', user_attempt.time_taken)
            db.session.commit()
            return {'message': 'User attempt updated successfully'}, 200

        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def delete(self):
        """Delete a user attempt"""
        try:
            data = request.get_json()
            if not data:
                return {'message': 'No data provided'}, 400

            user_attempt = UserAttempts.query.get(data.get('user_id'))
            if not user_attempt:
                return {'message': 'User attempt not found'}, 404

            db.session.delete(user_attempt)
            db.session.commit()
            return {'message': 'User attempt deleted successfully'}, 200

        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

# Add the resource to the API
api = Api(competitors_api)
api.add_resource(_UserAttemptsCRUD, '/api/user_attempts/crud')

@competitors_api.route('/api/user_attempts', methods=['GET'])
def get_user_attempts():
    try:
        users = UserAttempts.query.all()
        return jsonify([user.read() for user in users]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@competitors_api.route('/api/user_attempts', methods=['POST'])
def add_user_attempt():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        new_user_attempt = UserAttempts(
            user_name=data.get('user_name'),
            attempts_made=data.get('attempts_made'),
            time_taken=data.get('time_taken')
        )
        
        db.session.add(new_user_attempt)
        db.session.commit()
        return jsonify({"message": "User attempt added successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@competitors_api.route('/api/user_attempts', methods=['PUT'])
def update_user_attempt():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        user_attempt = UserAttempts.query.get(data.get('user_id'))
        if not user_attempt:
            return jsonify({"error": "User attempt not found"}), 404

        user_attempt.user_name = data.get('user_name', user_attempt.user_name)
        user_attempt.attempts_made = data.get('attempts_made', user_attempt.attempts_made)
        user_attempt.time_taken = data.get('time_taken', user_attempt.time_taken)
        db.session.commit()
        return jsonify({"message": "User attempt updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@competitors_api.route('/api/user_attempts', methods=['DELETE'])
def delete_user_attempt():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        user_attempt = UserAttempts.query.get(data.get('user_id'))
        if not user_attempt:
            return jsonify({"error": "User attempt not found"}), 404

        db.session.delete(user_attempt)
        db.session.commit()
        return jsonify({"message": "User attempt deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("FLASK_RUN_PORT", 8887))
    app.register_blueprint(competitors_api)
    app.run(host="0.0.0.0", port=port, debug=True)
