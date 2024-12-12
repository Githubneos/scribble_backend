import jwt
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from __init__ import app
from api.jwt_authorize import token_required

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comment_api.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    comments = db.relationship('Comment', backref='author', lazy=True)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    comments = db.relationship('Comment', backref='image', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), nullable=False)

# Routes
@app.route('/images', methods=['POST'])
def upload_image():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': 'Image URL is required'}), 400

    image = Image(url=url)
    db.session.add(image)
    db.session.commit()
    return jsonify({'message': 'Image uploaded successfully', 'image': {'id': image.id, 'url': image.url}}), 201

@app.route('/images', methods=['GET'])
def get_images():
    images = Image.query.all()
    return jsonify([{'id': img.id, 'url': img.url} for img in images])

@app.route('/images/<int:image_id>/comments', methods=['POST'])
def add_comment(image_id):
    data = request.json
    content = data.get('content')
    user_id = data.get('user_id')

    if not content or not user_id:
        return jsonify({'error': 'Content and user_id are required'}), 400

    image = Image.query.get(image_id)
    if not image:
        return jsonify({'error': 'Image not found'}), 404

    comment = Comment(content=content, user_id=user_id, image_id=image_id)
    db.session.add(comment)
    db.session.commit()
    return jsonify({'message': 'Comment added successfully', 'comment': {'id': comment.id, 'content': comment.content}}), 201

@app.route('/images/<int:image_id>', methods=['GET'])
def get_image_details(image_id):
    image = Image.query.get(image_id)
    if not image:
        return jsonify({'error': 'Image not found'}), 404

    comments = [{'id': c.id, 'content': c.content, 'user_id': c.user_id} for c in image.comments]
    return jsonify({'id': image.id, 'url': image.url, 'comments': comments})

@app.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404

    db.session.delete(comment)
    db.session.commit()
    return jsonify({'message': 'Comment deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
