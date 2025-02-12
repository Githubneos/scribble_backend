from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
from flask import Blueprint, request, jsonify, g
from flask_cors import CORS
import os
from __init__ import db
from model.statistics_hiroshi import Stats
from api.jwt_authorize import token_required

# Initialize a Flask application
app = Flask(__name__)
CORS(app)
# It's better to specify allowed origins explicitly rather than using '*'

stats_api = Blueprint('stats_api', __name__, url_prefix='/api')
api = Api(stats_api)

class StatisticsAPI:
    """
    Define the API CRUD endpoints for the Statistics model.
    All endpoints require JWT token authentication.
    """
    class _CRUD(Resource):
        @token_required
        def post(self, current_user):
            """Create or update user statistics"""
            try:
                data = request.get_json()
                
                if not data or 'username' not in data:
                    return {'message': 'Username required'}, 400

                stats = Stats.query.filter_by(user_name=data['username']).first()
                if not stats:
                    stats = Stats(
                        user_name=data['username'],
                        correct_guesses=int(data.get('correct', 0)),
                        wrong_guesses=int(data.get('wrong', 0)),
                        total_rounds=1
                    )
                    db.session.add(stats)
                else:
                    stats.correct_guesses += int(data.get('correct', 0))
                    stats.wrong_guesses += int(data.get('wrong', 0))
                    stats.total_rounds += 1

                db.session.commit()
                return {'message': 'Statistics updated successfully'}, 200

            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}, 500

        @token_required
        def get(self, current_user):
            """Get statistics for a specific user"""
            try:
                data = request.get_json()
                if not data or 'username' not in data:
                    return {'message': 'Username required'}, 400

                stats = Stats.query.filter_by(user_name=data['username']).first()
                if not stats:
                    return {
                        'username': data['username'],
                        'correct_guesses': 0,
                        'wrong_guesses': 0,
                        'total_rounds': 0
                    }, 200

                return stats.read(), 200
            except Exception as e:
                return {'error': str(e)}, 500

        @token_required
        def delete(self, current_user):
            """Delete user statistics"""
            try:
                data = request.get_json()
                if not data or 'username' not in data:
                    return {'message': 'Username required'}, 400

                stats = Stats.query.filter_by(user_name=data['username']).first()
                if not stats:
                    return {'message': 'User not found'}, 404

                db.session.delete(stats)
                db.session.commit()
                return {'message': 'Statistics deleted successfully'}, 200

            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}, 500

    class _List(Resource):
        @token_required
        def get(self, current_user):
            """Get all users' statistics"""
            try:
                all_stats = Stats.query.all()
                stats_list = [stat.read() for stat in all_stats]
                return jsonify({
                    'message': 'Statistics retrieved successfully',
                    'data': stats_list
                }), 200
            except Exception as e:
                return {'error': str(e)}, 500

    # Register API endpoints
    api.add_resource(_CRUD, '/statistics')
    api.add_resource(_List, '/statistics/all')

