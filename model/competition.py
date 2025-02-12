from sqlalchemy.exc import IntegrityError
from __init__ import app, db

class Time(db.Model):
    """Time Model for storing competition timer data"""
    __tablename__ = 'timer_data_table'

    id = db.Column(db.Integer, primary_key=True)
    users_name = db.Column(db.String(255), nullable=False)
    timer = db.Column(db.String(255), nullable=False)
    amount_drawn = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.String(255), nullable=True)  # Add auth tracking

    def __init__(self, users_name, timer, amount_drawn, created_by=None):
        self.users_name = users_name
        self.timer = timer
        self.amount_drawn = amount_drawn
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
            "timer": self.timer,
            "amount_drawn": self.amount_drawn,
            "created_by": self.created_by
        }

    def update(self, data):
        try:
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

def initTimerTable():
    """Initialize the timer database table"""
    with app.app_context():
        db.create_all()
