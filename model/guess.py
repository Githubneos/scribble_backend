from sqlalchemy.exc import IntegrityError
from datetime import datetime
from __init__ import app, db
import requests
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
class Guess(db.Model):
    """Model for storing user guesses"""
    __tablename__ = 'guesses'
    
    id = db.Column(db.Integer, primary_key=True)
    guesser_name = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)
    guess = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            raise e

    def read(self):
        return {
            'id': self.id,
            'guesser_name': self.guesser_name,
            'guess': self.guess,
            'correct_answer': self.correct_answer,
            'is_correct': self.is_correct,
            'created_by': self.created_by,
            'date_created': self.date_created.strftime("%Y-%m-%d %H:%M:%S")
        }

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

def initGuessDataTable():
    """Initialize word guess table"""
    with app.app_context():
        db.create_all()
        print("Word guess table initialized")

