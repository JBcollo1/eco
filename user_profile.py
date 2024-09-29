from flask_restful import Resource
from flask import request, jsonify, current_app
from models import Profile, db
import cloudinary.uploader  # Import the Cloudinary uploader
from flask_jwt_extended import jwt_required
import logging
from datetime import datetime


logging.basicConfig(level=logging.DEBUG)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class UserProfile(Resource):
    @jwt_required()
    def post(self, user_id):
        try:
            data = request.form
            logging.debug(f"Received data: {data}")
            # user_id = data.get('user_id')
            bio = data.get('bio')
            location = data.get('location')
            date_str = data.get('DOB')
            profile_picture = request.files.get('profile_picture')

            profile = Profile.query.filter_by(user_id=user_id).first()

            try:
                date_of_birth = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                logging.error(f"Invalid date format: {date_str}")
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400


            profile_picture_url = None
            if profile_picture and allowed_file(profile_picture.filename):
                logging.debug(f"Profile picture received: {profile_picture.filename}")
                try:
                    # Upload profile picture to Cloudinary
                    cloudinary_response = cloudinary.uploader.upload(profile_picture)
                    logging.debug(f"Cloudinary response: {cloudinary_response}")
                    profile_picture_url = cloudinary_response['secure_url']
                except Exception as e:
                    return {"error": "Failed to upload image", "details": str(e)}, 500

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
            return {"message": "Profile saved successfully!"}, 200

        except Exception as e:
            logging.error(f"Error occurred: {str(e)}")
            return {"error": "Failed to save profile", "details": str(e)}, 500

    @jwt_required()
    def get(self, user_id):
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return {"message": "Profile not found"}, 404
        return profile.as_dict(), 200

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
        logging.debug(f'Received update request for user_id: {user_id} with data: {data}')

        profile = Profile.query.filter_by(user_id=user_id).first()

        if not profile:
            logging.warning(f'Profile not found for user_id: {user_id}')
            return {'message': 'Profile not found'}, 404

        if 'bio' in data:
            profile.bio = data['bio']
            logging.info(f'Updated bio for user_id: {user_id} to: {profile.bio}')

        if 'location' in data:
            profile.location = data['location']
            logging.info(f'Updated location for user_id: {user_id} to: {profile.location}')

        if 'DOB' in data:
            profile.date_of_birth = datetime.strptime(data['DOB'], '%Y-%m-%d').date()
            logging.info(f'Updated date of birth for user_id: {user_id} to: {profile.date_of_birth}')

        profile_picture = request.files.get('profile_picture')
        if profile_picture and allowed_file(profile_picture.filename):
            try:
                # Upload new profile picture to Cloudinary
                cloudinary_response = cloudinary.uploader.upload(profile_picture)
                profile.profile_picture = cloudinary_response['secure_url']  # Update the profile picture URL
                logging.info(f'Uploaded new profile picture for user_id: {user_id}')
            except Exception as e:
                logging.error(f'Failed to upload profile picture for user_id: {user_id}. Error: {str(e)}')
                return {'message': 'Failed to upload profile picture', 'error': str(e)}, 500

        try:
            db.session.commit()
            logging.info(f'Profile updated successfully for user_id: {user_id}')
        except Exception as e:
            db.session.rollback()  # Rollback the session on error
            logging.error(f'Failed to update profile for user_id: {user_id}. Error: {str(e)}')
            return {'message': 'Failed to update profile', 'error': str(e)}, 500

        return {'message': 'Profile updated successfully'}, 200