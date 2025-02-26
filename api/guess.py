import traceback
from flask import Blueprint, request, jsonify, g
from flask_restful import Api, Resource
from datetime import datetime
from __init__ import app
from api.jwt_authorize import token_required
import random
from model.guess import Guess 
from flask import Blueprint, request, g
from flask_restful import Api, Resource
from datetime import datetime
from __init__ import app
from api.jwt_authorize import token_required
from __init__ import app, db

guess_api = Blueprint('guess_api', __name__, url_prefix='/api')
api = Api(guess_api)

class GuessAPI:
    """
    API CRUD endpoints for the Guess model.
    All endpoints require JWT authentication.
    """

    class _CRUD(Resource):

        @token_required()
        def post(self):
            """Submit a guess and store it with user and correctness status"""
            try:
                current_user = g.current_user
                data = request.get_json()

                if not data or "user_guess" not in data or "correct_word" not in data:
                    return jsonify({"message": "Missing required fields", "error": "Bad Request"}), 400

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

                db.session.add(word_guess)
                db.session.commit()  # Commit to database

                return jsonify({
                    "message": "Guess submitted successfully",
                    "guess": word_guess.read(),
                    "correct": is_correct
                }), 201

            except Exception as e:
                db.session.rollback()  # Rollback any failed transactions
                print("Error occurred while submitting guess:", str(e))
                traceback.print_exc()  # Debugging
                return jsonify({"message": "Internal Server Error", "error": str(e)}), 500
                
        @token_required()
        def get(self):
            """Fetch all guesses for the current user"""
            try:
                current_user = g.current_user
                guesses = Guess.query.filter_by(created_by=current_user.id).all()

                if not guesses:
                    return jsonify({"message": "No guesses found", "recent_guesses": []}), 200  

                return jsonify({
                    "message": "Guesses fetched successfully",
                    "recent_guesses": [guess.read() for guess in guesses]
                }), 200

            except Exception as e:
                print("Error occurred while fetching guesses:", str(e))
                traceback.print_exc()
                return jsonify({"message": "Internal Server Error", "error": str(e)}), 500

        @token_required()
        def put(self):
            """Update an existing guess"""
            try:
                current_user = g.current_user
                data = request.get_json()

                if not data or "id" not in data or "user_guess" not in data or "correct_word" not in data:
                    return jsonify({"message": "Missing required fields", "error": "Bad Request"}), 400

                guess = Guess.query.get(data["id"])
                if not guess:
                    return jsonify({"message": "Guess not found", "error": "Not Found"}), 404

                if guess.created_by != current_user.id:
                    return jsonify({"message": "Unauthorized to update this guess", "error": "Forbidden"}), 403

                guess.guess = data["user_guess"].strip().lower()
                guess.correct_answer = data["correct_word"].strip().lower()
                guess.is_correct = (guess.guess == guess.correct_answer)
                db.session.commit()  # Commit update

                return jsonify({"message": "Guess updated successfully", "guess": guess.read()}), 200

            except Exception as e:
                db.session.rollback()
                print("Error occurred while updating guess:", str(e))
                traceback.print_exc()
                return jsonify({"message": "Internal Server Error", "error": str(e)}), 500

        @token_required()
        def delete(self):
            """Delete a guess"""
            try:
                current_user = g.current_user
                data = request.get_json()

                if not data or "id" not in data:
                    return jsonify({"message": "Missing required fields", "error": "Bad Request"}), 400

                guess = Guess.query.get(data["id"])
                if not guess:
                    return jsonify({"message": "Guess not found", "error": "Not Found"}), 404

                if guess.created_by != current_user.id:
                    return jsonify({"message": "Unauthorized to delete this guess", "error": "Forbidden"}), 403

                db.session.delete(guess)
                db.session.commit()  # Commit delete

                return jsonify({"message": "Guess deleted successfully"}), 200

            except Exception as e:
                db.session.rollback()
                print("Error occurred while deleting guess:", str(e))
                traceback.print_exc()
                return jsonify({"message": "Internal Server Error", "error": str(e)}), 500

    # Register API endpoints
    api.add_resource(_CRUD, '/guess')