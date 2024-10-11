from flask_restful import Resource
from models import db, Follow, User
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

def follow_user(follower_id, followed_id):
    follower = User.query.get(follower_id)
    followed = User.query.get(followed_id)

    if not follower.is_following(followed):
        follower.follow(followed)
        db.session.commit()
        return {'message': f'You are now following {followed.user_name}'}
    else:
        return {'message': 'You are already following this user.'}, 400

def unfollow_user(follower_id, followed_id):
    follower = User.query.get(follower_id)
    followed = User.query.get(followed_id)

    if follower.is_following(followed):
        follower.unfollow(followed)
        db.session.commit()
        return {'message': f'You have unfollowed {followed.user_name}'}
    else:
        return {'message': 'You are not following this user.'}, 400

class FollowUser(Resource):
    @jwt_required()  # This ensures that only authenticated users can access this endpoint
    def post(self, user_id):
        # Get current user ID from the JWT token
        current_user_id = get_jwt_identity()  
        response = follow_user(current_user_id, user_id)
        return response

class UnfollowUser(Resource):
    @jwt_required()  # Ensures that only authenticated users can access this endpoint
    def post(self, user_id):
        # Get current user ID from the JWT token
        current_user_id = get_jwt_identity()
        response = unfollow_user(current_user_id, user_id)
        return response
