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
        if not Time.query.first():
            initial_times = [
                Time(users_name="Alice", timer="10:00", amount_drawn=5),
                Time(users_name="Bob", timer="15:00", amount_drawn=3),
                Time(users_name="Charlie", timer="20:00", amount_drawn=7)
            ]
            for time_entry in initial_times:
                db.session.add(time_entry)
            db.session.commit()

def initTimerDataTable():
    with app.app_context():
        db.create_all()
        print("TimerDataTable initialized.")
