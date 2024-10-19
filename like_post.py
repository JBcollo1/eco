from flask import jsonify, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Like, Post, Profile, User

class LikePost(Resource):
    @jwt_required()
    def post(self, post_id):
        user = get_jwt_identity()
        user_id = user.get('id') if isinstance(user, dict) else user

        post = Post.query.get(post_id)
        if not post:
            return {"message": "Post not found"}, 404
        
        # Check if the post is already liked by the user
        existing_like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
        if existing_like:
            return {"message": "Post has already been liked"}, 400
        
        # Create a new like
        new_like = Like(post_id=post_id, user_id=user_id)
        db.session.add(new_like)
        db.session.commit()

        return {"message": "Post liked successfully"}, 201

    @jwt_required()
    def delete(self, post_id):
        user = get_jwt_identity()
        user_id = user.get('id') if isinstance(user, dict) else user

        post = Post.query.get(post_id)
        if not post:
            return {"message": "Post not found"}, 404
        
        # Check if the like exists
        like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
        if not like:
            return {'message': 'Like not found'}, 404
        
        # Delete the like
        db.session.delete(like)
        db.session.commit()

        return {'message': 'Like removed successfully'}, 200
    @jwt_required()
    def get(self, post_id):
        user = get_jwt_identity()
        user_id = user.get('id') if isinstance(user, dict) else user

        post = Post.query.get(post_id)
        if not post:
            return {"message": "Post not found"}, 404
        
        # Check if the post is liked by the user
        like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
        
        return {"liked": bool(like)}, 200


class GetLikedPosts(Resource):
    @jwt_required()
    def get(self):
        user = get_jwt_identity()
        user_id = user.get('id') if isinstance(user, dict) else user

        # Query for all likes by the user
        likes = Like.query.filter_by(user_id=user_id).all()

        liked_posts = []
        for like in likes:
            post = Post.query.get(like.post_id)  # Individual query for each post
            if post:
                post_dict = post.as_dict()
                profile = Profile.query.filter_by(user_id=post.user_id).first()  # Individual query for each profile
                if profile:
                    post_dict['profile_picture'] = profile.profile_picture
                
                user = User.query.get(post.user_id)  # Individual query for each user
                if user:
                    post_dict['username'] = user.user_name
                liked_posts.append(post_dict)

        return liked_posts, 200
