from flask import Blueprint, request, jsonify, g
from flask_restful import Api, Resource
from api.jwt_authorize import token_required
from model.flashcard import Flashcard

flashcard_api = Blueprint('flashcard_api', __name__, url_prefix='/api')
api = Api(flashcard_api)

class FlashcardAPI:
    class _CRUD(Resource):
        @token_required()
        def post(self):
            current_user = g.current_user
            data = request.get_json()
            if not data or 'title' not in data or 'content' not in data:
                return {'message': 'Title and content are required'}, 400
            flashcard = Flashcard(data['title'], data['content'], current_user.id)
            flashcard = flashcard.create()
            if not flashcard:
                return {'message': 'Failed to create flashcard'}, 400
            return jsonify(flashcard.read())

        @token_required()
        def get(self):
            current_user = g.current_user
            flashcards = Flashcard.query.filter_by(_user_id=current_user.id).all()
            return jsonify([flashcard.read() for flashcard in flashcards])

        @token_required()
        def put(self):
            data = request.get_json()
            if not data or 'id' not in data:
                return {'message': 'Flashcard ID is required'}, 400
            flashcard = Flashcard.query.get(data['id'])
            if not flashcard or flashcard._user_id != g.current_user.id:
                return {'message': 'Flashcard not found or unauthorized'}, 404
            flashcard.update(data)
            return jsonify(flashcard.read())

        @token_required()
        def delete(self):
            data = request.get_json()
            if not data or 'id' not in data:
                return {'message': 'Flashcard ID is required'}, 400
            flashcard = Flashcard.query.get(data['id'])
            if not flashcard or flashcard._user_id != g.current_user.id:
                return {'message': 'Flashcard not found or unauthorized'}, 404
            flashcard.delete()
            return {'message': 'Flashcard deleted'}, 200

api.add_resource(FlashcardAPI._CRUD, '/flashcard')