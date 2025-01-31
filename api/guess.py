import base64
import sqlite3
from flask import Flask, g, request, jsonify, render_template
from datetime import datetime
from datetime import datetime
from flask_restful import Api, Resource
from flask import Blueprint, request, jsonify, current_app
from __init__ import app, db
from api.jwt_authorize import token_required
from model.guess import Guess, initGuessDataTable

app = Flask(__name__)
guess_api = Blueprint('guess_api', __name__)



# In-memory storage for chat logs and user stats
chat_logs = []
user_stats = {}

# Utility function to validate input data
def validate_request_data(data, required_keys):
    """Validates that the data contains all required keys."""
    if not data:
        return False, "Request data is missing."
    missing_keys = required_keys - data.keys()
    if missing_keys:
        return False, f"Missing required keys: {', '.join(missing_keys)}"
    return True, None

# Serve the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to get all chat logs
@app.route('/api/guesses', methods=['GET'])
def get_guesses():
    print("GET /api/guesses route was hit")  # Debugging line
    return jsonify(chat_logs), 200

# API endpoint to add a guess and update user stats
@app.route('/api/submit_guess', methods=['POST'])
def save_guess():
    try:
        # Debugging: Log the incoming request
        print("Incoming request data:", request.json)

        # Parse JSON input
        data = request.json  # Expecting JSON input
        required_keys = {'user', 'guess', 'is_correct'}

        # Validate input data
        is_valid, error_message = validate_request_data(data, required_keys)
        if not is_valid:
            print("Validation failed:", error_message)  # Debugging
            return jsonify({"error": error_message}), 400

        # Extract values from the request
        user = data['user']
        guess = data['guess']
        is_correct = data['is_correct']
        timestamp = datetime.now().isoformat()

        # Initialize stats for the user if not present
        if user not in user_stats:
            user_stats[user] = {
                "correct": 0,
                "wrong": 0,
                "total_guesses": 0,
                "guesses": []
            }

        # Update user stats
        user_stats[user]["total_guesses"] += 1
        if is_correct:
            user_stats[user]["correct"] += 1
        else:
            user_stats[user]["wrong"] += 1

        # Append guess details to the user's history
        user_stats[user]["guesses"].append({
            "guess": guess,
            "is_correct": is_correct,
            "timestamp": timestamp
        })

        # Append new guess to global chat logs
        chat_logs.append({
            "user": user,
            "guess": guess,
            "is_correct": is_correct,
            "timestamp": timestamp
        })
        

        #db.session.add(guess)

        # Return success response
        return jsonify({"status": "Guess and stats updated successfully."}), 201

    except KeyError as e:
        print("KeyError:", str(e))  # Log and handle missing keys
        return jsonify({"error": f"Missing key: {str(e)}"}), 400
    except TypeError as e:
        print("TypeError:", str(e))  # Log and handle type errors
        return jsonify({"error": f"Type error: {str(e)}"}), 400
    except Exception as e:
        # Log unexpected exceptions and provide better debugging info
        print("General Exception:", str(e))
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# API endpoint to retrieve stats for a specific user
@app.route('/api/user_stats/<string:username>', methods=['GET'])
def get_user_stats(username):
    try:
        user_stat = user_stats.get(username)

        if not user_stat:
            return jsonify({"error": f"No stats found for user '{username}'."}), 404

        return jsonify(user_stat), 202
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/api/save-drawing', methods=['POST'])
def save_drawing():
    try:
        # Debugging: Log the incoming request
        print("Incoming request data:", request.json)

        # Parse JSON input
        data = request.json  # Expecting JSON input
        required_keys = {'user_name', 'drawing_name', 'drawing'}

        # Validate input data
        missing_keys = required_keys - data.keys()
        if missing_keys:
            error_message = f"Missing keys: {', '.join(missing_keys)}"
            print("Validation failed:", error_message)  # Debugging
            return jsonify({"error": error_message}), 400

        # Extract values from the request
        user_name = data['user_name']
        drawing_name = data['drawing_name']
        drawing_data = data['drawing']
        timestamp = datetime.now().isoformat()

        # Decode and save the drawing
        file_path = f"drawings/{user_name}_{drawing_name}_{timestamp}.jpeg".replace(':', '-')
        with open(file_path, 'wb') as f:
            f.write(base64.b64decode(drawing_data.split(',')[1]))

        # Save metadata to the database
        with sqlite3.connect(sqlite3.DatabaseError) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO drawings (user_name, drawing_name, file_path, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (user_name, drawing_name, file_path, timestamp))
            conn.commit()

        # Return success response
        return jsonify({"status": "Drawing saved successfully.", "file_path": file_path}), 201

    except KeyError as e:
        print("KeyError:", str(e))  # Log and handle missing keys
        return jsonify({"error": f"Missing key: {str(e)}"}), 400
    except TypeError as e:
        print("TypeError:", str(e))  # Log and handle type errors
        return jsonify({"error": f"Type error: {str(e)}"}), 400
    except Exception as e:
        # Log unexpected exceptions and provide better debugging info
        print("General Exception:", str(e))
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
    
    
    
    
class _GuessCRUD(Resource):  # Guess Game API operations for Create, Read, Update, Delete
    def post(self):  # Create method for submitting a guess
        """
        Create a new guess.

        Reads data from the JSON body of the request, validates the input, and creates a new guess in the game database.

        Returns:
            JSON response with the guess details or an error message.
        """

        # Read data from JSON body
        body = request.get_json()

        ''' Avoid garbage in, error checking '''
        # Validate user and guess details
        user = body.get('user')
        guess = body.get('guess')
        is_correct = body.get('is_correct')
        if not user or len(user) < 2:
            return {'message': 'User name is missing or too short'}, 400
        if not guess or len(guess) < 1:
            return {'message': 'Guess is missing or too short'}, 400
        if is_correct is None:
            return {'message': 'is_correct field is missing'}, 400

        # Validate the guess correctness (e.g., check against the correct answer)
        if not isinstance(is_correct, bool):
            return {'message': 'is_correct should be a boolean'}, 400

        # Initialize stats for the user if not present
        if user not in user_stats:
            user_stats[user] = {
                "correct": 0,
                "wrong": 0,
                "total_guesses": 0,
                "guesses": []
            }

        # Update user stats
        user_stats[user]["total_guesses"] += 1
        if is_correct:
            user_stats[user]["correct"] += 1
        else:
            user_stats[user]["wrong"] += 1

        # Append guess details to the user's history
        user_stats[user]["guesses"].append({
            "guess": guess,
            "is_correct": is_correct
        })

        # Append new guess to global game logs
        chat_logs.append({
            "user": user,
            "guess": guess,
            "is_correct": is_correct
        })

        # Add guess to database
        try:
            # Initialize the database table for guesses if not already done
            initGuessDataTable()

            new_guess = Guess(
                guesser_name=user,
                guess=guess,
                is_correct=is_correct
            )
            db.session.add(new_guess)
            db.session.commit()  # Save to the database
            print("Guess saved to database successfully.")  # Debugging
        except Exception as e:
            print(f"Error saving guess to database: {e}")
            db.session.rollback()  # Rollback on failure
            return jsonify({"error": "Failed to save guess to database."}), 500

        # Prepare the response with the user's updated stats and the latest guess
        response_data = {
            "User": user,
            "Stats": {
                "Correct Guesses": user_stats[user]["correct"],
                "Wrong Guesses": user_stats[user]["wrong"],
                "Total Guesses": user_stats[user]["total_guesses"]
            },
            "Latest Guess": {
                "Guess": guess,
                "Is Correct": is_correct
            }
        }

        # Return success response with updated stats and guess
        return jsonify(response_data), 201

    @token_required()
    def get(self):  # Read method for retrieving all guesses
        """
        Retrieve all guesses for the game.

        Retrieves a list of all guesses made by all users in the game.

        Returns:
            JSON response with a list of guesses.
        """

        # Retrieve the current user from the token_required authentication check
        current_user = g.current_user

        """ Query the database to retrieve all guesses """
        guesses = Guess.query.all()

        # Prepare the response data for each guess
        json_ready = []
        for guess in guesses:
            guess_data = {
                "user": guess.guesser_name,
                "guess": guess.guess,
                "is_correct": guess.is_correct,
                "timestamp": guess.timestamp
            }

            # Include extra information depending on user role (admin can see all guesses)
            if current_user.role == 'Admin' or current_user.id == guess.user_id:
                guess_data['access'] = 'rw'  # Read-write access control
            else:
                guess_data['access'] = 'ro'  # Read-only access control

            json_ready.append(guess_data)

        # Return the list of guesses as a JSON response
        return jsonify(json_ready)

    @token_required()
    def put(self):  # Update method for updating a guess
        """
        Update a user's guess.

        Retrieves the current user from the token_required authentication check and updates the guess.

        Returns:
            JSON response with the updated guess details or an error message.
        """

        # Retrieve the current user from the token_required authentication check
        current_user = g.current_user

        # Read data from the JSON body of the request
        body = request.get_json()
        guess_id = body.get('id')
        new_guess = body.get('guess')
        is_correct = body.get('is_correct')

        if not guess_id or not new_guess or is_correct is None:
            return {'message': 'Missing required fields'}, 400

        # Validate the guess correctness
        if not isinstance(is_correct, bool):
            return {'message': 'is_correct must be a boolean'}, 400

        # Find the guess in the database
        guess = Guess.query.filter_by(id=guess_id).first()

        if not guess:
            return {'message': 'Guess not found'}, 404

        # Ensure that only the user who made the guess can update it (or admins)
        if current_user.id != guess.user_id and current_user.role != 'Admin':
            return {'message': 'Not authorized to update this guess'}, 403

        # Update the guess in the database
        guess.guess = new_guess
        guess.is_correct = is_correct
        db.session.commit()

        # Prepare the response with updated guess data
        response_data = {
            "User": guess.guesser_name,
            "Updated Guess": new_guess,
            "Is Correct": is_correct
        }

        return jsonify(response_data)

    @token_required("Admin")
    def delete(self):  # Delete method for removing a guess
        """
        Delete a guess from the database.

        Only accessible by admin users.

        Returns:
            JSON response with a success message or an error message.
        """

        body = request.get_json()
        guess_id = body.get('id')

        # Find the guess in the database
        guess = Guess.query.filter_by(id=guess_id).first()

        if not guess:
            return {'message': 'Guess not found'}, 404

        # Delete the guess from the database
        db.session.delete(guess)
        db.session.commit()

        return jsonify({"message": f"Deleted guess with ID {guess_id}"}), 204


# Run the app on localhost with port 8887
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8887)
