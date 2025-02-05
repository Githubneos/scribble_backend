from flask import Blueprint, request, jsonify, g
from flask_cors import CORS
from flask_restful import Api, Resource
from model.leaderboard import LeaderboardEntry, db

leaderboard_api = Blueprint('leaderboard_api', __name__)
CORS(leaderboard_api)

class _LeaderboardCRUD(Resource):
    def post(self):
        """Create a new leaderboard entry"""
        try:
            data = request.get_json()
            if not data:
                return {'message': 'No data provided'}, 400

            entry = LeaderboardEntry(
                profile_name=data.get('profile_name'),
                drawing_name=data.get('drawing_name'),
                score=int(data.get('score', 0))
            )
            
            if entry.create():
                return {'message': 'Entry added successfully'}, 201
            return {'message': 'Failed to add entry'}, 400

        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def get(self):
        """Retrieve all leaderboard entries"""
        try:
            entries = LeaderboardEntry.query.order_by(
                LeaderboardEntry.score.desc()
            ).all()
            return jsonify([entry.read() for entry in entries]), 200
        except Exception as e:
            return {'error': str(e)}, 500

    def put(self):
        """Update a leaderboard entry"""
        try:
            data = request.get_json()
            if not data:
                return {'message': 'No data provided'}, 400

            existing_entry = LeaderboardEntry.query.filter_by(
                profile_name=data.get('profile_name'),
                drawing_name=data.get('drawing_name')
            ).first()

            new_score = int(data.get('score', 0))

            if existing_entry:
                existing_entry.score = new_score
                db.session.commit()
                return {'message': 'Score updated successfully'}, 200

            entry = LeaderboardEntry(
                profile_name=data.get('profile_name'),
                drawing_name=data.get('drawing_name'),
                score=new_score
            )
            
            if entry.create():
                return {'message': 'New entry created'}, 201
            return {'message': 'Failed to create entry'}, 400

        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def delete(self):
        """Delete a leaderboard entry"""
        try:
            data = request.get_json()
            if not data:
                return {'message': 'No data provided'}, 400

            profile_name = data.get('profile_name')
            drawing_name = data.get('drawing_name')

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


# Add the resource to the API
api = Api(leaderboard_api)
api.add_resource(_LeaderboardCRUD, '/api/leaderboard/crud')


@leaderboard_api.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        entries = LeaderboardEntry.query.order_by(
            LeaderboardEntry.score.desc()
        ).all()
        return jsonify([entry.read() for entry in entries]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@leaderboard_api.route('/api/leaderboard', methods=['POST'])
def add_leaderboard_entry():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        entry = LeaderboardEntry(
            profile_name=data.get('profile_name'),
            drawing_name=data.get('drawing_name'),
            score=int(data.get('score', 0))
        )
        
        if entry.create():
            return jsonify({"message": "Entry added successfully"}), 201
        return jsonify({"error": "Failed to add entry"}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@leaderboard_api.route('/api/leaderboard', methods=['PUT'])
def update_leaderboard_entry():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Find existing entry
        existing_entry = LeaderboardEntry.query.filter_by(
            profile_name=data.get('profile_name'),
            drawing_name=data.get('drawing_name')
        ).first()

        new_score = int(data.get('score', 0))

        # If entry exists, update it regardless of score
        if existing_entry:
            existing_entry.score = new_score  # Always update score
            db.session.commit()
            return jsonify({"message": "Score updated successfully"}), 200

        # If no existing entry, create new one
        entry = LeaderboardEntry(
            profile_name=data.get('profile_name'),
            drawing_name=data.get('drawing_name'),
            score=new_score
        )
        
        if entry.create():
            return jsonify({"message": "New entry created"}), 201
        return jsonify({"error": "Failed to create entry"}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@leaderboard_api.route('/api/leaderboard', methods=['DELETE'])
def delete_entry():
    try:
        # Try to get data from JSON body
        data = request.get_json()
        
        # Get profile_name and drawing_name from either JSON body or URL parameters
        profile_name = data.get('profile_name') if data else None
        drawing_name = data.get('drawing_name') if data else None

        # Validate input
        if not profile_name or not drawing_name:
            return jsonify({"error": "Missing profile_name or drawing_name"}), 400

        # Find and delete entry
        entry = LeaderboardEntry.query.filter_by(
            profile_name=profile_name,
            drawing_name=drawing_name
        ).first()

        if not entry:
            return jsonify({"error": "Entry not found"}), 404

        entry.delete()
        return jsonify({"message": "Entry deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@leaderboard_api.route('/api/leaderboard/list', methods=['GET'])
def list_entries():
    """Return all leaderboard entries as a list"""
    try:
        entries = LeaderboardEntry.list_all()
        return jsonify({
            "message": "Entries retrieved successfully",
            "entries": entries
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

