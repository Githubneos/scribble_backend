from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from model.leaderboard import LeaderboardEntry, db
from api.jwt_authorize import token_required

leaderboard_api = Blueprint('leaderboard_api', __name__, url_prefix='/api')
api = Api(leaderboard_api)

class LeaderboardAPI:
    """
    Define the API CRUD endpoints for the Leaderboard model.
    All endpoints require JWT token authentication.
    """
    class _CRUD(Resource):
        @token_required
        def post(self, current_user):
            """Create a new leaderboard entry"""
            try:
                data = request.get_json()
                if not data:
                    return {'message': 'No data provided'}, 400

                entry = LeaderboardEntry(
                    profile_name=data.get('profile_name', current_user.name),
                    drawing_name=data.get('drawing_name'),
                    score=int(data.get('score', 0))
                )
                
                if entry.create():
                    return {'message': 'Entry added successfully'}, 201
                return {'message': 'Failed to add entry'}, 400

            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}, 500

        @token_required
        def get(self, current_user):
            """Retrieve all leaderboard entries"""
            try:
                entries = LeaderboardEntry.query.order_by(
                    LeaderboardEntry.score.desc()
                ).all()
                return jsonify([entry.read() for entry in entries]), 200
            except Exception as e:
                return {'error': str(e)}, 500

        @token_required
        def put(self, current_user):
            """Update a leaderboard entry"""
            try:
                data = request.get_json()
                if not data:
                    return {'message': 'No data provided'}, 400

                profile_name = data.get('profile_name', current_user.name)
                drawing_name = data.get('drawing_name')

                # Check if user is updating their own entry
                if profile_name != current_user.name:
                    return {'message': 'Unauthorized to update other users entries'}, 403

                existing_entry = LeaderboardEntry.query.filter_by(
                    profile_name=profile_name,
                    drawing_name=drawing_name
                ).first()

                new_score = int(data.get('score', 0))

                if existing_entry:
                    existing_entry.score = new_score
                    db.session.commit()
                    return {'message': 'Score updated successfully'}, 200

                entry = LeaderboardEntry(
                    profile_name=profile_name,
                    drawing_name=drawing_name,
                    score=new_score
                )
                
                if entry.create():
                    return {'message': 'New entry created'}, 201
                return {'message': 'Failed to create entry'}, 400

            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}, 500

        @token_required
        def delete(self, current_user):
            """Delete a leaderboard entry"""
            try:
                data = request.get_json()
                if not data:
                    return {'message': 'No data provided'}, 400

                profile_name = data.get('profile_name')
                drawing_name = data.get('drawing_name')

                # Check if user is deleting their own entry
                if profile_name != current_user.name:
                    return {'message': 'Unauthorized to delete other users entries'}, 403

                if not profile_name or not drawing_name:
                    return {'message': 'Missing profile_name or drawing_name'}, 400

                entry = LeaderboardEntry.query.filter_by(
                    profile_name=profile_name,
                    drawing_name=drawing_name
                ).first()

                if not entry:
                    return {'message': 'Entry not found'}, 404

                entry.delete()
                return {'message': 'Entry deleted successfully'}, 200

            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}, 500

    class _List(Resource):
        @token_required
        def get(self, current_user):
            """Get all leaderboard entries sorted by score"""
            try:
                entries = LeaderboardEntry.query.order_by(
                    LeaderboardEntry.score.desc()
                ).all()
                return jsonify({
                    "message": "Entries retrieved successfully",
                    "entries": [entry.read() for entry in entries]
                }), 200
            except Exception as e:
                return {'error': str(e)}, 500

    # Register API endpoints
    api.add_resource(_CRUD, '/leaderboard')
    api.add_resource(_List, '/leaderboard/list')

