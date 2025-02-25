from sqlalchemy.exc import IntegrityError
from datetime import datetime
from __init__ import app, db

class Time(db.Model):
    """Time Model for storing drawing completion times"""
    __tablename__ = 'competition'  # Changed from timer_entries
    
    # Define columns with better constraints
    id = db.Column(db.Integer, primary_key=True)
    users_name = db.Column(db.String(255), nullable=False)
    timer_duration = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.Integer, nullable=False)
    drawn_word = db.Column(db.String(50), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_modified = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

    def __init__(self, users_name, timer_duration, time_taken, drawn_word, created_by):
        self.users_name = users_name
        self.timer_duration = self._validate_duration(timer_duration)
        self.time_taken = self._validate_time(time_taken)
        self.drawn_word = drawn_word
        self.created_by = created_by

    def _validate_duration(self, duration):
        """Validate timer duration is reasonable"""
        try:
            duration = int(duration)
            if not (1 <= duration <= 3600):  # 1 second to 1 hour
                raise ValueError("Duration must be between 1 and 3600 seconds")
            return duration
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid duration: {str(e)}")

    def _validate_time(self, time_taken):
        """Validate time taken is reasonable"""
        try:
            time_taken = int(time_taken)
            if time_taken < 0:
                raise ValueError("Time taken cannot be negative")
            return time_taken
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid time taken: {str(e)}")

    def __repr__(self):
        return f"Time(id={self.id}, users_name={self.users_name}, time_taken={self.time_taken})"

    def create(self):
        """Create and return a new time entry"""
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            raise e

    def read(self):
        """Return dictionary of time entry attributes"""
        return {
            "id": self.id,
            "users_name": self.users_name,
            "timer_duration": self.timer_duration,
            "time_taken": self.time_taken,
            "drawn_word": self.drawn_word,
            "created_by": self.created_by,
            "date_created": self.date_created.strftime("%Y-%m-%d %H:%M:%S"),
            "date_modified": self.date_modified.strftime("%Y-%m-%d %H:%M:%S")
        }

    def update(self):
        try:
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            raise e

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def find_by_id(cls, entry_id):
        """Find time entry by ID"""
        return cls.query.filter_by(id=entry_id).first()

    @classmethod
    def find_by_user(cls, user_id):
        """Find all entries by a specific user"""
        return cls.query.filter_by(created_by=user_id).all()

    @staticmethod
    def restore(data):
        entries = {}
        for entry_data in data:
            _ = entry_data.pop('id', None)
            users_name = entry_data.get("users_name", None)
            drawn_word = entry_data.get("drawn_word", None)
            
            entry = Time.query.filter_by(
                users_name=users_name,
                drawn_word=drawn_word
            ).first()
            
            if entry:
                entry.update(entry_data)
            else:
                entry = Time(**entry_data)
                entry.create()
            
            entries[f"{users_name}_{drawn_word}"] = entry
        
        return entries

def initTimerTable():
    """Initialize the timer database table"""
    with app.app_context():
        db.create_all()
        print("Timer table initialized")