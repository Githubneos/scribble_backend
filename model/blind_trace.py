from sqlalchemy.exc import IntegrityError
from __init__ import app, db
from datetime import datetime

class BlindTraceSubmission(db.Model):
    """Model for storing Blind Trace drawing submissions"""
    __tablename__ = 'blind_trace_submissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)  # Image users were given to memorize
    drawing_url = db.Column(db.String(255), nullable=True)  # URL of user's drawn submission (if saved)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    submission_time = db.Column(db.DateTime, default=datetime.utcnow)
    date_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, user_id, image_url, drawing_url=None, is_deleted=False):
        self.user_id = user_id
        self.image_url = image_url
        self.drawing_url = drawing_url
        self.is_deleted = is_deleted

    def __repr__(self):
        return f"BlindTraceSubmission(id={self.id}, user_id={self.user_id}, image_url={self.image_url})"

    def create(self):
        """Create and save a new Blind Trace submission"""
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Duplicate entry or constraint violation")
        except Exception as e:
            db.session.rollback()
            raise e

    def read(self):
        """Return dictionary representation of submission"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "image_url": self.image_url,
            "drawing_url": self.drawing_url,
            "is_deleted": self.is_deleted,
            "submission_time": self.submission_time.strftime("%Y-%m-%d %H:%M:%S"),
            "date_modified": self.date_modified.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def update(self):
        """Update the submission (mark as modified)"""
        try:
            self.date_modified = datetime.utcnow()  # Automatically update the modification time
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            raise e

    def delete(self):
        """Delete the submission (soft delete by setting `is_deleted` to True)"""
        try:
            self.is_deleted = True
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def find_by_id(cls, submission_id):
        """Find a submission by ID"""
        return cls.query.filter_by(id=submission_id, is_deleted=False).first()

    @classmethod
    def find_by_user(cls, user_id):
        """Find all submissions by a specific user"""
        return cls.query.filter_by(user_id=user_id, is_deleted=False).all()

def initBlindTraceTable():
    """Initialize the Blind Trace Submissions table"""
    with app.app_context():
        BlindTraceSubmission.__table__.drop(db.engine, checkfirst=True)
        db.create_all()
        print("Blind Trace Submissions table initialized")
