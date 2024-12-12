import jwt
import os
import base64
import random
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from __init__ import app
from api.jwt_authorize import token_required

# Mock for machine learning analysis
def analyze_drawing(image_path):
    """Simulate drawing analysis and return detected features."""
    # Here, we can integrate an ML model like TensorFlow/Keras or OpenCV
    return random.choice([
        "circle",
        "square",
        "animal",
        "tree",
        "abstract shape",
    ])

def generate_hints(feature):
    """Generate hints based on the analyzed feature."""
    hints = {
        "circle": ["Is it something round?", "Think about wheels or balls."],
        "square": ["Does it have four sides?", "Maybe it’s a box or a frame?"],
        "animal": ["Does it look alive?", "Could it be a pet or a wild animal?"],
        "tree": ["Is it tall and leafy?", "Could it be a type of plant?"],
        "abstract shape": ["Could it be symbolic?", "Think outside the box!"],
    }
    return hints.get(feature, ["Try something else!", "Think creatively!"])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Routes
@app.route('/drawings', methods=['POST'])
def upload_drawing():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    prompt = request.form.get('prompt', '')

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Analyze the drawing
    feature = analyze_drawing(file_path)
    hints = generate_hints(feature)

    response = {
        "message": "Drawing uploaded successfully!",
        "drawing": {
            "filename": filename,
            "prompt": prompt,
            "feature": feature,
            "hints": hints,
        },
    }
    return jsonify(response), 201

if __name__ == '__main__':
    app.run(debug=True)
