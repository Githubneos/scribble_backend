from flask import Blueprint, request, jsonify, g
from flask_restful import Api, Resource
from datetime import datetime
from __init__ import app
from api.jwt_authorize import token_required
from model.guess import WordGuess
import random

guess_api = Blueprint('guess_api', __name__, url_prefix='/api')
api = Api(guess_api)

# Word list with definitions/hints
WORDS = {
    "algorithm": ["A step-by-step procedure for solving a problem", "Often used in computer science", "A sequence of instructions"],
    "binary": ["Base-2 number system", "Uses only 0s and 1s", "Computer's native language"],
    # ... Add more words and hints (total 150)
}

class GuessAPI:
    """
    Define the API CRUD endpoints for the Guess model.
    All endpoints require JWT token authentication.
    """
    class _CRUD(Resource):
<<<<<<< HEAD
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
=======
        @token_required()
        def post(self):
            """Submit a word guess"""
            current_user = g.current_user
            data = request.get_json()

            if not data or "word" not in data or "guess" not in data:
                return jsonify({
                    "message": "Missing required fields",
                    "error": "Bad Request"
                }), 400

            try:
                word = data['word'].lower()
                guess = data['guess'].lower()
                hint_used = data.get('hint_used', 0)

                # Create guess entry
                word_guess = WordGuess(
                    guesser_name=current_user.name,
                    word=word,
                    hint_used=hint_used,
                    attempts=1,
                    is_correct=(word == guess),
                    created_by=current_user.id
                )
                
                word_guess.create()
                return jsonify({
                    **word_guess.read(),
                    "correct": word == guess
                }), 201

            except Exception as e:
                return jsonify({
                    "message": "Failed to submit guess",
                    "error": str(e)
                }), 500

        def get(self):
            """Get a random word and first hint"""
            word = random.choice(list(WORDS.keys()))
            return jsonify({
                "word_length": len(word),
                "first_hint": WORDS[word][0],
                "word": word  # This will be used by frontend to validate guesses
            })

        @token_required()
        def delete(self):
            """Delete a guess record. Admin only."""
            current_user = g.current_user
            
            if current_user.role != 'Admin':
                return jsonify({
                    "message": "Admin access required",
                    "error": "Forbidden"
                }), 403

            data = request.get_json()
            if not data or "id" not in data:
                return jsonify({
                    "message": "Missing guess ID",
                    "error": "Bad Request"
                }), 400

            try:
                guess = WordGuess.query.get(data['id'])
                if not guess:
                    return jsonify({
                        "message": "Guess not found", 
                        "error": "Not Found"
                    }), 404

                guess.delete()
                return jsonify({
                    "message": "Guess deleted successfully"
                }), 200

>>>>>>> 41e6ee1cdd3ee6e31ef193398e68ac08f37c3656
            except Exception as e:
                return jsonify({
                    "message": "Failed to delete guess",
                    "error": str(e)
                }), 500

    class _Stats(Resource):
        @token_required()
        def get(self):
            """Get user's guessing statistics"""
            current_user = g.current_user
            try:
                user_guesses = WordGuess.query.filter_by(created_by=current_user.id).all()
                correct_guesses = [g for g in user_guesses if g.is_correct]
                
                return jsonify({
                    "total_guesses": len(user_guesses),
                    "correct_guesses": len(correct_guesses),
                    "accuracy": len(correct_guesses) / len(user_guesses) if user_guesses else 0,
                    "avg_hints": sum(g.hint_used for g in user_guesses) / len(user_guesses) if user_guesses else 0,
                    "recent_guesses": [g.read() for g in user_guesses[-5:]]
                })

            except Exception as e:
                return jsonify({
                    "message": "Failed to fetch statistics",
                    "error": str(e)
                }), 500

    class _Hint(Resource):
        @token_required()
        def get(self, word):
            """Get next hint for a word"""
            hints = WORDS.get(word.lower(), [])
            hint_index = int(request.args.get('hint_number', 1))
            
            if hint_index >= len(hints):
                return jsonify({
                    "message": "No more hints available",
                    "error": "Not Found"
                }), 404

            return jsonify({
                "hint": hints[hint_index]
            })

    # Register API endpoints
    api.add_resource(_CRUD, '/guess')
    api.add_resource(_Stats, '/guess/stats')
    api.add_resource(_Hint, '/guess/hint/<string:word>')