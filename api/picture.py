from flask import Blueprint, request, jsonify, g
from flask_restful import Api, Resource
from datetime import datetime
import base64
from api.jwt_authorize import token_required
from model.picture import Picture, db

# Create Blueprint with same pattern as other APIs
picture_api = Blueprint('picture_api', __name__, url_prefix='/api')
api = Api(picture_api)

class PictureAPI:
    class _CRUD(Resource):
        @token_required()
        def post(self):
            """Create a new picture entry with authentication"""
            current_user = g.current_user
            
            try:
                data = request.form
                if not data:
                    return jsonify({
                        "message": "No data provided",
                        "error": "Bad Request"
                    }), 400

                if 'image' not in request.files:
                    return jsonify({
                        "message": "No image provided",
                        "error": "Bad Request"
                    }), 400

                file = request.files['image']
                if file.filename == '':
                    return jsonify({
                        "message": "No selected file",
                        "error": "Bad Request"
                    }), 400

                # Read and encode image data
                image_data = base64.b64encode(file.read()).decode('utf-8')

                # Create database entry
                picture = Picture(
                    user_name=current_user.name,
                    drawing_name=data.get('drawing_name'),
                    image_data=image_data,
                    description=data.get('description')
                )
                
                if picture.create():
                    return jsonify(picture.read()), 201
                return jsonify({
                    "message": "Failed to create picture entry",
                    "error": "Database Error"
                }), 500

            except Exception as e:
                return jsonify({
                    "message": "Failed to create picture entry",
                    "error": str(e)
                }), 500

        def get(self):
            """Retrieve all pictures"""
            try:
                pictures = Picture.query.order_by(Picture.created_at.desc()).all()
                return jsonify([p.read() for p in pictures])

            except Exception as e:
                return jsonify([])

        @token_required()
        def delete(self):
            """Delete a picture. Admin only."""
            current_user = g.current_user
            
            # Check if user is admin
            if current_user.role != 'Admin':
                return jsonify({
                    "message": "Admin access required",
                    "error": "Forbidden"
                }), 403

            data = request.get_json()
            if not data or "id" not in data:
                return jsonify({
                    "message": "Missing picture ID",
                    "error": "Bad Request"
                }), 400

            try:
                picture = Picture.query.get(data['id'])
                if not picture:
                    return jsonify({
                        "message": "Picture not found", 
                        "error": "Not Found"
                    }), 404

                picture.delete()
                return jsonify({
                    "message": "Picture deleted successfully"
                }), 200

            except Exception as e:
                return jsonify({
                    "message": "Failed to delete picture",
                    "error": str(e)
                }), 500

    api.add_resource(_CRUD, '/picture')