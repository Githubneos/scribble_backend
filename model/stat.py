from sqlalchemy.exc import IntegrityError
from __init__ import app, db
import requests

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
    user_name = db.Column(db.String(255), nullable=False)
    correct_guesses = db.Column(db.Integer, nullable=False, default=0)
    wrong_guesses = db.Column(db.Integer, nullable=False, default=0)
    total_rounds = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, user_name, correct_guesses=0, wrong_guesses=0, total_rounds=0):
        self.user_name = user_name
        self.correct_guesses = correct_guesses
        self.wrong_guesses = wrong_guesses
        self.total_rounds = total_rounds

    def create(self):
        """
        Add a new stats entry to the database.
        """
        try:
            db.session.add(self)
            db.session.commit()
            print(f"Stats Added: {self.user_name} - Correct: {self.correct_guesses}, Wrong: {self.wrong_guesses}, Total Rounds: {self.total_rounds}")
        except IntegrityError:
            db.session.rollback()
            return None
        return self

    def read(self):
        """
        Return the stats data in dictionary format.
        """
        return {
            "id": self.id,
            "user_name": self.user_name,
            "correct_guesses": self.correct_guesses,
            "wrong_guesses": self.wrong_guesses,
            "total_rounds": self.total_rounds
        }

    def update(self, correct_increment=0, wrong_increment=0):
        """
        Update the statistics for the user.
        """
        self.correct_guesses += correct_increment
        self.wrong_guesses += wrong_increment
        self.total_rounds += 1  # Assume one round is completed for each update
        db.session.commit()

    def delete(self):
        """
        Delete this stats entry from the database.
        """
        db.session.delete(self)
        db.session.commit()

def initStatsDataTable():
    """
    Initialize the stats_data_table by creating the database table.
    """
    with app.app_context():
        db.create_all()
        print("StatsDataTable initialized.")
