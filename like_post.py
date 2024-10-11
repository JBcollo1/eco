from flask import jsonify, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Like, Post

class LikePost(Resource):
    @jwt_required()
    def post(self, post_id):
        user_id = get_jwt_identity()

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
        user_id = get_jwt_identity()

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
