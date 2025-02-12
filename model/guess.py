from sqlalchemy.exc import IntegrityError
from __init__ import app, db
import requests
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy

#db = SQLAlchemy()
class Guess(db.Model):
    """
    GuessDataTable Model

    Attributes:
        id (int): Primary key for the guess entry.
        guesser_name (str): Name of the guesser.
        guess (str): The guessed value.
        is_correct (bool): Indicates if the guess was correct.
        created_by (str): Name of the user who created the guess.
    """
    __tablename__ = 'guess_data_table'

    id = db.Column(db.Integer, primary_key=True)
    guesser_name = db.Column(db.String(255), nullable=False)
    guess = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    created_by = db.Column(db.String(255), nullable=True)  # Add auth tracking

    def __init__(self, guesser_name, guess, is_correct, created_by=None):
        self.guesser_name = guesser_name
        self.guess = guess
        self.is_correct = is_correct
        self.created_by = created_by

    def create(self):
        """
        Add a new guess entry to the database.
        """
        try:
            db.session.add(self)
            db.session.commit()
            print(f"Guess Added: {self.guesser_name} guessed '{self.guess}' - Correct: {self.is_correct}")
        except IntegrityError:
            db.session.rollback()
            return None
        return self

    def read(self):
        """
        Return the guess data in dictionary format.
        """
        return {
            "id": self.id,
            "guesser_name": self.guesser_name,
            "guess": self.guess,
            "is_correct": self.is_correct,
            "created_by": self.created_by
        }

    def delete(self):
        """
        Delete this guess entry from the database.
        """
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

def initGuessDataTable():
    """
    Initialize the guess_data_table by creating the database table.
    """
    with app.app_context():
        db.create_all()
        print("GuessDataTable initialized.")

