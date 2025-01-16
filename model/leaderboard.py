from sqlalchemy.exc import IntegrityError
from __init__ import app, db
from model.user import User  # Assuming you have a User model

class LeaderboardEntry(db.Model):
    """
    LeaderboardEntry Model

    Attributes:
        id (int): Primary key for the leaderboard entry.
        profile_name (str): Name of the user profile.
        drawing_name (str): Name of the drawing.
        score (int): Score for the drawing.
        user_id (int): ID of the user who owns this leaderboard entry.
    """
    __tablename__ = 'leaderboard'

    id = db.Column(db.Integer, primary_key=True)
    profile_name = db.Column(db.String(255), nullable=False)
    drawing_name = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key to User

    def __init__(self, profile_name, drawing_name, score, user_id):
        self.profile_name = profile_name
        self.drawing_name = drawing_name
        self.score = score
        self.user_id = user_id

    def create(self):
        """Add a new leaderboard entry to the database."""
        try:
            db.session.add(self)
            db.session.commit()
            print(f"Leaderboard Entry Added: {self.profile_name} - {self.drawing_name} - Score: {self.score}")
        except IntegrityError:
            db.session.rollback()
            return None
        return self

    def read(self):
        """Return the leaderboard entry data in dictionary format."""
        return {
            "id": self.id,
            "profile_name": self.profile_name,
            "drawing_name": self.drawing_name,
            "score": self.score,
            "user_id": self.user_id
        }

    def update(self, data):
        """Update the leaderboard entry."""
        for key, value in data.items():
            if key == "profile_name":
                self.profile_name = value
            if key == "drawing_name":
                self.drawing_name = value
            if key == "score":
                self.score = value
        db.session.commit()
        return self

    def delete(self):
        """Delete this leaderboard entry from the database."""
        db.session.delete(self)
        db.session.commit()

def initLeaderboardTable():
    """Initialize the leaderboard table by creating the database table."""
    with app.app_context():
        db.create_all()  # This will create all tables
        print("Leaderboard table initialized.")