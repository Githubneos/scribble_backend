from flask import Blueprint, request, jsonify, g
from flask_restful import Api, Resource
from datetime import datetime
from __init__ import app
from api.jwt_authorize import token_required
import random

guess_api = Blueprint('guess_api', __name__, url_prefix='/api')
api = Api(guess_api)
from flask import Flask, request, jsonify, g
from flask_restful import Resource
from datetime import datetime
from models import WordGuess
from auth import token_required

class GuessAPI:
    """
    API CRUD endpoints for the Guess model.
    All endpoints require JWT authentication.
    """

    class _CRUD(Resource):

        @token_required()
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
                guess = data["user_guess"].strip().lower()  # Fix frontend key name
                correct_word = data["correct_word"].strip().lower()

                is_correct = (guess == correct_word)

                word_guess = WordGuess(
                    guesser_name=current_user.name,
                    guess=guess,
                    is_correct=is_correct,
                    created_by=current_user.id
                )
                word_guess.create()  

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

        @token_required()  # ✅ Add token authentication for GET requests
        def get(self):
            """Fetch all guesses or a specific guess by ID"""
            current_user = g.current_user
            data = request.get_json(silent=True)

            try:
                if data and "id" in data:
                    guess = WordGuess.query.get(data["id"])
                    if not guess:
                        return jsonify({"message": "Guess not found", "error": "Not Found"}), 404
                    return jsonify({"message": "Guess fetched successfully", "guess": guess.read()}), 200

                # ✅ Fetch all guesses created by the user
                guesses = WordGuess.query.filter_by(created_by=current_user.id).all()
                return jsonify({
                    "message": "Guesses fetched successfully",
                    "recent_guesses": [guess.read() for guess in guesses]
                }), 200

            except Exception as e:
                return jsonify({
                    "message": "Failed to fetch guess(es)",
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
                guess = WordGuess.query.get(data["id"])
                if not guess:
                    return jsonify({"message": "Guess not found", "error": "Not Found"}), 404

                if guess.created_by != current_user.id and current_user.role != "Admin":
                    return jsonify({"message": "You are not authorized to update this guess", "error": "Forbidden"}), 403

                updated_guess = data["user_guess"].strip().lower()
                correct_word = data["correct_word"].strip().lower()
                is_correct = (updated_guess == correct_word)

                guess.guess = updated_guess
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
                guess = WordGuess.query.get(data["id"])
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