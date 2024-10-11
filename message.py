from flask_restful import Resource
from models import db, User, Message
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity





def send_message(sender_id, recipient_id, content):
    sender = User.query.get(sender_id)
    recipient = User.query.get(recipient_id)
    
    if not recipient:
        return {'message': 'Recipient not found.'}, 404

    # Create a new message
    message = Message(sender_id=sender_id, recipient_id=recipient_id, content=content)
    db.session.add(message)
    db.session.commit()
    
    return {'message': f'Message sent to {recipient.user_name}'}

def get_messages(user_id):
    messages = Message.query.filter_by(recipient_id=user_id).all()
    if messages:
        return [{'sender': User.query.get(message.sender_id).user_name, 'content': message.content, 'timestamp': message.timestamp} for message in messages]
    else:
        return {'message': 'No messages found.'}


class SendMessage(Resource):
    @jwt_required()
    def post(self, recipient_id):
        # Get the current user (sender) ID from JWT
        current_user_id = get_jwt_identity()
        
        # Extract the message content from the request body
        data = request.get_json()
        content = data.get('content')
        
        if not content:
            return {'message': 'Message content is required.'}, 400
        
        # Send the message
        response = send_message(current_user_id, recipient_id, content)
        return response

class GetMessages(Resource):
    @jwt_required()
    def get(self):
        # Get the current user ID from JWT
        current_user_id = get_jwt_identity()
        
        # Retrieve messages sent to the current user
        response = get_messages(current_user_id)
        return response
