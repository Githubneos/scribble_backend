from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy import inspect
from __init__ import app, db

class Picture(db.Model):
    """Picture Model for storing drawing images with user authentication"""
    __tablename__ = 'pictures'
    
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255), nullable=False)
    drawing_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    image_data = db.Column(db.Text, nullable=False)  # Store base64 image data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_name, drawing_name, image_data, description=None):
        self.user_name = user_name
        self.drawing_name = drawing_name
        self.description = description
        self.image_data = image_data

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
            'id': self.id,
            'user_name': self.user_name,
            'drawing_name': self.drawing_name,
            'description': self.description,
            'image_url': f"data:image/png;base64,{self.image_data}",
            'created_at': self.created_at.isoformat() if self.created_at else None
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