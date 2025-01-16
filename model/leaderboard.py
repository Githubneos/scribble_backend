from sqlalchemy.exc import IntegrityError
from __init__ import app, db


class LeaderboardEntry(db.Model):
    """LeaderboardEntry Model for storing drawing scores"""
    __tablename__ = 'leaderboard'


    id = db.Column(db.Integer, primary_key=True)
    profile_name = db.Column(db.String(255), nullable=False)
    drawing_name = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Integer, nullable=False)


    def __init__(self, profile_name, drawing_name, score):
        self.profile_name = profile_name
        self.drawing_name = drawing_name
        self.score = score


    def create(self):
        """Add new leaderboard entry"""
        try:
            db.session.add(self)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None
        return self


    def read(self):
        """Return entry as dictionary"""
        return {
            "profile_name": self.profile_name,
            "drawing_name": self.drawing_name,
            "score": self.score
        }


    def update(self, data):
        """Update entry fields"""
        for key, value in data.items():
            setattr(self, key, value)
        db.session.commit()
        return self


    def delete(self):
        """Remove entry"""
        db.session.delete(self)
        db.session.commit()


def initLeaderboardTable():
    """Initialize table with sample data"""
    with app.app_context():
        db.create_all()
        # Add sample entries if table is empty
        if not LeaderboardEntry.query.first():
            samples = [
                LeaderboardEntry("ArtMaster", "Sunset Beach", 95),
                LeaderboardEntry("PixelPro", "Mountain Valley", 88)
            ]
            for entry in samples:
                entry.create()
        print("Leaderboard table initialized.")
