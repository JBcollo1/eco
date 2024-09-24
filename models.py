from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(20), nullable=False, unique=True, index=True)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    posts = db.relationship('Post', back_populates='user', lazy='dynamic')  # One-to-many relationship with Post
    comments = db.relationship('Comment', back_populates='user', lazy='dynamic')  # One-to-many relationship with Comment
    likes = db.relationship('Like', back_populates='user', lazy='dynamic')  # One-to-many relationship with Like

    def set_password(self, password):
        """Hashes the password and stores it in the password_hash field."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the given password matches the stored password hash."""
        return check_password_hash(self.password_hash, password)

    def as_dict(self):
        """Returns a dictionary representation of the User object."""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'user_name': self.user_name,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<User {self.user_name}>'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to the User table
    content = db.Column(db.Text, nullable=False)  # The main content of the post
    image_url = db.Column(db.String(255))  # Optional field for images
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', back_populates='posts')  # Establishes a relationship with the User model
    comments = db.relationship('Comment', back_populates='post', lazy='dynamic')  # One-to-many relationship with Comment
    likes = db.relationship('Like', back_populates='post', lazy='dynamic')  # One-to-many relationship with Like

    def as_dict(self):
        """Returns a dictionary representation of the Post object."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Post {self.id} by User {self.user_id}>'


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)  # Foreign key to Post
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User
    content = db.Column(db.Text, nullable=False)  # The content of the comment
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='comments')  # Establishes a relationship with the User model
    post = db.relationship('Post', back_populates='comments')  # Establishes a relationship with the Post model

    def as_dict(self):
        """Returns a dictionary representation of the Comment object."""
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Comment {self.id} on Post {self.post_id} by User {self.user_id}>'


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)  # Foreign key to Post
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # When the like was created

    # Relationships
    user = db.relationship('User', back_populates='likes')  # Establishes a relationship with the User model
    post = db.relationship('Post', back_populates='likes')  # Establishes a relationship with the Post model

    def as_dict(self):
        """Returns a dictionary representation of the Like object."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Like {self.id} by User {self.user_id} on Post {self.post_id}>'
