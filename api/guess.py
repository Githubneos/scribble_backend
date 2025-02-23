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
            # Fetch all guesses by the current user
            user_guesses = WordGuess.query.filter_by(created_by=current_user.id).all()
            
            # If no guesses exist, handle that gracefully
            if not user_guesses:
                return jsonify({
                    "message": "No guesses found for this user.",
                    "total_guesses": 0,
                    "correct_guesses": 0,
                    "accuracy": 0,
                    "avg_hints": 0,
                    "recent_guesses": []
                })
            
            # Filter correct guesses
            correct_guesses = [g for g in user_guesses if g.is_correct]

            # Calculate statistics
            total_guesses = len(user_guesses)
            correct_guesses_count = len(correct_guesses)
            accuracy = correct_guesses_count / total_guesses if total_guesses else 0
            avg_hints = sum(g.hint_used for g in user_guesses) / total_guesses if total_guesses else 0

            # Fetch the most recent guesses (up to 5)
            recent_guesses = [g.read() for g in user_guesses[-5:]]

            return jsonify({
                "total_guesses": total_guesses,
                "correct_guesses": correct_guesses_count,
                "accuracy": accuracy,
                "avg_hints": avg_hints,
                "recent_guesses": recent_guesses
            })

        except Exception as e:
            # Return an error message if an exception occurs
            return jsonify({
                "message": "Failed to fetch statistics",
                "error": str(e)
            }), 500

                
    # Register API endpoints
    api.add_resource(_CRUD, '/guess')
    api.add_resource(_Stats, '/guess/stats')