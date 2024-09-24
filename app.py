import os
from flask import Flask
from flask_restful import Api
from models import db
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from login import RegisterUser, LoginUser, VerifyEmail, ResendVerification
from mail import mail

app = Flask(__name__)
api = Api(app)
jwt = JWTManager(app)

migrate = Migrate(app, db)
CORS(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # Use env variable

db.init_app(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jbcollins254@gmail.com'  
app.config['MAIL_PASSWORD'] = 'rbcp btoe tzjn umvl'  
app.config['MAIL_DEFAULT_SENDER'] = 'jbcollins254@gmail.com'

mail.init_app(app)

api.add_resource(RegisterUser, '/auth/register/user')
api.add_resource(LoginUser, '/auth/login/user')
api.add_resource(VerifyEmail, '/auth/verify/user')
api.add_resource(ResendVerification, '/auth/resend/user')


if __name__ == '__main__':
    app.run(debug=True)
