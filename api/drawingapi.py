from sqlalchemy.exc import IntegrityError
from __init__ import app, db
from flask import request, jsonify, Blueprint

drawing_api = Blueprint('drawing_api', __name__)

@drawing_api.route('/drawings', methods=['GET'])
def get_drawings():
    # Implement the logic to get drawings
    return jsonify({"message": "List of drawings"}), 200

@drawing_api.route('/drawings', methods=['POST'])
def add_drawing():
    # Implement the logic to add a new drawing
    data = request.json
    user_name = data.get('user_name')
    drawing_name = data.get('drawing_name')
    drawing_data = data.get('drawing_data')

    if not user_name or not drawing_name or not drawing_data:
        return jsonify({"error": "Missing required fields"}), 400

    new_drawing = Drawing(user_name=user_name, drawing_name=drawing_name, drawing_data=drawing_data)
    created_drawing = new_drawing.create()

    if created_drawing:
        return jsonify(created_drawing.read()), 201
    else:
        return jsonify({"error": "Failed to create drawing"}), 500

@drawing_api.route('/save-drawing', methods=['POST'])
def save_drawing():
    try:
        # Debugging: Log the incoming request
        print("Incoming request data:", request.json)

        # Parse JSON input
        data = request.get_json()  # Use get_json() to parse JSON input
        if not data:
            print("No JSON data received")
            return jsonify({"error": "Invalid or missing JSON payload."}), 400

        # Log the received data for debugging
        print("Received data:", data)

        # Check if the required keys are present
        if 'drawing' not in data:
            print("Missing key: drawing")
            return jsonify({"error": "Missing key: drawing"}), 400

        # Extract values from the request
        drawing_data = data['drawing']
        user_name = data.get('user_name', 'default_user')  # Use default value if not provided
        drawing_name = data.get('drawing_name', 'default_drawing')  # Use default value if not provided
        timestamp = datetime.now().isoformat()

        # Ensure the drawings directory exists
        if not os.path.exists('drawings'):
            os.makedirs('drawings')

        # Decode and save the drawing
        try:
            base64_data = drawing_data.split(',')[1]
            file_path = f"drawings/{user_name}_{drawing_name}_{timestamp}.jpeg".replace(':', '-')
            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(base64_data))
            print(f"Drawing saved to {file_path}")
        except IndexError:
            print("Error: Drawing data is not in the expected format")
            return jsonify({"error": "Drawing data is not in the expected format"}), 400
        except Exception as e:
            print(f"Error decoding drawing data: {e}")
            return jsonify({"error": f"Error decoding drawing data: {e}"}), 400

        # Save metadata to the database
        try:
            database_path = current_app.config.get('DATABASE', 'instance/database.db')
            with sqlite3.connect(database_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS drawings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_name TEXT NOT NULL,
                        drawing_name TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        timestamp TEXT NOT NULL
                    )
                ''')
                cursor.execute('''
                    INSERT INTO drawings (user_name, drawing_name, file_path, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (user_name, drawing_name, file_path, timestamp))
                conn.commit()
            print("Drawing metadata saved to database")
        except Exception as e:
            print(f"Error saving metadata to database: {e}")
            return jsonify({"error": f"Error saving metadata to database: {e}"}), 500

        # Return success response
        return jsonify({"status": "Drawing saved successfully.", "file_path": file_path}), 201

    except KeyError as e:
        print("KeyError:", str(e))  # Log and handle missing keys
        return jsonify({"error": f"Missing key: {str(e)}"}), 400
    except TypeError as e:
        print("TypeError:", str(e))  # Log and handle type errors
        return jsonify({"error": f"Type error: {str(e)}"}), 400
    except Exception as e:
        # Log unexpected exceptions and provide better debugging info
        print("General Exception:", str(e))
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

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

@app.route('/api/drawings', methods=['POST'])
def create_drawing():
    """
    API endpoint to create a new drawing.
    """
    data = request.get_json()
    user_name = data.get('user_name')
    drawing_name = data.get('drawing_name')
    drawing_data = data.get('drawing_data')

    if not user_name or not drawing_name or not drawing_data:
        return jsonify({"error": "Missing required fields"}), 400

    new_drawing = Drawing(user_name=user_name, drawing_name=drawing_name, drawing_data=drawing_data)
    created_drawing = new_drawing.create()

    if created_drawing:
        return jsonify(created_drawing.read()), 201
    else:
        return jsonify({"error": "Failed to create drawing"}), 500

@app.route('/api/drawings/<int:drawing_id>', methods=['GET'])
def get_drawing(drawing_id):
    """
    API endpoint to retrieve a drawing by its ID.
    """
    drawing = Drawing.query.get(drawing_id)
    if drawing:
        return jsonify(drawing.read()), 200
    else:
        return jsonify({"error": "Drawing not found"}), 404

def initDrawingTable():
    """
    Initialize the drawings table by creating the database table.
    """
    with app.app_context():
        db.create_all()
        print("Drawing table initialized.")