from flask import Blueprint, request, jsonify
from flask_cors import CORS
from flask_restful import Api, Resource
from datetime import datetime
import os
import base64
from werkzeug.utils import secure_filename
from model.picture import Picture, db

picture_api = Blueprint('picture_api', __name__)
CORS(picture_api)

UPLOAD_FOLDER = 'static/uploads/pictures'
ALLOWED_EXTENSIONS = {'png'}

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class _PictureAPI(Resource):
    def post(self):
        """Handle picture upload with metadata"""
        try:
            data = request.form
            if not data:
                return {'error': 'No data provided'}, 400

            user_name = data.get('user_name')
            drawing_name = data.get('drawing_name')
            description = data.get('description')

            if not all([user_name, drawing_name]):
                return {'error': 'Missing required fields'}, 400

            if 'image' not in request.files:
                return {'error': 'No image provided'}, 400

            file = request.files['image']
            if file.filename == '':
                return {'error': 'No selected file'}, 400

            # Read and encode image data
            image_data = base64.b64encode(file.read()).decode('utf-8')

            # Create database entry with base64 image data
            picture = Picture(
                user_name=user_name,
                drawing_name=drawing_name,
                description=description,
                image_data=image_data
            )
            
            if picture.create():
                return {
                    'message': 'Picture uploaded successfully',
                    'picture': picture.read()
                }, 201
            return {'error': 'Failed to save picture'}, 400

        except Exception as e:
            return {'error': f'Server error: {str(e)}'}, 500

    def get(self):
        """Retrieve pictures with optional filtering"""
        try:
            pictures = Picture.query.all()
            return {'pictures': [p.read() for p in pictures]}, 200

        except Exception as e:
            return {'error': f'Server error: {str(e)}'}, 500

# Add the resource to the API
api = Api(picture_api)
api.add_resource(_PictureAPI, '/api/picture')