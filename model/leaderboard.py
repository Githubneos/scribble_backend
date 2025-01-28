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
        except IntegrityError:    # Handle database constraints violations
            db.session.rollback() # Rollback on error
            return None
        return self

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

    @classmethod
    def update_score(cls, profile_name, drawing_name, new_score):
        """Update score regardless of value"""
        entry = cls.query.filter_by(
            profile_name=profile_name,
            drawing_name=drawing_name
        ).first()
        
        if entry:
            entry.score = new_score  # Always update score
            db.session.commit()
            return True
        return False

# Database initialization function
# Creates table and populates with sample data if empty
def initLeaderboardTable():
    """Initialize table with sample data"""
    with app.app_context():
        db.create_all()  # Create database tables
        # Check if table is empty and add sample data
        if not LeaderboardEntry.query.first():
            samples = [
                LeaderboardEntry("ArtMaster", "Sunset Beach", 95),
                LeaderboardEntry("PixelPro", "Mountain Valley", 88)
            ]
            for entry in samples:
                entry.create()
        print("Leaderboard table initialized.")
