import random
import string
from datetime import datetime, timedelta
from flask import request, jsonify, make_response
from flask_restful import Resource
from flask_mail import Message
from models import db, User
from flask_jwt_extended import create_access_token
from mail import mail  # Assuming mail.py contains the Mail instance
import logging



logging.basicConfig(level=logging.DEBUG)

class RegisterUser(Resource):
    def post(self):
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400

        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        user_name = data.get('user_name')

        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'User is already registered'}), 400
        if User.query.filter_by(user_name=user_name).first():
            return jsonify({'error': 'User name is already taken'}), 400

        verification_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        expiration_time = datetime.utcnow() + timedelta(hours=1)

        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_name=user_name,
            verification_code=verification_code,
            verification_code_expiration=expiration_time,
        )
        new_user.set_password(password)

        # Add the user to the database
        db.session.add(new_user)
        db.session.commit()

        # Create and send the email message
        msg = Message('Email Verification', recipients=[email])
        msg.body = f'Your verification code is {verification_code}. It is valid for 1 hour.'

        try:
            mail.send(msg)
            logging.info(f"Verification email sent to {email}.")
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            return jsonify({'error': 'Failed to send verification email. Please try again later.'}), 500

        return jsonify({'message': 'Registration successful! Please check your email for a verification code.'}), 201




class ResendVerification(Resource):
    def post(self):
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email')
        if not email:
            return jsonify({'error': 'Email is required'}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        if user.is_verified:
            return jsonify({'error': 'User is already verified'}), 400

        verification_code = self._generate_verification_code()
        expiration_time = datetime.utcnow() + timedelta(hours=1)

        user.verification_code = verification_code
        user.verification_code_expiration = expiration_time

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to update user information.'}), 500

        if not self._send_verification_email(email, verification_code):
            return jsonify({'error': 'Failed to resend verification email. Please try again later.'}), 500

        return jsonify({'message': 'A new verification code has been sent to your email.'}), 200

    def _send_verification_email(self, email, verification_code):
        # Email sending logic here
        return True  # Change this as needed for actual email sending



class VerifyEmail(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        verification_code = data.get('verification_code')

        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404
        if user.verification_code != verification_code:
            return jsonify({'error': 'Invalid verification code'}), 400
        if datetime.utcnow() > user.verification_code_expiration:
            return jsonify({'error': 'Verification code has expired'}), 400

        user.is_verified = True
        user.verification_code = None
        user.verification_code_expiration = None
        db.session.commit()

        return jsonify({'message': 'Email verified successfully! You can now log in.'}), 200

class LoginUser(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        if not user.is_verified:
            return jsonify({'error': 'User is not verified'}), 403

        access_token = create_access_token(
            identity={
                'type': 'user',
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            }
        )
        return jsonify({'access_token': access_token, 'message': 'Login successful'}), 200
