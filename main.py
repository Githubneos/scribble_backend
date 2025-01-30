# imports from flask
import base64
import json
import os
import sqlite3
from urllib.parse import urljoin, urlparse
from flask import abort, redirect, render_template, request, send_from_directory, url_for, jsonify  # import render_template from "public" flask libraries
from flask_login import current_user, login_user, logout_user
from flask.cli import AppGroup
from flask_login import current_user, login_required
from flask import current_app
from werkzeug.security import generate_password_hash
import shutil
from flask import Flask, request, jsonify, render_template
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_cors import CORS
from api.leaderboard_api import add_leaderboard_entry, get_leaderboard  # Import the functions
from flask import g


# import "objects" from "this" project
from __init__ import app, db, login_manager  # Key Flask objects
# API endpoints
from api.stats import stats_api
from api.user import user_api 
from api.pfp import pfp_api
from api.nestImg import nestImg_api # Justin added this, custom format for his website
from api.post import post_api
from api.channel import channel_api
from api.group import group_api
from api.section import section_api
from api.nestPost import nestPost_api # Justin added this, custom format for his website
from api.messages_api import messages_api # Adi added this, messages for his website
from api.carphoto import car_api
from api.carChat import car_chat_api
from api.vote import vote_api
from api.guess import guess_api
from api.leaderboard_api import leaderboard_api
from api.competition import competitors_api
from api.drawingapi import drawing_api  # Import the drawing API blueprint

# database Initialization functions
from model.leaderboard import LeaderboardEntry
from model.statistics_hiroshi import Stats, initStatsDataTable
from model.carChat import CarChat
from model.user import User, initUsers
from model.section import Section, initSections
from model.group import Group, initGroups
from model.channel import Channel, initChannels
from model.post import Post, initPosts
from model.nestPost import NestPost, initNestPosts # Justin added this, custom format for his website
from model.vote import Vote, initVotes
from model.guess import db, Guess, initGuessDataTable
from model.leaderboard import LeaderboardEntry, initLeaderboardTable
from model.leaderboard import  initLeaderboardTable  # Import the LeaderboardEntry model and init function
# server only Views

# Add after app creation
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# register URIs for api endpoints
app.register_blueprint(messages_api) # Adi added this, messages for his website
app.register_blueprint(user_api)
app.register_blueprint(pfp_api)
app.register_blueprint(post_api)
app.register_blueprint(channel_api)
app.register_blueprint(group_api)
app.register_blueprint(section_api)
app.register_blueprint(car_chat_api)
app.register_blueprint(guess_api)
app.register_blueprint(leaderboard_api)
app.register_blueprint(competitors_api)
app.register_blueprint(stats_api)
# Added new files to create nestPosts, uses a different format than Mortensen and didn't want to touch his junk
app.register_blueprint(nestPost_api)
app.register_blueprint(nestImg_api)
app.register_blueprint(vote_api)
app.register_blueprint(car_api)
app.register_blueprint(drawing_api)  # Register the drawing API blueprint


# Tell Flask-Login the view function name of your login route
login_manager.login_view = "login"


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login', next=request.path))


# register URIs for server pages
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.context_processor
def inject_user():
    return dict(current_user=current_user)


# Helper function to check if the URL is safe for redirects
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    next_page = request.args.get('next', '') or request.form.get('next', '')
    if request.method == 'POST':
        user = User.query.filter_by(_uid=request.form['username']).first()
        if user and user.is_password(request.form['password']):
            login_user(user)
            if not is_safe_url(next_page):
                return abort(400)
            return redirect(next_page or url_for('index'))
        else:
            error = 'Invalid username or password.'
    return render_template("login.html", error=error, next=next_page)
   
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.errorhandler(404)  # catch for URL not found
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@app.route('/')  # connects default URL to index() function
def index():
    print("Home:", current_user)
    return render_template("index.html")


@app.route('/users/table')
@login_required
def utable():
    users = User.query.all()
    return render_template("utable.html", user_data=users)


@app.route('/users/table2')
@login_required
def u2table():
    users = User.query.all()
    return render_template("u2table.html", user_data=users)


# Helper function to extract uploads for a user (ie PFP image)
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
 
