from sqlite3 import IntegrityError
from __init__ import app, db
from model.user import User

class Guess(db.Model):
    __tablename__ = 'guesses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    drawing_id = db.Column(db.String(255), nullable=False)
    guess = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, drawing_id, guess, is_correct, timestamp):
        """
        Constructor for Guess.
        
        Args:
            user_id (int): ID of the user making the guess.
            drawing_id (str): ID of the drawing being guessed.
            guess (str): User's guess.
            is_correct (bool): Whether the guess is correct.
            timestamp (datetime): When the guess was made.
        """
        self.user_id = user_id
        self.drawing_id = drawing_id
        self.guess = guess
        self.is_correct = is_correct
        self.timestamp = timestamp

    def create(self):
        """
        Add the guess to the database.
        """
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def read(self):
        """
        Return a dictionary representation of the guess.
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'drawing_id': self.drawing_id,
            'guess': self.guess,
            'is_correct': self.is_correct,
            'timestamp': self.timestamp.isoformat()
        }
