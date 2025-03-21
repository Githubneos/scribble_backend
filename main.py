# imports from flask
import json
import os
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
from api.leaderboard_api import leaderboard_api  # Keep only one import
from api.competition import competitors_api
from api.picture import picture_api # Add this import if not present
from api.blind_trace import blind_trace_api  # Add this import

# database Initialization functions
from model.leaderboard import LeaderboardEntry, initLeaderboardTable
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
from model.picture import Picture, initPictureTable  # Update this line
from model.competition import Time, initTimerTable  # Add this import
from model.blind_trace import BlindTraceSubmission, initBlindTraceTable # Add this import
# server only Views

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
app.register_blueprint(leaderboard_api)  # Make sure this registration is present
app.register_blueprint(competitors_api)
app.register_blueprint(stats_api)
# Added new files to create nestPosts, uses a different format than Mortensen and didn't want to touch his junk
app.register_blueprint(nestPost_api)
app.register_blueprint(nestImg_api)
app.register_blueprint(vote_api)
app.register_blueprint(car_api)
app.register_blueprint(picture_api)
app.register_blueprint(blind_trace_api)  # Add this line


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

@app.route('/admin/submission')
@login_required
def blind_trace_admin():
    if not current_user.is_authenticated or current_user.role != 'Admin':
        return redirect(url_for('index'))

    blind_trace_data = BlindTraceSubmission.query.all()  # Ensure this model exists
    return render_template('blind_trace_admin.html', blind_trace_data=blind_trace_data)

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
    initLeaderboardTable()
    initStatsDataTable()
    initTimerTable()
    initPictureTable()  # Add this line
    initBlindTraceTable


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
        data['timer_entries'] = [time.read() for time in Time.query.all()]
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
        if 'timer_entries' in data:
            _ = Time.restore(data['timer_entries'])
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


# Add initialization at app startup
_is_initialized = False

@app.before_request
def initialize_tables():
    global _is_initialized
    if not _is_initialized:
        try:
            with app.app_context():
                db.create_all()
                # Make sure Competition table is created before Leaderboard
                initTimerTable()     # Competition table initialization
                initLeaderboardTable()  # Leaderboard table initialization
                initPictureTable()   # Keep this initialization
                initGuessDataTable()
                initStatsDataTable()
                initBlindTraceTable
                _is_initialized = True
        except Exception as e:
            print(f"Error initializing tables: {str(e)}")  # Add better error logging
            app.logger.error(f"Error initializing: {str(e)}")
            return jsonify({"error": "Init failed"}), 500

@app.route('/admin/leaderboard')
@login_required
def leaderboard_admin():
    if not current_user.is_authenticated or current_user.role != 'Admin':
        return redirect(url_for('index'))
        
    leaderboard_data = LeaderboardEntry.query.all()
    return render_template(
        'leaderboard_admin.html', 
        leaderboard_data=leaderboard_data
    )

@app.route('/admin/competition')
@login_required
def competition_admin():
    if not current_user.is_authenticated or current_user.role != 'Admin':
        return redirect(url_for('index'))
        
    competition_data = Time.query.all()
    return render_template(
        'competition_admin.html', 
        competition_data=competition_data
    )

@app.route('/admin/pictures')
@login_required
def picture_admin():
    if not current_user.is_authenticated or current_user.role != 'Admin':
        return redirect(url_for('index'))
        
    picture_data = Picture.query.all()
    return render_template(
        'picture_admin.html', 
        picture_data=picture_data
    )

@app.route('/admin/submission')
@login_required
def manage_blind_trace():
    if not current_user.is_authenticated or current_user.role != 'Admin':
        return redirect(url_for('index'))

    # Fetch all non-deleted Blind Trace submissions
    blind_trace_data = BlindTraceSubmission.query.filter_by(is_deleted=False).all()
    
    return render_template(
        'blind_trace_admin.html',
        blind_trace_data=blind_trace_data
    )



# this runs the flask application on the development server
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="8203")
