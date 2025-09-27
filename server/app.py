from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

@app.route('/messages', methods=['GET'])
def messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([m.to_dict() for m in messages]), 200

@app.route('/messages/<int:id>', methods=['GET'])
def message_by_id(id):
    message = Message.query.get_or_404(id)
    return jsonify(message.to_dict()), 200


@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    new_msg = Message(
        body=data.get('body'),
        username=data.get('username'),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(new_msg)
    db.session.commit()
    return jsonify(new_msg.to_dict()), 201

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get_or_404(id)
    data = request.get_json()
    if 'body' in data:
        message.body = data['body']
    if 'username' in data:
        message.username = data['username']
    message.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(message.to_dict()), 200


@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    app.run(port=5555, debug=True)


