from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime
from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        # Get all messages ordered by created_at in ascending order
        messages = Message.query.order_by(Message.created_at.asc()).all()
        response = make_response(jsonify([message.to_dict() for message in messages]), 200)
    elif request.method == 'POST':
        # Get data from the JSON body
        data = request.get_json()
        # Ensure required fields are present in the request
        if not data.get('body') or not data.get('username'):
            return make_response(jsonify({"error": "Missing required fields"}), 400)
        
        # Create a new message
        new_message = Message(
            body=data["body"],
            username=data["username"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.session.add(new_message)
        db.session.commit()
        # Respond with the newly created message as JSON
        message_dict = new_message.to_dict()
        response = make_response(jsonify(message_dict), 201)
    
    return response

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.get(id)
    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404)
    
    if request.method == 'PATCH':
        # Get the data from the JSON body
        data = request.get_json()
        # Update only the fields provided in the request
        for key, value in data.items():
            setattr(message, key, value)
        db.session.commit()
        # Respond with the updated message as JSON
        return make_response(jsonify(message.to_dict()), 200)

    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        # Respond with a success message
        return make_response(jsonify({'message': 'Message deleted'}), 200)

if __name__ == '__main__':
    app.run(port=5555)
