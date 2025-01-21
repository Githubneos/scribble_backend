from sqlalchemy.exc import IntegrityError
from __init__ import app, db
import requests
class Time(db.Model):
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
        try:
            db.session.add(self)
            db.session.commit()
            print(f"Time Added: {self.users_name} - Timer: '{self.timer}' - Amount Drawn: {self.amount_drawn}")
        except IntegrityError:
            db.session.rollback()
            return None
        return self

    def read(self):
        return {
            "id": self.id,
            "users_name": self.users_name,
            "timer": self.timer,
            "amount_drawn": self.amount_drawn
        }

    def delete(self):
        db.session.delete(self)
        db.session.commit()

def init_db():
    with app.app_context():
        db.create_all()

def initTimerDataTable():
    with app.app_context():
        db.create_all()
        print("TimerDataTable initialized.")
