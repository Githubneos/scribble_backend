from sqlalchemy.exc import IntegrityError
from __init__ import app, db  # Correct import statement

class Drawing(db.Model):
    """
    Drawing Model

    Attributes:
        id (int): Primary key for the drawing entry.
        user_name (str): Name of the user who created the drawing.
        drawing_name (str): Name of the drawing.
        drawing_data (str): Base64-encoded drawing data.
    """
    __tablename__ = 'drawings'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255), nullable=False)
    drawing_name = db.Column(db.String(255), nullable=False)
    drawing_data = db.Column(db.Text, nullable=False)

    def __init__(self, user_name, drawing_name, drawing_data):
        self.user_name = user_name
        self.drawing_name = drawing_name
        self.drawing_data = drawing_data

    def create(self):
        """
        Add a new drawing entry to the database.
        """
        try:
            db.session.add(self)
            db.session.commit()
            print(f"Drawing Added: {self.user_name} - Drawing: '{self.drawing_name}'")
        except IntegrityError:
            db.session.rollback()
            return None
        return self

    def read(self):
        """
        Return the drawing data in dictionary format.
        """
        return {
            "id": self.id,
            "user_name": self.user_name,
            "drawing_name": self.drawing_name,
            "drawing_data": self.drawing_data
        }

    def delete(self):
        """
        Delete this drawing entry from the database.
        """
        db.session.delete(self)
        db.session.commit()

def initDrawingTable():
    """
    Initialize the drawings table by creating the database table.
    """
    with app.app_context():
        db.create_all()
        print("Drawing table initialized.")