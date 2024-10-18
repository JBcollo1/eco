from flask import request, jsonify
from flask_restful import Resource
from models import db, Post, Profile
from flask_jwt_extended import jwt_required, get_jwt_identity
import cloudinary.uploader  # Import the Cloudinary uploader

class Upload(Resource):
    @jwt_required()
    def post(self, user_id):
        # Extract content from the request
        content = request.form.get('content')
        # Fetch the current user's ID from the JWT token
        current_user_id = get_jwt_identity()

        if isinstance(current_user_id, dict):
            current_user_id = current_user_id.get('id')
        # Fetch the user's profile from the database
        user_profile = Profile.query.filter_by(user_id=current_user_id).first()
        
        if not user_profile:
            return {'message': 'User profile not found'}, 404
        
        profile_id = user_profile.id

        # Ensure the current user matches the requested user_id
        if int(user_id) != current_user_id:
            return {'message': 'Unauthorized'}, 403
       

        # Initialize photo and video URLs
        photo_url = None
        video_url = None

        try:
            # Check for photo uploads
            if 'photo' in request.files:
                photo = request.files['photo']
                cloudinary_response = cloudinary.uploader.upload(photo)
                photo_url = cloudinary_response['secure_url']

            # Check for video uploads
            if 'video' in request.files:
                video = request.files['video']
                cloudinary_response = cloudinary.uploader.upload(video, resource_type='video')
                video_url = cloudinary_response['secure_url']

            # Create a Post instance with the provided content and user_id
            new_post = Post(content=content, user_id=user_id, image_url=photo_url, video_url=video_url, profile_id=profile_id)

            # Save the post to the database
            db.session.add(new_post)
            db.session.commit()

            response_data = {
                'message': 'Post created successfully',
                'post_id': new_post.id,
                'content': new_post.content,
                'photo_url': photo_url,
                'video_url': video_url,
                'created_at': new_post.created_at.isoformat()
            }

            return response_data, 201

        except Exception as e:
            return {'message': str(e)}, 500  

    @jwt_required()
    def patch(self, post_id):
        """Update a post by ID."""
        post = Post.query.get(post_id)
        if not post:
            return jsonify({'message': 'Post not found'}), 404
        
        # Get the current user's id from the JWT token
        current_user_id = get_jwt_identity()

        # Check if the current user is the owner of the post
        if post.user_id != current_user_id:
            return jsonify({'message': 'You do not have permission to edit this post'}), 403

        content = request.form.get('content')  # Get new content if provided
        if content:
            post.content = content  # Update content

        # Handle photo uploads (if a new photo is being added)
        if 'photo' in request.files:
            photo = request.files['photo']
            # Upload photo to Cloudinary
            cloudinary_response = cloudinary.uploader.upload(photo)
            post.image_url = cloudinary_response['secure_url']  # Save the photo URL in the post model

        # Handle video uploads (if a new video is being added)
        if 'video' in request.files:
            video = request.files['video']
            # Upload video to Cloudinary
            cloudinary_response = cloudinary.uploader.upload(video, resource_type='video')
            post.video_url = cloudinary_response['secure_url']  # Save the video URL in the post model

        db.session.commit()  
        return jsonify({'message': 'Post updated successfully'}), 200

    @jwt_required()
    def delete(self, post_id):
        """Delete a post by ID."""
        post = Post.query.get(post_id)
        if not post:
            return jsonify({'message': 'Post not found'}), 404

        current_user_id = get_jwt_identity()
        if post.user_id != current_user_id:
            return jsonify({'message': 'You do not have permission to delete this post'}), 403

        db.session.delete(post)  # Delete the post
        db.session.commit()  # Commit the deletion
        return jsonify({'message': 'Post deleted successfully'}), 200

    @jwt_required()
    def get(self, post_id):
        """Retrieve a post by ID."""
        post = Post.query.get(post_id)
        if not post:
            return jsonify({'message': 'Post not found'}), 404

        return jsonify(post.as_dict()), 200

class PostListResource(Resource):
    @jwt_required()
    def get(self):
        """Retrieve a paginated list of posts."""
        page = request.args.get('page', 1, type=int)  
        per_page = request.args.get('per_page', 1, type=int)  

        posts = Post.query.paginate(page=page, per_page=per_page, error_out=False)
        next_page = posts.page + 1 if posts.has_next else None
        prev_page = posts.page - 1 if posts.has_prev else None
        return {
            'posts': [post.as_dict() for post in posts.items],
            'total': posts.total,
            'page': posts.page,
            'per_page': posts.per_page,
            'next_page': next_page,
            'prev_page': prev_page,
            'has_next_page': posts.has_next,  # Indicate if more pages are available
            'has_prev_page': posts.has_prev
        }, 200
