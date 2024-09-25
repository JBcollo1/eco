from flask_restful import Resource
from flask import request, jsonify, current_app
from models import Profile, db
import cloudinary.uploader  # Import the Cloudinary uploader
from flask_jwt_extended import jwt_required

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class UserProfile(Resource):
    @jwt_required()
    def post(self):
        data = request.form
        user_id = data.get('user_id')
        bio = data.get('bio')
        location = data.get('location')
        date_of_birth = data.get('DOB')
        profile_picture = request.files.get('profile_picture')

        profile = Profile.query.filter_by(user_id=user_id).first()

        profile_picture_url = None
        if profile_picture and allowed_file(profile_picture.filename):
            # Upload profile picture to Cloudinary
            cloudinary_response = cloudinary.uploader.upload(profile_picture)
            profile_picture_url = cloudinary_response['secure_url']  # Get the secure URL of the uploaded image

        if profile:
            profile.bio = bio
            profile.location = location
            profile.date_of_birth = date_of_birth
            if profile_picture_url:
                profile.profile_picture = profile_picture_url
        else:
            profile = Profile(
                user_id=user_id,
                bio=bio,
                location=location,
                date_of_birth=date_of_birth,
                profile_picture=profile_picture_url
            )
            db.session.add(profile)

        db.session.commit()
        return jsonify({"message": "Profile saved successfully!"}), 200

    @jwt_required()
    def get(self, user_id):
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({"message": "Profile not found"}), 404
        return jsonify(profile.as_dict()), 200

    @jwt_required()
    def delete(self, user_id):
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({"message": "Profile not found"}), 404

        db.session.delete(profile)
        db.session.commit()
        return jsonify({"message": "Profile deleted successfully!"}), 200

    @jwt_required()
    def patch(self, user_id):
        data = request.form
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({'message': 'Profile not found'}), 404

        if 'bio' in data:
            profile.bio = data['bio']
        if 'location' in data:
            profile.location = data['location']
        if 'date_of_birth' in data:
            profile.date_of_birth = data['date_of_birth']

        profile_picture = request.files.get('profile_picture')
        if profile_picture and allowed_file(profile_picture.filename):
            # Upload new profile picture to Cloudinary
            cloudinary_response = cloudinary.uploader.upload(profile_picture)
            profile.profile_picture = cloudinary_response['secure_url']  # Update the profile picture URL

        db.session.commit()
        return jsonify({'message': 'Profile updated successfully', 'profile': profile.as_dict()}), 200
