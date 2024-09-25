from flask import request, jsonify
from flask_restful import Resource
from models import db, Comment, Post
from flask_jwt_extended import jwt_required, get_jwt_identity

class AddComment(Resource):
    @jwt_required
    def post(self, post_id):
        content = request.json.get('content')
        user_id = get_jwt_identity()

        if not content:
            return jsonify ({"message":"content required"}), 400
        post = Post.query.get(post_id)
        if not post:
            return jsonify ({'message':'post is not available'})
        comment = Comment()

class GetComments(Resource):
    @jwt_required
    def get(self, post_id):
        post = Post.query.get(post_id)
        if not post :
            return jsonify({"message":"post not found"})
        comments = Comment.query.filter_by(post_id = post_id).all()
        return jsonify([comment.as_dict() for comment in comments]), 200
    

class UpdateComment(Resource):
    @jwt_required
    def patch(self, comment_id):
        comment = Comment.query.get(comment_id)
        if not comment :
            return jsonify({"message":"Comment not found"}), 404
        user_id = get_jwt_identity()
        if comment.user_id != user_id:
            return jsonify({"message":"Not authorised"}), 403
        content = request.json.get("content")
        if content:
            comment.content = content
            db.session.commit()
        return jsonify(comment.as_dict()), 200
    
class DeleteComment(Resource):
    @jwt_required
    def delete(self, comment_id):
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({"message":"Comment not found"}), 404
        user_id = get_jwt_identity()
        if comment.user_id != user_id:
            return jsonify ({"mesasage":"Not authorised"}), 403
        
        db.session.delete(comment)
        db.session.commit()

        return jsonify ({"message": "Comment deleted"})
        

        


