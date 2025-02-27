import traceback
from flask import Blueprint, request, jsonify, g
from flask_restful import Api, Resource
from datetime import datetime
from __init__ import app, db
from api.jwt_authorize import token_required
import random
from model.blind_trace import BlindTraceSubmission  # Assume this model exists

blind_trace_api = Blueprint('blind_trace_api', __name__, url_prefix='/api/blind_trace')
api = Api(blind_trace_api)

class BlindTraceAPI:
    """
    API for handling Blind Trace submissions.
    Requires JWT authentication.
    """

    images = [
        "https://thumbs.dreamstime.com/b/tower-bridge-sunset-popular-landmark-london-uk-29462158.jpg",
        "https://t3.ftcdn.net/jpg/02/82/38/10/360_F_282381041_O7uUYn2MgQHcltBSnRnVf2daOZDR9nmO.jpg",
        "https://www.pexels.com/photo/landmark-1796686/",
        "https://www.pexels.com/photo/landmark-1796685/",
        "https://www.pexels.com/photo/landmark-1796687/"
    ]

    class _Image(Resource):
        @token_required()
        def get(self):
            """Fetch a random image for the Blind Trace challenge"""
            try:
                random_image = random.choice(BlindTraceAPI.images)
                return jsonify({"message": "Random image fetched", "image_url": random_image}), 200

            except Exception as e:
                print("Error fetching image:", str(e))
                traceback.print_exc()
                return jsonify({"message": "Internal Server Error", "error": str(e)}), 500

    class _Submission(Resource):
        @token_required()
        def post(self):
            """Submit a drawing (metadata only for now)"""
            try:
                current_user = g.current_user
                data = request.get_json()

                if not data or "image_url" not in data:
                    return jsonify({"message": "Missing required fields", "error": "Bad Request"}), 400

                submission = BlindTraceSubmission(
                    user_id=current_user.id,
                    image_url=data["image_url"],
                    submission_time=datetime.utcnow()
                )

                db.session.add(submission)
                db.session.commit()

                return jsonify({"message": "Submission saved successfully", "submission": submission.read()}), 201

            except Exception as e:
                db.session.rollback()
                print("Error submitting drawing:", str(e))
                traceback.print_exc()
                return jsonify({"message": "Internal Server Error", "error": str(e)}), 500

        @token_required()
        def get(self):
            """Retrieve all past submissions for the current user"""
            try:
                current_user = g.current_user
                submissions = BlindTraceSubmission.query.filter_by(user_id=current_user.id).all()

                if not submissions:
                    return jsonify({"message": "No submissions found", "submissions": []}), 200

                return jsonify({
                    "message": "Submissions retrieved successfully",
                    "submissions": [submission.read() for submission in submissions]
                }), 200

            except Exception as e:
                print("Error fetching submissions:", str(e))
                traceback.print_exc()
                return jsonify({"message": "Internal Server Error", "error": str(e)}), 500

        @token_required()
        def delete(self):
            """Delete a submission"""
            try:
                current_user = g.current_user
                data = request.get_json()

                if not data or "id" not in data:
                    return jsonify({"message": "Missing required fields", "error": "Bad Request"}), 400

                submission = BlindTraceSubmission.query.get(data["id"])
                if not submission:
                    return jsonify({"message": "Submission not found", "error": "Not Found"}), 404

                if submission.user_id != current_user.id:
                    return jsonify({"message": "Unauthorized to delete this submission", "error": "Forbidden"}), 403

                db.session.delete(submission)
                db.session.commit()

                return jsonify({"message": "Submission deleted successfully"}), 200

            except Exception as e:
                db.session.rollback()
                print("Error deleting submission:", str(e))
                traceback.print_exc()
                return jsonify({"message": "Internal Server Error", "error": str(e)}), 500

    # Register API endpoints
    api.add_resource(_Image, '/image')  # Fetch a random image
    api.add_resource(_Submission, '/submission')  # Handle submissions

