from flask_restful import Resource
from models import db, User, Message
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime



# Function to send a message
def send_message(sender_id, receiver_id, content):
    receiver = User.query.get(receiver_id)

    if not receiver:
        return {'message': 'Receiver not found.'}, 404

    # Create a new message
    message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.session.add(message)
    db.session.commit()

    return {'message': f'Message sent to {receiver.user_name}'}, 200


# Function to get all messages between two users (conversation)
def get_conversation(user_id, receiver_id):
    messages = Message.query.filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == receiver_id)) | 
        ((Message.sender_id == receiver_id) & (Message.receiver_id == user_id))
    ).order_by(Message.created_at.asc()).all()

    if messages:
        # Mark messages as read
        for message in messages:
            if message.receiver_id == user_id and not message.is_read:
                message.is_read = True
        db.session.commit()

        return [message.as_dict() for message in messages]
    else:
        return {'message': 'No conversation found.'}, 404


# API resource for sending a message
class SendMessage(Resource):
    @jwt_required()
    def post(self, receiver_id):
        # Get the current user (sender) ID from JWT
        current_user_id = get_jwt_identity()

        # Extract the message content from the request body
        data = request.get_json()
        content = data.get('content')

        if not content:
            return {'message': 'Message content is required.'}, 400

        # Send the message
        response = send_message(current_user_id, receiver_id, content)
        return response


# API resource for retrieving conversation messages between two users
class GetConversation(Resource):
    @jwt_required()
    def get(self, receiver_id):
        # Get the current user ID from JWT
        current_user_id = get_jwt_identity()

        # Retrieve the conversation messages between the current user and the receiver
        response = get_conversation(current_user_id, receiver_id)
        return response




