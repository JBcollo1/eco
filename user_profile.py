from flask_restful import Resource
from flask import request, jsonify, current_app
from models import Profile, db
import os
from werkzeug.utils import secure_filename


class UserProfile(Resource):
    def post(self):
        data = request.form
        user_id = data.get('user_id')  # Assuming you're passing user_id in the request
        bio = data.get('bio')
        location = data.get('location')
        date_of_birth = data.get('DOB')
        profile_picture = request.files.get('profile_picture')  # Get the uploaded file

        # Check if a profile already exists for the user
        profile = Profile.query.filter_by(user_id=user_id).first()

        # Handle the profile picture upload
        if profile_picture:
            filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            profile_picture_url = f"/{current_app.config['UPLOAD_FOLDER']}/{filename}"
        else:
            profile_picture_url = None

        if profile:
            # Update existing profile
            profile.bio = bio
            profile.location = location
            profile.date_of_birth = date_of_birth
            profile.profile_picture = profile_picture_url
        else:
            # Create a new profile
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

    def get(self, user_id):
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({"message": "Profile not found"}), 404

        return jsonify(profile.as_dict()), 200

    def delete(self, user_id):
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({"message": "Profile not found"}), 404

        db.session.delete(profile)
        db.session.commit()
        return jsonify({"message": "Profile deleted successfully!"}), 200
    def patch(self, user_id):
        data = request.get_json()
        
        # Fetch the profile from the database
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({'message': 'Profile not found'}), 404
        
        # Update fields if they are present in the request
        if 'bio' in data:
            profile.bio = data['bio']
        if 'location' in data:
            profile.location = data['location']
        if 'date_of_birth' in data:
            profile.date_of_birth = data['date_of_birth']
        
        # Handle profile picture upload if provided
        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture:
                filename = secure_filename(profile_picture.filename)
                profile_picture.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                profile.profile_picture = filename  # Update profile picture filename
        
        # Commit the changes to the database
        db.session.commit()
        
        return jsonify({'message': 'Profile updated successfully', 'profile': profile.as_dict()}), 200