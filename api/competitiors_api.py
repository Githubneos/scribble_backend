from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask import Blueprint, request, jsonify, g
from api.jwt_authorize import token_required
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
competitors_api = Blueprint('competitors_api', __name__)
CORS(app)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///competitions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Competitor_Status model
class Competitor_Status(db.Model):
    id = db.Column(db.String, primary_key=True)
    timer = db.Column(db.Integer)
    user_drawings = db.Column(db.PickleType)

# Create the database and tables
with app.app_context():
    db.create_all()

class Competitors(Resource):
    def get(self, competitors_id):
        competitors = Competitor_Status.query.get(competitors_id)
        if competitors:
            return jsonify({
                "id": competitors.id,
                "timer": competitors.timer,
                "user_drawings": competitors.user_drawings
            })
        return jsonify({"message": "Competitors not found"}), 404

    def post(self):
        data = request.get_json()
        competitors_id = data.get('id')
        if Competitor_Status.query.get(competitors_id):
            return jsonify({"message": "Competitors already exists"}), 400
        
        competitors = Competitor_Status(
            id=competitors_id,
            timer=data.get('timer'),
            user_drawings=data.get('user_drawings', [])
        )
        db.session.add(competitors)
        db.session.commit()
        return jsonify({"message": "Competitors created successfully"}), 201

    def put(self, competitors_id):
        data = request.get_json()
        competitors = Competitor_Status.query.get(competitors_id)
        if not competitors:
            return jsonify({"message": "Competitors not found"}), 404
        
        competitors.timer = data.get('timer', competitors.timer)
        competitors.user_drawings = data.get('user_drawings', competitors.user_drawings)
        db.session.commit()
        return jsonify({"message": "Competitors updated successfully"})

    def delete(self, competitors_id):
        competitors = Competitor_Status.query.get(competitors_id)
        if competitors:
            db.session.delete(competitors)
            db.session.commit()
            return jsonify({"message": "Competitors deleted successfully"})
        return jsonify({"message": "Competitors not found"}), 404

api = Api(competitors_api)
api.add_resource(Competitors, '/competitors', '/competitors/<string:competitors_id>')

app.register_blueprint(competitors_api, url_prefix='/api')

if __name__ == '__main__':
    port = int(os.environ.get("FLASK_RUN_PORT", 4887))
    app.run(host="0.0.0.0", port=port, debug=True)