@app.route('/users/delete/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.delete()
        return jsonify({'message': 'User deleted successfully'}), 200
    return jsonify({'error': 'User not found'}), 404


@app.route('/users/reset_password/<int:user_id>', methods=['POST'])
@login_required
def reset_password(user_id):
    if current_user.role != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 403
   
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404


    # Set the new password
    if user.update({"password": app.config['DEFAULT_PASSWORD']}):
        return jsonify({'message': 'Password reset successfully'}), 200
    return jsonify({'error': 'Password reset failed'}), 500


# Create an AppGroup for custom commands
custom_cli = AppGroup('custom', help='Custom commands')


# Define a command to run the data generation functions
@custom_cli.command('generate_data')
def generate_data():
    initUsers()
    initSections()
    initGroups()
    initChannels()
    initPosts()
    initNestPosts()
    initVotes()
    initLeaderboardTable()  # Add this line
   
# Backup the old database
def backup_database(db_uri, backup_uri):
    """Backup the current database."""
    if backup_uri:
        db_path = db_uri.replace('sqlite:///', 'instance/')
        backup_path = backup_uri.replace('sqlite:///', 'instance/')
        shutil.copyfile(db_path, backup_path)
        print(f"Database backed up to {backup_path}")
    else:
        print("Backup not supported for production database.")


# Extract data from the existing database
def extract_data():
    data = {}
    with app.app_context():
        data['users'] = [user.read() for user in User.query.all()]
        data['sections'] = [section.read() for section in Section.query.all()]
        data['groups'] = [group.read() for group in Group.query.all()]
        data['channels'] = [channel.read() for channel in Channel.query.all()]
        data['posts'] = [post.read() for post in Post.query.all()]
    return data


# Save extracted data to JSON files
def save_data_to_json(data, directory='backup'):
    if not os.path.exists(directory):
        os.makedirs(directory)
    for table, records in data.items():
        with open(os.path.join(directory, f'{table}.json'), 'w') as f:
            json.dump(records, f)
    print(f"Data backed up to {directory} directory.")


# Load data from JSON files
def load_data_from_json(directory='backup'):
    data = {}
    for table in ['users', 'sections', 'groups', 'channels', 'posts']:
        with open(os.path.join(directory, f'{table}.json'), 'r') as f:
            data[table] = json.load(f)
    return data


# Restore data to the new database
def restore_data(data):
    with app.app_context():
        users = User.restore(data['users'])
        _ = Section.restore(data['sections'])
        _ = Group.restore(data['groups'], users)
        _ = Channel.restore(data['channels'])
        _ = Post.restore(data['posts'])
    print("Data restored to the new database.")


# Define a command to backup data
@custom_cli.command('backup_data')
def backup_data():
    data = extract_data()
    save_data_to_json(data)
    backup_database(app.config['SQLALCHEMY_DATABASE_URI'], app.config['SQLALCHEMY_BACKUP_URI'])


# Define a command to restore data
@custom_cli.command('restore_data')
def restore_data_command():
    data = load_data_from_json()
    restore_data(data)
   
# Register the custom command group with the Flask application
app.cli.add_command(custom_cli)


# In-memory storage for chat logs and user stats
chat_logs = []
user_stats = {}


def validate_request_data(data, required_keys):
    """
    Validate that the request data contains all required keys.
    :param data: The incoming JSON data
    :param required_keys: A set of keys that must be present in the data
    :return: (bool, str) indicating if validation passed and an error message if not
    """
    if not isinstance(data, dict):
        return False, "Request data must be a JSON object."
    missing_keys = required_keys - data.keys()
    if missing_keys:
        return False, f"Missing required keys: {', '.join(missing_keys)}"
    return True, ""



@app.route('/api/submit_guess', methods=['POST'])
def save_guess_simple():
    try:
        # Parse JSON input
        data = request.json
        if not data:
            return jsonify({"error": "Invalid or missing JSON payload."}), 400

        print("Incoming request data:", data)  # Debugging

        required_keys = {'user', 'guess', 'is_correct'}
        is_valid, error_message = validate_request_data(data, required_keys)

        # Validate input data
        if not is_valid:
            print("Validation failed:", error_message)  # Debugging
            return jsonify({"error": error_message}), 400

        # Extract values from the request
        user = data['user']
        guess = data['guess']
        is_correct = data['is_correct']

        # Ensure the types of the inputs are correct
        if not isinstance(user, str) or not isinstance(guess, str) or not isinstance(is_correct, bool):
            return jsonify({"error": "Invalid data types for user, guess, or is_correct."}), 400

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

        # Append new guess to global chat logs
        chat_logs.append({
            "user": user,
            "guess": guess,
            "is_correct": is_correct
        })

        # Append new guess to the database
        try:
            # Initialize the database table
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
            db.session.rollback()  # Roll back the transaction on failure
            return jsonify({"error": "Failed to save guess to database."}), 500

        # Prepare the response
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
        # Return success response with stats and latest guess
        return jsonify(response_data), 201

    except Exception as e:
        # Log unexpected exceptions and provide detailed debugging information
        print("General Exception:", str(e))
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/api/guesses', methods=['GET'])
def get_all_guesses():
    try:
        # Retrieve all guesses from the database
        guesses = Guess.query.all()

        # Prepare the response (removed id and timestamp)
        guesses_data = []
        for guess in guesses:
            guesses_data.append({
                "user": guess.guesser_name,
                "guess": guess.guess,
                "is_correct": guess.is_correct
                # Removed "id" and "timestamp" fields from the response
            })

        return jsonify(guesses_data), 200

    except Exception as e:
        print("General Exception:", str(e))
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500



@app.route('/api/guesses', methods=['PUT'])
def update_guess():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid or missing JSON payload."}), 400
        
        # Log the received data to make sure the frontend is sending it correctly
        print("Received data:", data)

        required_keys = ['user', 'guess', 'is_correct']
        is_valid, error_message = validate_request_data(data, required_keys)

        if not is_valid:
            return jsonify({"error": error_message}), 400

        user = data['user']
        new_guess = data['guess']
        is_correct = data['is_correct']

        # Find the existing guess in the database using the combination of user and guess
        guess = Guess.query.filter_by(guesser_name=user, guess=new_guess).first()
        if not guess:
            return jsonify({"error": "Guess not found."}), 404

        # Update the guess
        guess.is_correct = is_correct
        db.session.commit()  # Save changes to the database

        response_data = {
            "user": guess.guesser_name,
            "guess": guess.guess,
            "is_correct": guess.is_correct
        }

        return jsonify(response_data), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500




@app.route('/api/guesses', methods=['DELETE'])
def delete_guess():
    try:
        # Parse JSON input
        data = request.json
        if not data:
            return jsonify({"error": "Invalid or missing JSON payload."}), 400

        if 'user' not in data or 'guess' not in data:
            return jsonify({"error": "Missing user or guess."}), 400

        user = data['user']
        guess_value = data['guess']

        # Debugging log to check the data received
        print(f"Received DELETE request for guess: {user} - {guess_value}")

        # Find the guess in the database using user and guess
        guess = Guess.query.filter_by(guesser_name=user, guess=guess_value).first()
        if not guess:
            print(f"Guess not found for: {user} - {guess_value}")
            return jsonify({"error": "Guess not found."}), 404

        # Debugging log to confirm guess deletion
        print(f"Deleting guess: {user} - {guess_value}")

        # Delete the guess from the database
        db.session.delete(guess)
        db.session.commit()  # Commit the deletion to the database

        # Return success message with 200 status code
        return jsonify({"message": f"Guess by {user} deleted successfully."}), 200

    except Exception as e:
        # Log unexpected exceptions
        print("General Exception:", str(e))
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500




@app.route('/api/leaderboard', methods=['GET'])
def leaderboard_get():
    try:
        entries = LeaderboardEntry.query.order_by(LeaderboardEntry.score.desc()).all()
        leaderboard_data = [{
            "profile_name": entry.profile_name,
            "drawing_name": entry.drawing_name,
            "score": entry.score
        } for entry in entries]
        return jsonify(leaderboard_data), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch leaderboard: {str(e)}"}), 500

@app.route('/api/leaderboard', methods=['POST'])
def leaderboard_post():
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'score' not in data:
            return jsonify({"error": "Missing required fields"}), 400
        
        name_parts = data['name'].split(' - ', 1)
        profile_name = name_parts[0]
        drawing_name = name_parts[1] if len(name_parts) > 1 else "Untitled"
        score = int(data['score'])
        
        # Check for existing entry and update if new score is higher
        existing_entry = LeaderboardEntry.query.filter_by(
            profile_name=profile_name,
            drawing_name=drawing_name
        ).first()
        
        if existing_entry:
            if score > existing_entry.score:
                existing_entry.score = score
                db.session.commit()
                return jsonify({"message": "Score updated successfully"}), 200
            return jsonify({"message": "Existing score is higher"}), 200
            
        # Create new entry if none exists
        entry = LeaderboardEntry(
            profile_name=profile_name,
            drawing_name=drawing_name,
            score=score
        )
        db.session.add(entry)
        db.session.commit()
        
        return jsonify({"message": "Entry added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to add/update entry: {str(e)}"}), 500


# Add near the bottom of file, before if __name__ == "__main__":
import sys

# Add near the bottom of file, before if __name__ == "__main__":
from model.competition import Time

@app.route('/api/times', methods=['GET'])
def get_times():
    times = Time.query.all()
    times_list = [time.read() for time in times]
    return jsonify(times_list), 200

@app.route('/api/times', methods=['POST'])
def add_time():
    data = request.json
    users_name = data.get('users_name')
    timer = data.get('timer')
    amount_drawn = data.get('amount_drawn')

    if not users_name or not timer or not amount_drawn:
        return jsonify({"error": "Missing data"}), 400

    new_time = Time(users_name=users_name, timer=timer, amount_drawn=amount_drawn)
    db.session.add(new_time)
    db.session.commit()

    return jsonify({"message": "Time entry added successfully"}), 201

def init_db():
    with app.app_context():
        db.create_all()
        if not Time.query.first():
            initial_times = [
                Time(users_name="Alice", timer="10:00", amount_drawn=5),
                Time(users_name="Bob", timer="15:00", amount_drawn=3),
                Time(users_name="Charlie", timer="20:00", amount_drawn=7)
            ]
            for time_entry in initial_times:
                db.session.add(time_entry)
            db.session.commit()

@app.route('/api/statistics', methods=['POST'])
def update_statistics():
    try:
        data = request.get_json()
        if not data or 'user_name' not in data:
            return jsonify({"error": "Missing user_name field"}), 400

        # Find existing stats or create new
        stats = Stats.query.filter_by(user_name=data['user_name']).first()
        if not stats:
            stats = Stats(user_name=data['user_name'])
            db.session.add(stats)
        
        # Update stats if correct/wrong provided
        if 'correct' in data:
            stats.update(correct_increment=data['correct'])
        if 'wrong' in data:
            stats.update(wrong_increment=data['wrong'])
            
        db.session.commit()
        
        return jsonify({
            "message": "Statistics updated successfully",
            "stats": stats.read()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update statistics: {str(e)}"}), 500


# Add initialization at app startup
_is_initialized = False

@app.before_request
def initialize_tables():
    global _is_initialized
    if not _is_initialized:
        try:
            with app.app_context():
                initStatsDataTable()
                initLeaderboardTable()  # Add this
                db.create_all()
                _is_initialized = True
        except Exception as e:
            app.logger.error(f"Error initializing: {str(e)}")
            return jsonify({"error": "Init failed"}), 500
        
@app.route('/api/save-drawing', methods=['POST'])
def save_drawing():
    try:
        # Debugging: Log the incoming request
        print("Incoming request data:", request.json)

        # Parse JSON input
        data = request.get_json()  # Use get_json() to parse JSON input
        if not data:
            print("No JSON data received")
            return jsonify({"error": "Invalid or missing JSON payload."}), 400

        # Log the received data for debugging
        print("Received data:", data)

        # Check if the required keys are present
        if 'drawing' not in data:
            print("Missing key: drawing")
            return jsonify({"error": "Missing key: drawing"}), 400

        # Extract values from the request
        drawing_data = data['drawing']
        user_name = data.get('user_name', 'default_user')  # Use default value if not provided
        drawing_name = data.get('drawing_name', 'default_drawing')  # Use default value if not provided
        timestamp = datetime.now().isoformat()

        # Ensure the drawings directory exists
        if not os.path.exists('drawings'):
            os.makedirs('drawings')

        # Decode and save the drawing
        try:
            base64_data = drawing_data.split(',')[1]
            file_path = f"drawings/{user_name}_{drawing_name}_{timestamp}.jpeg".replace(':', '-')
            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(base64_data))
            print(f"Drawing saved to {file_path}")
        except IndexError:
            print("Error: Drawing data is not in the expected format")
            return jsonify({"error": "Drawing data is not in the expected format"}), 400
        except Exception as e:
            print(f"Error decoding drawing data: {e}")
            return jsonify({"error": f"Error decoding drawing data: {e}"}), 400

        # Save metadata to the database
        try:
            database_path = current_app.config.get('DATABASE', 'instance/database.db')
            with sqlite3.connect(database_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS drawings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_name TEXT NOT NULL,
                        drawing_name TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        timestamp TEXT NOT NULL
                    )
                ''')
                cursor.execute('''
                    INSERT INTO drawings (user_name, drawing_name, file_path, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (user_name, drawing_name, file_path, timestamp))
                conn.commit()
            print("Drawing metadata saved to database")
        except Exception as e:
            print(f"Error saving metadata to database: {e}")
            return jsonify({"error": f"Error saving metadata to database: {e}"}), 500

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
        
# this runs the flask application on the development server
if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port="8887")
