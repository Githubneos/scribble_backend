from sqlalchemy.exc import IntegrityError
from __init__ import app, db
import requests

class Time(db.Model):
    """
    TimerDataTable Model

    Attributes:
        id (int): Primary key for the guess entry.
        users_name (str): Name of the guesser.
        timer (str): The timer value.
        amount_drawn (int): Number of drawings made by the guesser.
    """
    __tablename__ = 'timer_data_table'

    id = db.Column(db.Integer, primary_key=True)
    users_name = db.Column(db.String(255), nullable=False)
    timer = db.Column(db.String(255), nullable=False)
    amount_drawn = db.Column(db.Integer, nullable=False)

    def __init__(self, users_name, timer, amount_drawn):
        self.users_name = users_name
        self.timer = timer
        self.amount_drawn = amount_drawn

    def create(self):
        """
        Add a new guess entry to the database.
        """
        try:
            db.session.add(self)
            db.session.commit()
            print(f"Guess Added: {self.users_name} set timer '{self.timer}' - Amount Drawn: {self.amount_drawn}")
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
            "users_name": self.users_name,
            "timer": self.timer,
            "amount_drawn": self.amount_drawn
        }

    def delete(self):
        """
        Delete this guess entry from the database.
        """
        db.session.delete(self)
        db.session.commit()

def initTimerDataTable():
    """
    Initialize the timer_data_table by creating the database table.
    """
    with app.app_context():
        db.create_all()
        print("TimerDataTable initialized.")
