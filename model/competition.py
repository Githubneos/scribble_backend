from sqlalchemy.exc import IntegrityError
from datetime import datetime
from __init__ import app, db

class Time(db.Model):
    """Time Model for storing drawing completion times"""
    __tablename__ = 'drawing_times'

    id = db.Column(db.Integer, primary_key=True)
    users_name = db.Column(db.String(255), nullable=False)
    time_taken = db.Column(db.Integer, nullable=False)  # Time in seconds
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, users_name, time_taken, created_by):
        self.users_name = users_name
        self.time_taken = time_taken
        self.created_by = created_by

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def read(self):
        return {
            "id": self.id,
            "users_name": self.users_name,
            "time_taken": self.time_taken,
            "date_created": self.date_created.strftime("%Y-%m-%d %H:%M:%S")
        }

def initTimerTable():
    """Initialize the timer database table"""
    with app.app_context():
        db.create_all()
