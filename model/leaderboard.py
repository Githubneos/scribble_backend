from sqlalchemy.exc import IntegrityError
from __init__ import app, db

# Database Model Class for managing leaderboard entries in the drawing game
# Uses SQLAlchemy ORM to map Python objects to database tables
class LeaderboardEntry(db.Model):
    """LeaderboardEntry Model for storing drawing scores"""
    __tablename__ = 'leaderboard'

    # Database columns definition
    # Each entry has unique ID, player name, drawing name and score
    id = db.Column(db.Integer, primary_key=True)
    profile_name = db.Column(db.String(255), nullable=False)  # Player's username
    drawing_name = db.Column(db.String(255), nullable=False)  # Name of the drawing
    score = db.Column(db.Integer, nullable=False)            # Score achieved

    # Constructor to initialize a new leaderboard entry
    def __init__(self, profile_name, drawing_name, score):
        self.profile_name = profile_name
        self.drawing_name = drawing_name
        self.score = score

    # CREATE operation
    # Adds new entry to database and handles potential integrity errors
    def create(self):
        """Add new leaderboard entry"""
        try:
            db.session.add(self)  # Add entry to database session
            db.session.commit()   # Commit changes to database
            return True
        except IntegrityError:    # Handle database constraints violations
            db.session.rollback() # Rollback on error
            return False

    # READ operation
    # Converts database entry to dictionary format for API responses
    def read(self):
        """Return entry as dictionary"""
        return {
            "profile_name": self.profile_name,
            "drawing_name": self.drawing_name,
            "score": self.score
        }

    # UPDATE operation
    # Updates entry fields with new data
    def update(self, data):
        """Update entry fields"""
        for key, value in data.items():
            setattr(self, key, value)  # Dynamically set attributes
        db.session.commit()
        return self

    # DELETE operation
    # Removes entry from database
    def delete(self):
        """Remove entry"""
        db.session.delete(self)
        db.session.commit()
        return True

    @classmethod
    def list_all(cls):
        """Return all entries as a list of dictionaries"""
        entries = cls.query.all()
        return [{
            "profile_name": entry.profile_name,
            "drawing_name": entry.drawing_name, 
            "score": entry.score
        } for entry in entries]

# Database initialization function
def initLeaderboardTable():
    """Initialize table"""
    with app.app_context():
        db.create_all()  # Create database tables
        print("Leaderboard table initialized.")
