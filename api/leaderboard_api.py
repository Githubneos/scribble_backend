from flask import Blueprint, request, g
from flask_restful import Api, Resource
from datetime import datetime
from __init__ import app
from api.jwt_authorize import token_required
from model.leaderboard import LeaderboardEntry

leaderboard_api = Blueprint('leaderboard_api', __name__, url_prefix='/api')
api = Api(leaderboard_api)

class LeaderboardAPI:
    class _CRUD(Resource):
        @token_required()
        def post(self):
            current_user = g.current_user
            data = request.get_json()

            if not data or "drawing_name" not in data or "score" not in data:
                return {
                    "message": "Missing required fields",
                    "error": "Bad Request"
                }, 400

            try:
                # Check if entry already exists for this user and drawing
                existing_entry = LeaderboardEntry.query.filter_by(
                    created_by=current_user.id,
                    drawing_name=data['drawing_name']
                ).first()

                if existing_entry:
                    # Update the score if new score is higher
                    if int(data['score']) > existing_entry.score:
                        existing_entry.score = int(data['score'])
                        existing_entry.update()
                        return existing_entry.read(), 200
                    return existing_entry.read(), 200
                else:
                    # Create new entry if none exists
                    entry = LeaderboardEntry(
                        profile_name=current_user.name,
                        drawing_name=data['drawing_name'],
                        score=int(data['score']),
                        created_by=current_user.id
                    )
                    entry.create()
                    return entry.read(), 201

            except Exception as e:
                return {
                    "message": "Failed to create/update entry",
                    "error": str(e)
                }, 500

        def get(self):
            try:
                entries = LeaderboardEntry.query.order_by(
                    LeaderboardEntry.score.desc()
                ).all()
                return [entry.read() for entry in entries]

            except Exception as e:
                return []

        @token_required()
        def delete(self):
            current_user = g.current_user
            
            if current_user.role != 'Admin':
                return {
                    "message": "Admin access required",
                    "error": "Forbidden"
                }, 403

            data = request.get_json()
            if not data or "id" not in data:
                return {
                    "message": "Missing entry ID",
                    "error": "Bad Request"
                }, 400

            try:
                entry = LeaderboardEntry.query.get(data['id'])
                if not entry:
                    return {
                        "message": "Entry not found", 
                        "error": "Not Found"
                    }, 404

                entry.delete()
                return {
                    "message": "Entry deleted successfully"
                }, 200

            except Exception as e:
                return {
                    "message": "Failed to delete entry",
                    "error": str(e)
                }, 500

    api.add_resource(_CRUD, '/leaderboard')
