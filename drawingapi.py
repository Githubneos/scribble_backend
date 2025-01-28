from flask import Blueprint
from sqlalchemy.exc import IntegrityError
from __init__ import app, db
from flask import request, jsonify

drawing_api = Blueprint('drawing_api', __name__)

class Drawing(db.Model):
    # ...existing code...

@drawing_api.route('/api/drawings', methods=['POST'])
def create_drawing():
    # ...existing code...

@drawing_api.route('/api/drawings/<int:drawing_id>', methods=['GET'])
def get_drawing(drawing_id):
    # ...existing code...

def initDrawingTable():
    # ...existing code...
