from flask import Flask
from flask_restful import Api
from models import db
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from login import Registeruser, Loginuser

app = Flask(__name__)
api = Api(app)
jwt = JWTManager(app)

migrate = Migrate(app,db)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'ecofriendly'

db.init_app(app)

api.add_resource(Registeruser, '/auth/register/user')
api.add_resource(Loginuser, '/auth/login/user')
if __name__ == '__main__':
    app.run(debug=True)