from flask import Blueprint, request, jsonify, g
from flask_restful import Api, Resource
from datetime import datetime
from __init__ import app
from api.jwt_authorize import token_required
from model.guess import WordGuess
import random

guess_api = Blueprint('guess_api', __name__, url_prefix='/api')
api = Api(guess_api)

class GuessAPI:
    """
    Define the API CRUD endpoints for the Guess model.
    All endpoints require JWT token authentication.
    """
    class _CRUD(Resource):
        
        @token_required()
        def post(self):
            """Submit a guess and store it with user and correctness status"""
            current_user = g.current_user
            data = request.get_json()

            if not data or "guess" not in data or "correct_word" not in data:
                return jsonify({
                    "message": "Missing required fields",
                    "error": "Bad Request"
                }), 400

            try:
                guess = data['guess'].lower()  # User's guess
                correct_word = data['correct_word'].lower()  # Correct word for validation

                # Determine if the guess is correct
                is_correct = (guess == correct_word)

                # Store the guess along with user info and correctness
                word_guess = WordGuess(
                    guesser_name=current_user.name,
                    guess=guess,
                    is_correct=is_correct,
                    created_by=current_user.id
                )
                
                word_guess.create()  # Save to the database
                return jsonify({
                    "message": "Guess submitted successfully",
                    "guess": word_guess.read(),
                    "correct": is_correct
                }), 201

            except Exception as e:
                return jsonify({
                    "message": "Failed to submit guess",
                    "error": str(e)
                }), 500

        @token_required()
        def get(self):
            """Fetch a specific guess by ID"""
            current_user = g.current_user
            data = request.get_json()

            if not data or "id" not in data:
                return jsonify({
                    "message": "Missing required fields",
                    "error": "Bad Request"
                }), 400

            try:
                guess = WordGuess.query.get(data['id'])
                if not guess:
                    return jsonify({
                        "message": "Guess not found", 
                        "error": "Not Found"
                    }), 404
                
                return jsonify({
                    "message": "Guess fetched successfully",
                    "guess": guess.read()
                }), 200

            except Exception as e:
                return jsonify({
                    "message": "Failed to fetch guess",
                    "error": str(e)
                }), 500

        @token_required()
        def put(self):
            """Update an existing guess with new details"""
            current_user = g.current_user
            data = request.get_json()

            if not data or "id" not in data or "guess" not in data:
                return jsonify({
                    "message": "Missing required fields",
                    "error": "Bad Request"
                }), 400

            try:
                guess = WordGuess.query.get(data['id'])
                if not guess:
                    return jsonify({
                        "message": "Guess not found", 
                        "error": "Not Found"
                    }), 404

                # Ensure the current user is authorized to update this guess
                if guess.created_by != current_user.id and current_user.role != 'Admin':
                    return jsonify({
                        "message": "You are not authorized to update this guess",
                        "error": "Forbidden"
                    }), 403

                # Update the guess with the new guess value
                updated_guess = data['guess'].lower()
                correct_word = data['correct_word'].lower()  # Correct word for validation
                is_correct = (updated_guess == correct_word)

                guess.guess = updated_guess
                guess.is_correct = is_correct
                guess.updated_at = datetime.utcnow()  # Optionally track update time
                guess.update()  # Update the guess in the database

                return jsonify({
                    "message": "Guess updated successfully",
                    "guess": guess.read(),
                    "correct": is_correct
                }), 200

            except Exception as e:
                return jsonify({
                    "message": "Failed to update guess",
                    "error": str(e)
                }), 500

        @token_required()
        def delete(self):
            """Delete a guess"""
            current_user = g.current_user
            data = request.get_json()

            if not data or "id" not in data:
                return jsonify({
                    "message": "Missing required fields",
                    "error": "Bad Request"
                }), 400

            try:
                guess = WordGuess.query.get(data['id'])
                if not guess:
                    return jsonify({
                        "message": "Guess not found", 
                        "error": "Not Found"
                    }), 404

                # Ensure the current user is authorized to delete this guess
                if guess.created_by != current_user.id and current_user.role != 'Admin':
                    return jsonify({
                        "message": "You are not authorized to delete this guess",
                        "error": "Forbidden"
                    }), 403

                # Delete the guess
                guess.delete()

                return jsonify({
                    "message": "Guess deleted successfully"
                }), 200

            except Exception as e:
                return jsonify({
                    "message": "Failed to delete guess",
                    "error": str(e)
                }), 500

                
    # Register API endpoints
    api.add_resource(_CRUD, '/guess')