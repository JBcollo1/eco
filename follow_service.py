from models import db, User, Follow
from sqlalchemy.exc import IntegrityError

def follow_user(follower_id, followed_id):
    """
    Make a user follow another user.
    
    :param follower_id: ID of the user who wants to follow
    :param followed_id: ID of the user to be followed
    :return: tuple (success, message)
    """
    if follower_id == followed_id:
        return False, "Users cannot follow themselves."

    follower = User.query.get(follower_id)
    followed = User.query.get(followed_id)

    if not follower or not followed:
        return False, "One or both users not found."

    if follower.is_following(followed):
        return False, f"{follower.user_name} is already following {followed.user_name}."

    try:
        follower.follow(followed)
        db.session.commit()
        return True, f"{follower.user_name} is now following {followed.user_name}."
    except IntegrityError:
        db.session.rollback()
        return False, "An error occurred while trying to follow the user."

def unfollow_user(follower_id, followed_id):
    """
    Make a user unfollow another user.
    
    :param follower_id: ID of the user who wants to unfollow
    :param followed_id: ID of the user to be unfollowed
    :return: tuple (success, message)
    """
    if follower_id == followed_id:
        return False, "Users cannot unfollow themselves."

    follower = User.query.get(follower_id)
    followed = User.query.get(followed_id)

    if not follower or not followed:
        return False, "One or both users not found."

    if not follower.is_following(followed):
        return False, f"{follower.user_name} is not following {followed.user_name}."

    try:
        follower.unfollow(followed)
        db.session.commit()
        return True, f"{follower.user_name} has unfollowed {followed.user_name}."
    except IntegrityError:
        db.session.rollback()
        return False, "An error occurred while trying to unfollow the user."

def get_follow_status(follower_id, followed_id):
    """
    Check if one user is following another.
    
    :param follower_id: ID of the potential follower
    :param followed_id: ID of the potentially followed user
    :return: tuple (is_following, message)
    """
    follower = User.query.get(follower_id)
    followed = User.query.get(followed_id)

    if not follower or not followed:
        return False, "One or both users not found."

    is_following = follower.is_following(followed)
    message = f"{follower.user_name} {'is' if is_following else 'is not'} following {followed.user_name}."
    return is_following, message

def get_follower_count(user_id):
    """
    Get the number of followers for a user.
    
    :param user_id: ID of the user
    :return: tuple (count, message)
    """
    user = User.query.get(user_id)
    if not user:
        return 0, "User not found."
    
    count = user.followers.count()
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
