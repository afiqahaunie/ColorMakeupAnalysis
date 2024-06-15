from . import db 
from flask_login import UserMixin 
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    posts = db.relationship('Post', backref='user', passive_deletes=True)
    result = db.relationship('Result', backref='user_result')
    coloranalysis = db.relationship('ColorAnalysis', backref='user_pallete')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    photo = db.Column(db.String(255))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    comments = db.relationship('Comment', backref='post', passive_deletes=True)
    likes = db.relationship('Like', backref='post', passive_deletes=True)
    visual_type = db.Column(db.String(255), nullable=True)
    seasonal_palette = db.Column(db.String(255), nullable=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)
    author_username = db.relationship('User', backref='comments', lazy=True)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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

class ColorAnalysis(db.Model):
    __tablename__ = 'color_analysis'
    id = db.Column(db.Integer, primary_key=True)
    seasonal_palette = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db. ForeignKey('user.id'))
    user = db.relationship('User', back_populates='coloranalysis', overlaps='coloranalysis,user_pallete')