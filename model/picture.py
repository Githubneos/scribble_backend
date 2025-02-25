from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy import inspect
from __init__ import app, db

class Picture(db.Model):
    """Picture Model for storing drawing images"""
    __tablename__ = 'pictures'

    id = db.Column(db.Integer, primary_key=True)
    drawing_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_data = db.Column(db.Text, nullable=False)  # Base64 encoded image
    user_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, drawing_name, description, image_data, user_name):
        self.drawing_name = drawing_name
        self.description = description
        self.image_data = image_data
        self.user_name = user_name

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    def read(self):
        return {
            "id": self.id,
            "drawing_name": self.drawing_name,
            "description": self.description,
            "image_data": self.image_data,  # This should include the data URI prefix
            "user_name": self.user_name,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

def initPictureTable():
    """Create the pictures table if it doesn't exist"""
    try:
        inspector = inspect(db.engine)
        if not inspector.has_table('pictures'):
            db.create_all()
            print("Picture table created successfully")
        else:
            print("Picture table already exists")
    except Exception as e:
        print("Error creating Picture table:", str(e))