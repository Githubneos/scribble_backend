from sqlalchemy.exc import IntegrityError
from __init__ import app, db
from datetime import datetime
from model.competition import Time

class LeaderboardEntry(db.Model):
    """LeaderboardEntry Model for storing drawing scores"""
    __tablename__ = 'leaderboard'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_name = db.Column(db.String(255), nullable=False)
    drawing_name = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)  # Add is_deleted column
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_modified = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

    def __init__(self, profile_name, drawing_name, score, created_by, is_deleted=False):
        self.profile_name = profile_name
        self.drawing_name = drawing_name
        self.score = self._validate_score(score)
        self.created_by = created_by
        self.is_deleted = is_deleted

    def _validate_score(self, score):
        """Validate score is between 0 and 1000"""
        try:
            score = int(score)
            if not (0 <= score <= 1000):
                raise ValueError("Score must be between 0 and 1000")
            return score
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid score: {str(e)}")

    def calculate_score(self, timer_duration, time_taken):
        """Calculate score based on competition performance"""
        try:
            return int((timer_duration / time_taken) * 100)
        except ZeroDivisionError:
            raise ValueError("Time taken cannot be zero")
        except Exception as e:
            raise ValueError(f"Score calculation error: {str(e)}")

    @classmethod
    def get_grouped_rankings(cls):
        """Get rankings grouped by drawing name"""
        try:
            # Get unique drawings from competition
            drawings = Time.query.with_entities(Time.drawn_word).distinct().all()
            result = {}
            
            for drawing in drawings:
                entries = cls.query.filter_by(
                    drawing_name=drawing[0]
                ).order_by(
                    cls.score.desc()
                ).all()
                result[drawing[0]] = [entry.read() for entry in entries]
            
            return result
        except Exception as e:
            print(f"Error getting rankings: {str(e)}")
            return {}

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
            "is_deleted": self.is_deleted,
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
        try:
            for entry_data in data:
                _ = entry_data.pop('id', None)
                profile_name = entry_data.get("profile_name", None)
                drawing_name = entry_data.get("drawing_name", None)
                
                # Try to find matching competition entry
                competition_entry = Time.query.filter_by(
                    users_name=profile_name,
                    drawn_word=drawing_name
                ).first()
                
                if competition_entry:
                    # Calculate score from competition data
                    score = int((competition_entry.timer_duration / competition_entry.time_taken) * 100)
                    entry_data['score'] = max(score, entry_data.get('score', 0))
                
                entry = LeaderboardEntry.query.filter_by(
                    profile_name=profile_name,
                    drawing_name=drawing_name
                ).first()
                
                if entry:
                    if entry_data.get('score', 0) > entry.score:
                        for key, value in entry_data.items():
                            setattr(entry, key, value)
                        entry.update()
                else:
                    entry = LeaderboardEntry(**entry_data)
                    entry.create()
                
                entries[f"{profile_name}_{drawing_name}"] = entry
            
            return entries
        except Exception as e:
            print(f"Error in restore method: {str(e)}")
            return {}

def initLeaderboardTable():
    """Initialize the leaderboard table"""
    with app.app_context():
        # Drop existing table if it exists
        LeaderboardEntry.__table__.drop(db.engine, checkfirst=True)
        # Create new table with updated schema
        db.create_all()
        print("Leaderboard table initialized with is_deleted column")
