from sqlalchemy.exc import IntegrityError
from __init__ import app, db
from typing import Optional, Dict, Any

class Stats(db.Model):
    """Stats Model for storing user game statistics"""
    __tablename__ = 'stats_data_table'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255), nullable=False, unique=True)
    correct_guesses = db.Column(db.Integer, nullable=False, default=0)
    wrong_guesses = db.Column(db.Integer, nullable=False, default=0)
    total_rounds = db.Column(db.Integer, nullable=False, default=0)
    created_by = db.Column(db.String(255), nullable=True)  # Add this for auth tracking

    def __init__(self, user_name: str, correct_guesses: int = 0, 
                 wrong_guesses: int = 0, total_rounds: int = 0,
                 created_by: str = None) -> None:
        self.user_name = user_name
        self.correct_guesses = correct_guesses
        self.wrong_guesses = wrong_guesses
        self.total_rounds = total_rounds
        self.created_by = created_by

    def calculate_win_rate(self) -> float:
        total = self.correct_guesses + self.wrong_guesses
        if total == 0:
            return 0.0
        return (self.correct_guesses / total) * 100

    def create(self) -> Optional['Stats']:
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def read(self) -> Dict[str, Any]:
        return {
            "username": self.user_name,
            "correct_guesses": self.correct_guesses,
            "wrong_guesses": self.wrong_guesses,
            "total_rounds": self.total_rounds,
            "win_rate": self.calculate_win_rate(),
            "created_by": self.created_by
        }

    def update(self, correct_increment: int = 0, wrong_increment: int = 0) -> bool:
        try:
            if correct_increment < 0 or wrong_increment < 0:
                return False
            
            self.correct_guesses += correct_increment
            self.wrong_guesses += wrong_increment
            self.total_rounds += 1
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

    def delete(self) -> bool:
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

def initStatsDataTable() -> None:
    """Initialize the stats database table"""
    with app.app_context():
        db.create_all()
