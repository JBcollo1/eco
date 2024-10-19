from flask_restful import Resource
from models import db, User, Message
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity



# Function to send a message
def send_message(sender_id, recipient_id, content):
    sender = User.query.get(sender_id)
    recipient = User.query.get(recipient_id)

    if not recipient:
        return {'message': 'Recipient not found.'}, 404

    # Create a new message
    message = Message(sender_id=sender_id, recipient_id=recipient_id, content=content)
    db.session.add(message)
    db.session.commit()

    return {'message': f'Message sent to {recipient.user_name}'}, 200


# Function to get all messages between two users (conversation)
def get_conversation(user_id, recipient_id):
    messages = Message.query.filter(
        ((Message.sender_id == user_id) & (Message.recipient_id == recipient_id)) | 
        ((Message.sender_id == recipient_id) & (Message.recipient_id == user_id))
    ).order_by(Message.timestamp.asc()).all()

    if messages:
        return [
            {'sender': User.query.get(message.sender_id).user_name, 
             'content': message.content, 
             'timestamp': message.timestamp} 
            for message in messages
        ]
    else:
        return {'message': 'No conversation found.'}, 404


# API resource for sending a message
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


# API resource for retrieving conversation messages between two users
class GetConversation(Resource):
    @jwt_required()
    def get(self, recipient_id):
        # Get the current user ID from JWT
        current_user_id = get_jwt_identity()

        # Retrieve the conversation messages between the current user and the recipient
        response = get_conversation(current_user_id, recipient_id)
        return response


# Add resources to API routes

