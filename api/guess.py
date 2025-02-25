from flask import Blueprint, request, jsonify, g
from flask_restful import Api, Resource
from datetime import datetime
from __init__ import app
from api.jwt_authorize import token_required
import random
from model.guess import Guess 


guess_api = Blueprint('guess_api', __name__, url_prefix='/api')
api = Api(guess_api)

class GuessAPI:
    """
    API CRUD endpoints for the Guess model.
    All endpoints require JWT authentication.
    """

    class _CRUD(Resource):

        @token_required()  # Ensure JWT token is required
        def post(self):
            """Submit a guess and store it with user and correctness status"""
            current_user = g.current_user
            data = request.get_json()

            if not data or "user_guess" not in data or "correct_word" not in data:
                return jsonify({
                    "message": "Missing required fields",
                    "error": "Bad Request"
                }), 400

            try:
                guess = data["user_guess"].strip().lower()
                correct_word = data["correct_word"].strip().lower()

                is_correct = (guess == correct_word)

                word_guess = Guess(
                    guesser_name=current_user.name,
                    guess=guess,
                    correct_answer=correct_word,
                    is_correct=is_correct,
                    created_by=current_user.id,
                    date_created=datetime.utcnow()
                )

                # Save the guess to the database
                word_guess.create()

                return jsonify({
                    "message": "Guess submitted successfully",
                    "guess": word_guess.read(),
                    "correct": is_correct
                }), 201

            except Exception as e:
                # Log the error for debugging
                print("Error occurred while submitting guess:", e)
                return jsonify({
                    "message": "Failed to submit guess",
                    "error": str(e)
                }), 500
                
        @token_required()
        def get(self):
            """Fetch all guesses for the current user"""
            current_user = g.current_user

            try:
                guesses = Guess.query.filter_by(created_by=current_user.id).all()

                if not guesses:
                    return jsonify({
                        "message": "No guesses found",
                        "recent_guesses": []
                    }), 200  # Return an empty list instead of a 404

                return jsonify({
                    "message": "Guesses fetched successfully",
                    "recent_guesses": [guess.read() for guess in guesses]
                }), 200

            except Exception as e:
                print("Error occurred while fetching guesses:", e)
                return jsonify({
                    "message": "Failed to fetch guesses",
                    "error": str(e)
                }), 500

        @token_required()
        def put(self):
            """Update an existing guess"""
            current_user = g.current_user
            data = request.get_json()

            if not data or "id" not in data or "user_guess" not in data or "correct_word" not in data:
                return jsonify({
                    "message": "Missing required fields",
                    "error": "Bad Request"
                }), 400

            try:
                guess = Guess.query.get(data["id"])
                if not guess:
                    return jsonify({"message": "Guess not found", "error": "Not Found"}), 404

                if guess.created_by != current_user.id and current_user.role != "Admin":
                    return jsonify({"message": "You are not authorized to update this guess", "error": "Forbidden"}), 403

                updated_guess = data["user_guess"].strip().lower()
                correct_word = data["correct_word"].strip().lower()
                is_correct = (updated_guess == correct_word)

                guess.guess = updated_guess
                guess.correct_answer = correct_word
                guess.is_correct = is_correct
                guess.updated_at = datetime.utcnow()
                guess.update()

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
                guess = Guess.query.get(data["id"])
                if not guess:
                    return jsonify({"message": "Guess not found", "error": "Not Found"}), 404

                if guess.created_by != current_user.id and current_user.role != "Admin":
                    return jsonify({"message": "You are not authorized to delete this guess", "error": "Forbidden"}), 403

                guess.delete()

                return jsonify({"message": "Guess deleted successfully"}), 200

            except Exception as e:
                return jsonify({
                    "message": "Failed to delete guess",
                    "error": str(e)
                }), 500



                
    # Register API endpoints
    api.add_resource(_CRUD, '/guess')