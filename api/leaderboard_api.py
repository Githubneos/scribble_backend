from flask import Blueprint, request, g
from flask_restful import Api, Resource
from datetime import datetime
from __init__ import app
from api.jwt_authorize import token_required
from model.leaderboard import LeaderboardEntry
from model.competition import Time

leaderboard_api = Blueprint('leaderboard_api', __name__, url_prefix='/api')
api = Api(leaderboard_api)

class LeaderboardAPI:
    class _CRUD(Resource):
        @token_required()
        def post(self):
            current_user = g.current_user
            data = request.get_json()

            if not data or "drawing_name" not in data:
                return {
                    "message": "Missing drawing name",
                    "error": "Bad Request"
                }, 400

            try:
                if "score" in data:
                    # Manual score input
                    score = int(data['score'])
                else:
                    # Get competition data for automatic score calculation
                    competition_entry = Time.query.filter_by(
                        created_by=current_user.id,
                        drawn_word=data['drawing_name']
                    ).first()

                    if not competition_entry:
                        return {
                            "message": "No competition entry found for this drawing",
                            "error": "Not Found"
                        }, 404

                    # Calculate speed factor and scale to 1000 points
                    speed_factor = competition_entry.timer_duration / competition_entry.time_taken
                    score = min(1000, int(speed_factor * 500))

                # Check if entry exists and update if necessary
                existing_entry = LeaderboardEntry.query.filter_by(
                    created_by=current_user.id,
                    drawing_name=data['drawing_name']
                ).first()

                if existing_entry:
                    if score > existing_entry.score:
                        existing_entry.score = score
                        existing_entry.update()
                    return existing_entry.read(), 200
                else:
                    entry = LeaderboardEntry(
                        profile_name=current_user.name,
                        drawing_name=data['drawing_name'],
                        score=score,
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
            """Get leaderboard entries with calculated scores from competition data"""
            try:
                # Track deleted entries to prevent re-adding
                deleted_entries = set()
                competition_entries = Time.query.all()
                print(f"Found {len(competition_entries)} competition entries")
                result = {}

                for entry in competition_entries:
                    word = entry.drawn_word
                    if word not in result:
                        result[word] = []
                        print(f"Processing word: {word}")

                    # Skip if this entry was previously deleted from leaderboard
                    entry_key = f"{entry.created_by}_{word}"
                    if entry_key in deleted_entries:
                        continue

                    # Calculate speed factor: original_time/actual_time
                    speed_factor = entry.timer_duration / entry.time_taken
                    score = min(1000, int(speed_factor * 500))
                    print(f"Speed factor for {entry.users_name}: {speed_factor:.2f}, Score: {score}")

                    # Create or update leaderboard entry
                    leaderboard_entry = LeaderboardEntry.query.filter_by(
                        created_by=entry.created_by,
                        drawing_name=word
                    ).first()

                    if leaderboard_entry and not leaderboard_entry.is_deleted:
                        if score > leaderboard_entry.score:
                            leaderboard_entry.score = score
                            leaderboard_entry.update()
                        result[word].append(leaderboard_entry.read())
                    elif not leaderboard_entry:
                        leaderboard_entry = LeaderboardEntry(
                            profile_name=entry.users_name,
                            drawing_name=word,
                            score=score,
                            created_by=entry.created_by,
                            is_deleted=False
                        )
                        leaderboard_entry.create()
                        result[word].append(leaderboard_entry.read())

                # Sort each word's entries by score
                for word in result:
                    result[word] = sorted(
                        result[word],
                        key=lambda x: x['score'],
                        reverse=True
                    )

                return result

            except Exception as e:
                print(f"Error in get method: {str(e)}")
                return {}

        @token_required()
        def delete(self):
            """Delete a leaderboard entry (Admin only)"""
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

                # Mark as deleted instead of actually deleting
                entry.is_deleted = True
                entry.update()
                
                return {
                    "message": "Entry deleted successfully"
                }, 200

            except Exception as e:
                return {
                    "message": "Failed to delete entry",
                    "error": str(e)
                }, 500

    api.add_resource(_CRUD, '/leaderboard')
