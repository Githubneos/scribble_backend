from sqlalchemy.exc import IntegrityError
from __init__ import app, db
from datetime import datetime

class LeaderboardEntry(db.Model):
    """LeaderboardEntry Model for storing drawing scores with JWT authentication"""
    __tablename__ = 'leaderboard'
    
    # Define columns with better constraints
    id = db.Column(db.Integer, primary_key=True)
    profile_name = db.Column(db.String(255), nullable=False)
    drawing_name = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_modified = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

    def __init__(self, profile_name, drawing_name, score, created_by):
        self.profile_name = profile_name
        self.drawing_name = drawing_name
        self.score = self._validate_score(score)
        self.created_by = created_by

    def _validate_score(self, score):
        """Validate score is within acceptable range"""
        try:
            score = int(score)
            if not (0 <= score <= 100):
                raise ValueError("Score must be between 0 and 100")
            return score
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid score: {str(e)}")

    def __repr__(self):
        return f"LeaderboardEntry(id={self.id}, profile_name={self.profile_name}, score={self.score})"

    def create(self):
        """Create and return a new leaderboard entry"""
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            raise e

    def read(self):
        """Return dictionary of leaderboard entry attributes"""
        return {
            "id": self.id,
            "profile_name": self.profile_name,
            "drawing_name": self.drawing_name,
            "score": self.score,
            "created_by": self.created_by,
            "date_created": self.date_created.strftime("%Y-%m-%d %H:%M:%S"),
            "date_modified": self.date_modified.strftime("%Y-%m-%d %H:%M:%S")
        }

    def update(self):
        try:
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            raise e

    def delete(self):
        """Delete the leaderboard entry"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def find_by_id(cls, entry_id):
        """Find leaderboard entry by ID"""
        return cls.query.filter_by(id=entry_id).first()

    @classmethod
    def find_by_user(cls, user_id):
        """Find all entries by a specific user"""
        return cls.query.filter_by(created_by=user_id).all()

    @staticmethod
    def restore(data):
        entries = {}
        for entry_data in data:
            _ = entry_data.pop('id', None)  # Remove 'id' from entry_data
            profile_name = entry_data.get("profile_name", None)
            drawing_name = entry_data.get("drawing_name", None)
            
            # Look for existing entry by profile and drawing name
            entry = LeaderboardEntry.query.filter_by(
                profile_name=profile_name,
                drawing_name=drawing_name
            ).first()
            
            if entry:
                entry.update(entry_data)
            else:
                entry = LeaderboardEntry(**entry_data)
                entry.create()
            
            entries[f"{profile_name}_{drawing_name}"] = entry
        
        return entries

def initLeaderboardTable():
    """Initialize the leaderboard table"""
    with app.app_context():
        db.create_all()
        print("Leaderboard table initialized.")
