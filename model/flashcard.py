from sqlalchemy.exc import IntegrityError
from __init__ import app, db

class Flashcard(db.Model):
    """
    Flashcard Model
    
    Attributes:
        id (int): Primary key for the flashcard.
        title (str): Title of the flashcard.
        content (str): Content of the flashcard.
        user_id (int): ID of the user who owns this flashcard.
    """
    __tablename__ = 'flashcards'

    id = db.Column(db.Integer, primary_key=True)
    _title = db.Column(db.String(255), nullable=False)
    _content = db.Column(db.String(255), nullable=False)
    _user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, title, content, user_id):
        self._title = title
        self._content = content
        self._user_id = user_id

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            print(f"Flashcard Created: {self._title}, {self._content}")
        except IntegrityError:
            db.session.rollback()
            return None
        return self

    def read(self):
        return {
            "id": self.id,
            "title": self._title,
            "content": self._content,
            "user_id": self._user_id
        }

    def update(self, data):
        for key, value in data.items():
            if key == "title":
                self._title = value
            if key == "content":
                self._content = value
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

def initFlashcards():
    with app.app_context():
        db.create_all()
        print("Flashcards table initialized.")