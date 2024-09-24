from flask import request,jsonify
from flask_restful import Resource
from models import User, db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

class Registeruser(Resource):
    def post(self):
        data = request.get_json()
        if not data:
            return jsonify({'error':'invalid JSON'}),400
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        user_name = data.get('user_name')

        if User.query.filter_by(email = email).first():
            return jsonify({'error':'user is already registered'}), 400
        
        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_name = user_name,
            
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

class Loginuser(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email = email).first()

        if not user or not user.check_password(password):
            return jsonify({'error':'invalid email or password'}), 401
        
        access_token = create_access_token(
            identity={'type': 'user', 'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email},
            
        )
        return {'access_token': access_token, 'message': 'Login successful'}, 200

        


        
        