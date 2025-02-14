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

            # Validate input data
            if not data:
                return {'message': 'No input data provided'}, 400
            if 'guesser_name' not in data:
                return {'message': 'Guesser name is required'}, 400
            if 'guess' not in data:
                return {'message': 'Guess value is required'}, 400
            if 'is_correct' not in data:
                return {'message': 'Correctness status is required'}, 400
            if 'image_label' not in data:
                return {'message': 'Image label is required'}, 400
            if 'hints_used' not in data:
                return {'message': 'Hints used is required'}, 400

            # Create new guess entry
            guess = Guess(
                guesser_name=data['guesser_name'],
                guess=data['guess'],
                is_correct=data['is_correct'],
                image_label=data['image_label'],
                hints_used=data['hints_used']  # Hints used field
            )

            # Try to save the guess, commit transaction manually
            db.session.add(guess)
            db.session.commit()
            return jsonify(guess.read()), 201

        except Exception as e:
            db.session.rollback()  # Rollback any changes if an error occurs
            return {'error': str(e)}, 500

    @token_required
    def get(self, current_user):
        """Get guesses for a specific image label"""
        try:
            # Use query params to get image_label
            image_label = request.args.get('image_label')
            if not image_label:
                return {'message': 'Image label is required'}, 400

            # Get guesses for the provided image_label
            guesses = Guess.query.filter_by(image_label=image_label).all()
            if not guesses:
                return {'message': 'No guesses found for the given image label'}, 404

            # Return guesses data
            return jsonify([guess.read() for guess in guesses])

        except Exception as e:
            return {'error': str(e)}, 500

    @token_required
    def put(self, current_user):
        """Update a guess based on guess ID"""
        try:
            data = request.get_json()
            if not data or 'guess_id' not in data or 'guess' not in data:
                return {'message': 'Guess ID and new guess value are required'}, 400

            # Find the guess by its ID
            guess = Guess.query.get(data['guess_id'])
            if not guess:
                return {'message': 'Guess not found for the given guess ID'}, 404

            # Update guess details
            guess.guess = data['guess']
            guess.is_correct = data.get('is_correct', guess.is_correct)  # Optional update for correctness
            guess.hints_used = data.get('hints_used', guess.hints_used)  # Optional update for hints used

            db.session.commit()  # Commit the changes manually

            return jsonify(guess.read()), 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @token_required
    def delete(self, current_user):
        """Delete a guess based on guess ID"""
        try:
            data = request.get_json()
            if not data or 'guess_id' not in data:
                return {'message': 'Guess ID is required'}, 400

            # Find and delete the guess by ID
            guess = Guess.query.get(data['guess_id'])
            if not guess:
                return {'message': 'Guess not found for the given guess ID'}, 404

            db.session.delete(guess)  # Delete guess
            db.session.commit()  # Commit deletion

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