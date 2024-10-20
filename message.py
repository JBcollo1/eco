from flask_restful import Resource, reqparse
from models import db, User, Message, Profile
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy import case, func



# Function to send a message
def send_message(sender_id, receiver_id, content):
    receiver = User.query.get('id')

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
        current_user = get_jwt_identity()
        sender_id = current_user.get('id') if isinstance(current_user, dict) else current_user

        parser = reqparse.RequestParser()
        parser.add_argument('content', type=str, required=True, help='Message content is required')
        args = parser.parse_args()

        new_message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=args['content']
        )

        db.session.add(new_message)
        db.session.commit()

        return {
            'message': 'Message sent successfully',
            'message_id': new_message.id
        }, 201


# API resource for retrieving conversation messages between two users
class GetConversation(Resource):
    @jwt_required()
    def get(self, receiver_id):
        current_user = get_jwt_identity()
        current_user_id = current_user.get('id') if isinstance(current_user, dict) else current_user

        # Fetch messages between current user and receiver
        messages = Message.query.filter(
            ((Message.sender_id == current_user_id) & (Message.receiver_id == receiver_id)) |
            ((Message.sender_id == receiver_id) & (Message.receiver_id == current_user_id))
        ).order_by(Message.created_at.asc()).all()

        conversation = []
        for message in messages:
            conversation.append({
                'id': message.id,
                'sender_id': message.sender_id,
                'receiver_id': message.receiver_id,
                'content': message.content,
                'timestamp': message.created_at.isoformat(),
                'is_read': message.is_read
            })

        # Mark messages as read
        unread_messages = Message.query.filter(
            Message.receiver_id == current_user_id,
            Message.sender_id == receiver_id,
            Message.is_read == False
        ).all()
        for message in unread_messages:
            message.is_read = True
        db.session.commit()

        return conversation, 200




# API resource for retrieving a list of conversations for the current user
class GetConversationList(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        current_user_id = current_user.get('id') if isinstance(current_user, dict) else current_user

        # Subquery to get the latest message for each conversation
        latest_messages = db.session.query(
            db.func.max(Message.id).label('max_id')
        ).group_by(
            case(
                (Message.sender_id < Message.receiver_id, Message.sender_id),
                else_=Message.receiver_id
            ),
            case(
                (Message.sender_id > Message.receiver_id, Message.sender_id),
                else_=Message.receiver_id
            )
        ).subquery()

        # Query to get the conversations with the latest message
        conversations = db.session.query(Message).join(
            latest_messages,
            Message.id == latest_messages.c.max_id
        ).filter(
            (Message.sender_id == current_user_id) | (Message.receiver_id == current_user_id)
        ).order_by(Message.created_at.desc()).all()

        conversation_list = []
        for conversation in conversations:
            other_user_id = conversation.receiver_id if conversation.sender_id == current_user_id else conversation.sender_id
            other_user = User.query.get(other_user_id)
            
            # Count unread messages for this conversation
            unread_count = Message.query.filter(
                Message.sender_id == other_user_id,
                Message.receiver_id == current_user_id,
                Message.is_read == False
            ).count()
            
            conversation_list.append({
                'user_id': other_user_id,
                'username': other_user.user_name,
                'last_message': conversation.content,
                'timestamp': conversation.created_at.isoformat(),
                'is_read': conversation.is_read,
                'unread_count': unread_count
            })

        return conversation_list, 200


class GetUserList(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        current_user_id = current_user.get('id') if isinstance(current_user, dict) else current_user

        # Query all users except the current user
        users = User.query.filter(User.id != current_user_id).all()

        user_list = []
        for user in users:
            profile = Profile.query.filter(Profile.user_id == user.id).first()
            user_list.append({
                'user_id': user.id,
                'username': user.user_name,
                'profile_picture': profile.profile_picture if profile else None,
                # Add any other user information you want to include
            })

        if not user_list:
            return {'message': 'No other users found.'}, 204  # 204 No Content

        return user_list, 200
