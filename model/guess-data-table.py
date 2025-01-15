from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///guesses.db'  # Update to your database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database models
class ChatLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(255), nullable=False)
    guess = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class UserStat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(255), unique=True, nullable=False)
    correct = db.Column(db.Integer, default=0)
    wrong = db.Column(db.Integer, default=0)
    total_guesses = db.Column(db.Integer, default=0)

def init_db():
    with app.app_context():
        db.create_all()

# Serve the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to get all chat logs
@app.route('/api/guesses', methods=['GET'])
def get_guesses():
    guesses = ChatLog.query.all()
    return jsonify([{
        'user': g.user,
        'guess': g.guess,
        'is_correct': g.is_correct,
        'timestamp': g.timestamp.isoformat()
    } for g in guesses]), 200

# API endpoint to add a guess and update user stats
@app.route('/api/submit_guess', methods=['POST'])
def save_guess():
    data = request.json
    required_keys = {'user', 'guess', 'is_correct'}

    if not data or not required_keys.issubset(data.keys()):
        return jsonify({"error": "Missing required keys."}), 400

    user = data['user']
    guess = data['guess']
    is_correct = data['is_correct']

    try:
        # Update chat log
        new_log = ChatLog(user=user, guess=guess, is_correct=is_correct)
        db.session.add(new_log)

        # Update or create user stats
        user_stat = UserStat.query.filter_by(user=user).first()
        if not user_stat:
            user_stat = UserStat(user=user)
            db.session.add(user_stat)

        user_stat.total_guesses += 1
        if is_correct:
            user_stat.correct += 1
        else:
            user_stat.wrong += 1

        db.session.commit()
        return jsonify({"status": "Guess and stats updated successfully."}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# API endpoint to retrieve stats for a specific user
@app.route('/api/user_stats/<string:username>', methods=['GET'])
def get_user_stats(username):
    user_stat = UserStat.query.filter_by(user=username).first()
    if not user_stat:
        return jsonify({"error": f"No stats found for user '{username}'."}), 404

    return jsonify({
        "user": user_stat.user,
        "correct": user_stat.correct,
        "wrong": user_stat.wrong,
        "total_guesses": user_stat.total_guesses
    }), 200

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=8887)
