from sqlalchemy.exc import IntegrityError
from __init__ import app, db

class UserAttempts(db.Model):
    __tablename__ = 'user_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255), nullable=False)
    attempts_made = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.String(255), nullable=False)

    def __init__(self, user_name, attempts_made, time_taken):
        self.user_name = user_name
        self.attempts_made = attempts_made
        self.time_taken = time_taken

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            print(f"User Attempt Added: {self.user_name} - Attempts Made: {self.attempts_made} - Time Taken: {self.time_taken}")
        except IntegrityError:
            db.session.rollback()
            return None
        return self

    def read(self):
        return {
            "id": self.id,
            "user_name": self.user_name,
            "attempts_made": self.attempts_made,
            "time_taken": self.time_taken
        }

    def delete(self):
        db.session.delete(self)
        db.session.commit()

def init_db():
    with app.app_context():
        db.create_all()
        if not UserAttempts.query.first():
            initial_attempts = [
                UserAttempts(user_name="Alice", attempts_made=5, time_taken="10:00"),
                UserAttempts(user_name="Bob", attempts_made=3, time_taken="15:00"),
                UserAttempts(user_name="Charlie", attempts_made=7, time_taken="20:00")
            ]
            for attempt in initial_attempts:
                db.session.add(attempt)
            db.session.commit()

def initUserAttemptsTable():
    with app.app_context():
        db.create_all()
        print("UserAttempts table initialized.")
