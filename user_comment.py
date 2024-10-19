from flask import request, jsonify
from flask_restful import Resource
from models import db, Comment, Post
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

class AddComment(Resource):
    @jwt_required()
    def post(self, post_id):
        content = request.json.get('comment')
        user = get_jwt_identity()

        if not content:
            return {"message": "Content required"}, 400
        
        post = Post.query.get(post_id)
        if not post:
            return {'message': 'Post not available'}, 404
        
        # Create and add comment
        comment = Comment(content=content,created_at=datetime.utcnow(),  post_id=post_id, user_id=user['id'])
        db.session.add(comment)
        db.session.commit()

        return {"message": "Comment added successfully", "comment": comment.as_dict()}, 201


class GetComments(Resource):
    @jwt_required()
    def get(self, post_id):
        post = Post.query.get(post_id)
        if not post:
            return {"message": "Post not found"}, 404

        comments = Comment.query.filter_by(post_id=post_id).all()
        comments_list = []
        for comment in comments:
            comments_list.append({
                "id": comment.id,
                "content": comment.content,
                "created_at":  comment.created_at.isoformat() if comment.created_at else None,
                "user_id": comment.user_id
                # Add other fields as needed
            })
        return comments_list

class UpdateComment(Resource):
    @jwt_required()
    def patch(self, comment_id):
        comment = Comment.query.get(comment_id)
        if not comment:
            return {"message": "Comment not found"}, 404

        user_id = get_jwt_identity()
        if comment.user_id != user_id:
            return {"message": "Not authorized to update this comment"}, 403

        content = request.json.get("content")
        if content:
            comment.content = content
            db.session.commit()

        return comment.as_dict(), 200


class DeleteComment(Resource):
    @jwt_required()
    def delete(self, comment_id):
        comment = Comment.query.get(comment_id)
        if not comment:
            return {"message": "Comment not found"}, 404

        user_id = get_jwt_identity()
        if comment.user_id != user_id:
            return {"message": "Not authorized to delete this comment"}, 403

        db.session.delete(comment)
        db.session.commit()

        return jsonify({"message": "Comment deleted successfully"}), 200


class GetAllComments(Resource):
    @jwt_required()
    def get(self):
        comments = Comment.query.all()
        return jsonify([comment.as_dict() for comment in comments]), 200
