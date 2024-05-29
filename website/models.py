from . import db 
from flask_login import UserMixin 
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    posts =db.relationship('Post', backref='user', passive_deletes=True)
    comments =db.relationship('Comment', backref='post', passive_deletes=True)
    result = db.relationship('Result', backref='user_result', uselist=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    comments = db.relationship('Comment', backref='post_comments', lazy=True)
    visual_type = db.Column(db.String(255), nullable=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(150))
    hair_color = db.Column(db.String(7))  # Assuming hexadecimal color representation, e.g., "#RRGGBB"
    skin_color = db.Column(db.String(7))
    eye_color = db.Column(db.String(7))
     
class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result_data = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db. ForeignKey('user.id'))
    user = db.relationship('User', backref='results')
