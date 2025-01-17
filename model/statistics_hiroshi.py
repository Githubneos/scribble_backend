from sqlalchemy.exc import IntegrityError
from __init__ import app, db
from typing import Optional, Dict, Any

class Stats(db.Model):
    """
    StatsDataTable Model

    Attributes:
        id (int): Primary key for the stats entry.
        user_name (str): Name of the user associated with the stats.
        correct_guesses (int): Number of correct guesses.
        wrong_guesses (int): Number of wrong guesses.
        total_rounds (int): Total rounds played.
    """
    __tablename__ = 'stats_data_table'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255), nullable=False, unique=True)
    correct_guesses = db.Column(db.Integer, nullable=False, default=0)
    wrong_guesses = db.Column(db.Integer, nullable=False, default=0)
    total_rounds = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, user_name: str, correct_guesses: int = 0, 
                 wrong_guesses: int = 0, total_rounds: int = 0) -> None:
        self.user_name = user_name
        self.correct_guesses = correct_guesses
        self.wrong_guesses = wrong_guesses
        self.total_rounds = total_rounds

    def create(self) -> Optional['Stats']:
        """
        Add a new stats entry to the database.
        Returns:
            Stats: The created stats object, None if creation fails
        """
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def read(self) -> Dict[str, Any]:
        """
        Return the stats data in dictionary format.
        Returns:
            dict: Dictionary containing stats data
        """
        return {
            "id": self.id,
            "user_name": self.user_name,
            "correct_guesses": self.correct_guesses,
            "wrong_guesses": self.wrong_guesses,
            "total_rounds": self.total_rounds
        }

    def update(self, correct_increment: int = 0, wrong_increment: int = 0) -> bool:
        """
        Update the statistics for the user.
        Args:
            correct_increment: Number of correct guesses to add
            wrong_increment: Number of wrong guesses to add
        Returns:
            bool: True if update successful, False otherwise
        """
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
        """
        Delete this stats entry from the database.
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

def initStatsDataTable() -> None:
    """
    Initialize the stats_data_table by creating the database table.
    """
    with app.app_context():
        db.create_all()
        print("StatsDataTable initialized.")
