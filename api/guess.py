from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from datetime import datetime
from __init__ import app, db
from api.jwt_authorize import token_required
from model.guess import Guess

guess_api = Blueprint('guess_api', __name__, url_prefix='/api')
api = Api(guess_api)

class GuessAPI:
    """
    Define the API CRUD endpoints for the Guess model.
    All endpoints require JWT token authentication.
    """
    class _CRUD(Resource):
        @token_required
        def post(self, current_user):
            """Create a new guess"""
            try:
                data = request.get_json()
                
                if not data:
                    return {'message': 'No input data provided'}, 400
                if 'guesser_name' not in data:
                    return {'message': 'Guesser name is required'}, 400
                if 'guess' not in data:
                    return {'message': 'Guess value is required'}, 400
                if 'is_correct' not in data:
                    return {'message': 'Correctness status is required'}, 400

                guess = Guess(
                    guesser_name=data['guesser_name'],
                    guess=data['guess'],
                    is_correct=data['is_correct']
                )
                
                if guess.create():
                    return jsonify(guess.read()), 201
                return {'message': 'Failed to create guess'}, 400

            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}, 500

        @token_required
        def get(self, current_user):
            """Get a specific guess by ID"""
            try:
                data = request.get_json()
                if not data or 'id' not in data:
                    return {'message': 'Guess ID is required'}, 400

                guess = Guess.query.get(data['id'])
                if not guess:
                    return {'message': 'Guess not found'}, 404

                return jsonify(guess.read())
            except Exception as e:
                return {'error': str(e)}, 500

        @token_required
        def delete(self, current_user):
            """Delete a guess"""
            try:
                data = request.get_json()
                if not data or 'id' not in data:
                    return {'message': 'Guess ID is required'}, 400

                guess = Guess.query.get(data['id'])
                if not guess:
                    return {'message': 'Guess not found'}, 404

                guess.delete()
                return {'message': 'Guess deleted successfully'}, 200
            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}, 500

    class _List(Resource):
        @token_required
        def get(self, current_user):
            """Get all guesses"""
            try:
                guesses = Guess.query.all()
                return jsonify([guess.read() for guess in guesses])
            except Exception as e:
                return {'error': str(e)}, 500

    # Register API endpoints
    api.add_resource(_CRUD, '/guess')
    api.add_resource(_List, '/guesses')