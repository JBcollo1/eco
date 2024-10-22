from models import db, User, Follow
from sqlalchemy.exc import IntegrityError
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity

def follow_user(follower_id, followed_id):
    try:
        follower_id = int(follower_id)
        followed_id = int(followed_id)
    except ValueError:
        return False, "Invalid user IDs."

    if follower_id == followed_id:
        return False, "Users cannot follow themselves."

    follower = User.query.get(follower_id)
    followed = User.query.get(followed_id)

    if not follower or not followed:
        return False, "One or both users not found."

    if follower.is_following(followed):
        return False, f"{follower.user_name} is already following {followed.user_name}."

    try:
        new_follow = Follow(follower_id=follower_id, followed_id=followed_id)
        db.session.add(new_follow)
        db.session.commit()
        return True, f"{follower.user_name} is now following {followed.user_name}."
    except IntegrityError:
        db.session.rollback()
        return False, "An error occurred while trying to follow the user."

def unfollow_user(follower_id, followed_id):
    try:
        follower_id = int(follower_id)
        followed_id = int(followed_id)
    except ValueError:
        return False, "Invalid user IDs."

    if follower_id == followed_id:
        return False, "Users cannot unfollow themselves."

    follower = User.query.get(follower_id)
    followed = User.query.get(followed_id)

    if not follower or not followed:
        return False, "One or both users not found."

    follow = Follow.query.filter_by(follower_id=follower_id, followed_id=followed_id).first()
    if not follow:
        return False, f"{follower.user_name} is not following {followed.user_name}."

    try:
        db.session.delete(follow)
        db.session.commit()
        return True, f"{follower.user_name} has unfollowed {followed.user_name}."
    except IntegrityError:
        db.session.rollback()
        return False, "An error occurred while trying to unfollow the user."

def get_follow_status(follower_id, followed_id):
    try:
        follower_id = int(follower_id)
        followed_id = int(followed_id)
    except ValueError:
        return False, "Invalid user IDs."

    follower = User.query.get(follower_id)
    followed = User.query.get(followed_id)

    if not follower or not followed:
        return False, "One or both users not found."

    is_following = Follow.query.filter_by(follower_id=follower_id, followed_id=followed_id).first() is not None
    message = f"{follower.user_name} {'is' if is_following else 'is not'} following {followed.user_name}."
    return is_following, message

def get_follower_count(user_id):
    try:
        user_id = int(user_id)
    except ValueError:
        return 0, "Invalid user ID."

    user = User.query.get(user_id)
    if not user:
        return 0, "User not found."
    
    count = Follow.query.filter_by(followed_id=user_id).count()
    return count, f"{user.user_name} has {count} followers."

def get_following_count(user_id):
    """
    Get the number of users a user is following.
    
    :param user_id: ID of the user
    :return: tuple (count, message)
    """
    user = User.query.get(user_id)
    if not user:
        return 0, "User not found."
    
    count = user.following.count()
    return count, f"{user.user_name} is following {count} users."

class FollowUser(Resource):
    @jwt_required()
    def post(self, user_id):
        current_user = get_jwt_identity()
        current_user_id = current_user.get('id') if isinstance(current_user, dict) else current_user
        success, message = follow_user(current_user_id, user_id)
        return {"success": success, "message": message}, 200 if success else 400

class UnfollowUser(Resource):
    @jwt_required()
    def post(self, user_id):
        current_user = get_jwt_identity()
        current_user_id = current_user.get('id') if isinstance(current_user, dict) else current_user
        success, message = unfollow_user(current_user_id, user_id)
        return {"success": success, "message": message}, 200 if success else 400

class FollowStatus(Resource):
    @jwt_required()
    def get(self, user_id):
        current_user = get_jwt_identity()
        current_user_id = current_user.get('id') if isinstance(current_user, dict) else current_user
        is_following, message = get_follow_status(current_user_id, user_id)
        return {"is_following": is_following, "message": message}, 200

class FollowerCount(Resource):
    def get(self, user_id):
        count, message = get_follower_count(user_id)
        return {"count": count, "message": message}, 200

class FollowingCount(Resource):
    def get(self, user_id):
        count, message = get_following_count(user_id)
        return {"count": count, "message": message}, 200






