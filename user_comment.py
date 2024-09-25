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

