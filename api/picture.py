from flask import Blueprint, request, g
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
                    return {
                        "message": "No data provided",
                        "error": "Bad Request"
                    }, 400

                if 'image' not in request.files:
                    return {
                        "message": "No image provided",
                        "error": "Bad Request"
                    }, 400

                file = request.files['image']
                if file.filename == '':
                    return {
                        "message": "No selected file",
                        "error": "Bad Request"
                    }, 400
                
                # Add file type validation
                if not file.content_type.startswith('image/'):
                    return {
                        "message": "Invalid file type - must be an image",
                        "error": "Bad Request"
                    }, 400

                # Read and encode image data
                image_bytes = file.read()
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                # Remove duplicate data URI prefix
                image_data = f"data:image/png;base64,{image_base64}"

                # Create database entry
                picture = Picture(
                    user_name=current_user.name,
                    drawing_name=data.get('drawing_name'),
                    image_data=image_data,
                    description=data.get('description')
                )
                
                if picture.create():
                    return picture.read(), 201
                return {
                    "message": "Failed to create picture entry",
                    "error": "Database Error"
                }, 500

            except Exception as e:
                print(f"Upload error: {str(e)}")  # Debug log
                return {
                    "message": "Failed to create picture entry",
                    "error": str(e)
                }, 500

        def get(self):
            """Retrieve all pictures"""
            try:
                pictures = Picture.query.order_by(Picture.created_at.desc()).all()
                return [p.read() for p in pictures]
            except Exception as e:
                print(f"Get error: {str(e)}")  # Debug log
                return []

        @token_required()
        def delete(self):
            """Delete a picture. Admin only."""
            current_user = g.current_user
            
            if current_user.role != 'Admin':
                return {
                    "message": "Admin access required",
                    "error": "Forbidden"
                }, 403

            data = request.get_json()
            if not data or "id" not in data:
                return {
                    "message": "Missing picture ID",
                    "error": "Bad Request"
                }, 400

            try:
                picture = Picture.query.get(data['id'])
                if not picture:
                    return {
                        "message": "Picture not found", 
                        "error": "Not Found"
                    }, 404

                picture.delete()
                return {
                    "message": "Picture deleted successfully"
                }, 200

            except Exception as e:
                print(f"Delete error: {str(e)}")  # Debug log
                return {
                    "message": "Failed to delete picture",
                    "error": str(e)
                }, 500

    api.add_resource(_CRUD, '/picture')