from flask import jsonify, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Like, Post


class LikePost(Resource):
    @jwt_required
    def post(self, post_id):
        user_id = get_jwt_identity

        post =Post.query.get(post_id)
        if not post:
            return jsonify({"message":"Post not found "}), 404
        
        existing_like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
        if existing_like:
            return jsonify({"message":"Post has already been liked"}), 400
        
        new_like = Like(post_id=post_id, user_id=user_id)

        db.session.add(new_like)
        db.session.commit()

        return jsonify({"message":"Post liked successfully"})
    @jwt_required
    def delete(self, post_id):
        user_id = get_jwt_identity

        post =Post.query.get(post_id)
        if not post:
            return jsonify({"message":"Post not found "}), 404
        like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
        if not like:
            return jsonify({'message': 'Like not found'}), 404
        
        db.session.delete()
        db.session.commit()

        return jsonify({'message': 'Like removed successfully'}), 200
        