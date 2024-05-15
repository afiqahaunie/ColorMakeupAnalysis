from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from .models import Post, Upload
from .color_analysis import analyze_colors_from_image
from . import db
from werkzeug.utils import secure_filename
from random import choice
from sqlalchemy import func
import os

views = Blueprint("views", __name__)

@views.route("/")
@views.route("/home")
def home():
    if request.method =="POST":
        text = request.form.get('text')

        if not text:
            flash('Post cannot be empty', category='error')
        else:
            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')

    return render_template("home.html", user=current_user)

@views.route('/makeup')
def makeup():
    return render_template("makeup_page.html")

@views.route('/community')
def community():
    posts = Post.query.all()
    return render_template("community_page.html", user=current_user, posts=posts)

@views.route('/login')
def login():
    return render_template("login.html")

@views.route('/signup')
def signup():
    return render_template("signup.html")

@views.route("/post_page")
def post_page():
    posts = Post.query.all()
    return render_template("post_page.html", posts=posts)
    
@views.route("/community_page", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')

        if not text:
            flash('Post cannot be empty', category='error')
        else:
            post = Post(text=text, author=current_user.id)  
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.community'))  # Redirect to the community page after successfully creating the post
    return render_template('community_page.html', user=current_user)

#UPLOAD PICTURE
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route("/color", methods=['GET', 'POST'])
def color():
    if request.method == "POST":
        image = request.files.get('image')

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path=os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
             # Analyze colors from the uploaded image
            dominant_colors = analyze_colors_from_image(image_path)
            # Process the dominant colors as needed
            color = Upload(image=filename)
        
        elif image and not allowed_file(image.filename):
            flash('Invalid file type. Allowed types are: png, jpg, jpeg', category='error')
            return redirect(request.url)
        
        else:
            color = Upload(image=filename)
        
        db.session.add(color)
        db.session.commit()
        flash('Image submitted succesfully!', category='success')
        return redirect(url_for('views.display_image'))
        

    return render_template('color_page.html')

@views.route("/display_image")
def display_image():
    image = Upload.query.order_by(Upload.id.desc()).first()
    return render_template('display_image.html', image=[image])

@views.route('/generate-palette', methods=['POST'])
def generate_palette():
    data = request.get_json()
    hair_color = data['hair_color']
    skin_color = data['skin_color']
    eye_color = data['eye_color']
    processed_colors = process_colors(hair_color, skin_color, eye_color)
    return jsonify({'palette': processed_colors})

def process_colors(hair_color, skin_color, eye_color):
    # Implement color processing logic here
    processed_colors = [hair_color, skin_color, eye_color]
    return processed_colors