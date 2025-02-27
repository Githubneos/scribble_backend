import traceback
import base64
import io
import numpy as np
from flask import Blueprint, request, jsonify, g
from flask_restful import Api, Resource
from datetime import datetime
from __init__ import db
from api.jwt_authorize import token_required
from model.blind_trace import BlindTraceSubmission
from PIL import Image
import requests

# Blueprint & API Initialization
blind_trace_api = Blueprint('blind_trace_api', __name__, url_prefix='/api/blind_trace')
api = Api(blind_trace_api)

class BlindTraceAPI:
    class _Submission(Resource):
        @token_required()
        def post(self):
            """Submit a drawing, grade it using SSIM, and store the result"""
            current_user = g.current_user
            data = request.get_json()

            # Validate request data
            if not data or "image_url" not in data or "drawing" not in data:
                return {"message": "Missing required fields", "error": "Bad Request"}, 400

            try:
                # Decode base64 drawing
                drawing_data = base64.b64decode(data["drawing"].split(",")[1])
                drawing_img = Image.open(io.BytesIO(drawing_data)).convert("L")  # Convert to grayscale

                # Fetch reference image
                reference_img = Image.open(io.BytesIO(requests.get(data["image_url"]).content)).convert("L")

                # Resize to match dimensions
                reference_img = reference_img.resize(drawing_img.size)

                # Convert images to numpy arrays
                drawing_arr = np.array(drawing_img)
                reference_arr = np.array(reference_img)

                # Compute Mean Squared Error (MSE)
                mse = np.mean((drawing_arr - reference_arr) ** 2)
                max_mse = np.prod(drawing_arr.shape) * 255**2  # Max possible MSE for 8-bit images
                score = round(100 * (1 - mse / max_mse), 2)  # Normalize to percentage

                # Save submission
                submission = BlindTraceSubmission(
                    user_id=current_user.id,
                    image_url=data["image_url"],
                    drawing=data["drawing"],
                    score=score,
                    submission_time=datetime.utcnow()
                )
                db.session.add(submission)
                db.session.commit()

                return {
                    "message": "Submission graded",
                    "score": score,
                    "submission": submission.read()
                }, 201

            except Exception as e:
                db.session.rollback()
                traceback.print_exc()
                return {"message": "Internal Server Error", "error": str(e)}, 500

        @token_required()
        def get(self):
            """Retrieve all past submissions for the current user"""
            current_user = g.current_user
            try:
                submissions = BlindTraceSubmission.query.filter_by(user_id=current_user.id).all()
                return {
                    "message": "Submissions retrieved successfully",
                    "submissions": [sub.read() for sub in submissions]
                }, 200
            except Exception as e:
                traceback.print_exc()
                return {"message": "Internal Server Error", "error": str(e)}, 500

        @token_required()
        def delete(self):
            """Delete a submission by ID"""
            current_user = g.current_user
            data = request.get_json()

            if not data or "id" not in data:
                return {"message": "Missing required fields", "error": "Bad Request"}, 400

            try:
                submission = BlindTraceSubmission.query.get(data["id"])
                if not submission:
                    return {"message": "Submission not found", "error": "Not Found"}, 404
                
                if submission.user_id != current_user.id:
                    return {"message": "Unauthorized to delete this submission", "error": "Forbidden"}, 403

                db.session.delete(submission)
                db.session.commit()

                return {"message": "Submission deleted successfully"}, 200

            except Exception as e:
                db.session.rollback()
                traceback.print_exc()
                return {"message": "Internal Server Error", "error": str(e)}, 500

    # Register API endpoint
    api.add_resource(_Submission, '/submission')
