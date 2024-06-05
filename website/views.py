from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from .models import User,Post, Upload, Comment, Like, Upload
from . import db
from werkzeug.utils import secure_filename
from colorsys import hls_to_rgb
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

@views.route("/community")
def community():
    posts = Post.query.all()
    
    if current_user.is_authenticated:
        visual_type = current_user.result.result_data if current_user.result else None # Fetch user's result from result table
        if visual_type:
            related_posts = Post.query.filter_by(visual_type=visual_type).all() # Relate the post with user's result of makeup test
        else:
            related_posts = []

    else:
        visual_type = None
        related_posts = []

    return render_template("community_page.html", user=current_user, posts=posts, related_posts=related_posts)


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

@views.route("/posts.comment/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.community'))
    
    posts = user.posts
    return render_template("community_page.html", user=current_user, posts=posts, username=username)

@views.route("/community_page", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')
        photo = request.files.get('photo')

        if not text:
            flash('Post cannot be empty', category='error')
        else:
            visual_type = None
            if current_user.result:
                visual_type = current_user.result.result_data # Relate the post with user's result of makeup test

            filename = None
            if photo and allowed_file(photo.filename):
                # Save the uploaded photo
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            elif photo and not allowed_file(photo.filename):
                flash('Invalid file type', category='error')
                return redirect(request.url)
            
            post = Post(text=text, author=current_user.id, photo=filename, visual_type=visual_type)
            
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.community'))  # Redirect to the community page after successfully creating the post

    # Fetch posts to display on the page
    posts = Post.query.order_by(Post.date.desc()).all()
    return render_template('community_page.html', user=current_user, posts=posts)

@views.route("/delete-post/<int:id>")
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)

    if current_user != post.user:
        flash("You do not have permission to delete this post.", category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('views.community'))

@views.route("/create-comment/<int:post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id).first()
        if post:
            comment = Comment(text=text, author=current_user.id, post_id=post_id)  # Use current_user.id
            db.session.add(comment)
            db.session.commit()
            flash('Comment created!', category='success')
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('views.community'))

@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()
        flash('Comment deleted.', category='success')

    return redirect(url_for('views.community'))

@views.route("/like-post/<post_id>", methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(author=current_user.id, post_id=post_id).first()

    if not post:
        return jsonify({'error': 'Post does not exist.'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": any(like.author == current_user.id for like in post.likes)})


#UPLOAD PICTURE
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route("/color", methods=['GET', 'POST'])
def color():
    if request.method == "POST":
        image = request.files.get('image')

        if not image:
            return jsonify({'success': False, 'message': 'No image file provided'})
        
        if not allowed_file(image.filename):
            return jsonify({'success': False, 'message': 'Invalid file type. Allowed types are: png, jpg, jpeg'})
        
        filename = secure_filename(image.filename)
        image_path=os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)

        color = Upload(image=filename)
        
        db.session.add(color)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Image submitted successfully!'})
        
    return render_template('color_page.html')

@views.route("/display_image", methods=['GET','POST'])
def display_image():
    image = Upload.query.order_by(Upload.id.desc()).first()
    return render_template('display_image.html', image=[image])

#COLOR ANALYSIS
@views.route("/results", methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        hair_color = request.form.get('hair_color')
        skin_color = request.form.get('skin_color')
        eye_color = request.form.get('eye_color')

        # Process the form data
        seasonal_palette = analyze_colors(hair_color, skin_color, eye_color)

        # Debug statement to print the seasonal_palette
        print("Seasonal Palette:", seasonal_palette)

        image = Upload.query.order_by(Upload.id.desc()).first()
        image.hair_color = hair_color
        image.skin_color = skin_color
        image.eye_color = eye_color
        image.seasonal_palette = seasonal_palette
        db.session.commit()

        # Redirect to results page with seasonal_palette as a query parameter
        return redirect(url_for('views.show_results', seasonal_palette=seasonal_palette))

    return render_template('results.html')

def analyze_colors(hair_color, skin_color, eye_color):
    undertone = determine_undertone(skin_color)
    hair_type = analyze_hair_color(hair_color)
    eye_type = analyze_eye_color(eye_color)
    seasonal_palette = determine_seasonal_palette(undertone, hair_type, eye_type)

    # Debug statements to print undertone, hair type, and eye type
    print("Undertone:", undertone)
    print("Hair Type:", hair_type)
    print("Eye Type:", eye_type)

    return seasonal_palette

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def determine_undertone(skin_color):
    r, g, b = hex_to_rgb(skin_color)
    if r > g and r > b:
        return 'warm'
    elif b > r and b > g:
        return 'cool'
    else:
        return 'neutral'

def analyze_hair_color(hair_color):
    r, g, b = hex_to_rgb(hair_color)
    if r > g and r > b:
        return 'warm'
    elif b > r and b > g:
        return 'cool'
    elif r + g + b > 450:
        return 'light'
    else:
        return 'neutral'

def analyze_eye_color(eye_color):
    r, g, b = hex_to_rgb(eye_color)
    if r > g and r > b:
        return 'warm'
    elif b > r and b > g:
        return 'cool'
    else:
        return 'neutral'

def determine_seasonal_palette(undertone, hair_type, eye_type):
    if undertone == 'cool' and hair_type == 'cool' and eye_type == 'cool':
        return 'Summer'
    elif undertone == 'cool' and hair_type == 'cool' and eye_type == 'neutral':
        return 'Summer'
    elif undertone == 'cool' and hair_type == 'neutral' and eye_type == 'cool':
        return 'Winter'
    elif undertone == 'cool' and hair_type == 'neutral' and eye_type == 'neutral':
        return 'Soft Summer'
    elif undertone == 'cool' and hair_type == 'light' and eye_type == 'cool':
        return 'Summer'
    elif undertone == 'cool' and hair_type == 'warm' and eye_type == 'warm':
        return 'Soft Autumn'
    elif undertone == 'cool' and hair_type == 'light' and eye_type == 'warm':
        return 'Soft Summer'
    elif undertone == 'cool' and hair_type == 'cool' and eye_type == 'warm':
        return 'Soft Autumn'
    elif undertone == 'cool' and hair_type == 'warm' and eye_type == 'cool':
        return 'Soft Summer'
    elif undertone == 'cool' and hair_type == 'warm' and eye_type == 'neutral':
        return 'Soft Autumn'
    elif undertone == 'cool' and hair_type == 'neutral' and eye_type == 'warm':
        return 'Soft Autumn'
    elif undertone == 'cool' and hair_type == 'light' and eye_type == 'neutral':
        return 'Soft Summer'
    elif undertone == 'warm' and hair_type == 'light' and eye_type == 'neutral':
        return 'Light Spring'
    elif undertone == 'warm' and hair_type == 'warm' and eye_type == 'warm':
        return 'Autumn'
    elif undertone == 'warm' and hair_type == 'light' and eye_type == 'warm':
        return 'Light Spring'
    elif undertone == 'warm' and hair_type == 'warm' and eye_type == 'cool':
        return 'Soft Autumn'
    elif undertone == 'warm' and hair_type == 'cool' and eye_type == 'warm':
        return 'Soft Autumn'
    elif undertone == 'warm' and hair_type == 'warm' and eye_type == 'neutral':
        return 'Autumn'
    elif undertone == 'warm' and hair_type == 'neutral' and eye_type == 'warm':
        return 'Autumn'
    elif undertone == 'warm' and hair_type == 'light' and eye_type == 'cool':
        return 'Soft Autumn'
    elif undertone == 'warm' and hair_type == 'cool' and eye_type == 'neutral':
        return 'Soft Autumn'
    elif undertone == 'warm' and hair_type == 'neutral' and eye_type == 'cool':
        return 'Soft Autumn'
    elif undertone == 'warm' and hair_type == 'cool' and eye_type == 'cool':
        return 'Soft Summer'
    elif undertone == 'warm' and hair_type == 'neutral' and eye_type == 'neutral':
        return 'Soft Autumn'
    elif undertone == 'neutral' and hair_type == 'warm' and eye_type == 'cool':
        return 'Soft Autumn'
    elif undertone == 'neutral' and hair_type == 'cool' and eye_type == 'warm':
        return 'Soft Autumn'
    elif undertone == 'neutral' and hair_type == 'light' and eye_type == 'neutral':
        return 'Soft Summer'
    elif undertone == 'neutral' and hair_type == 'cool' and eye_type == 'neutral':
        return 'Soft Summer'
    elif undertone == 'neutral' and hair_type == 'neutral' and eye_type == 'cool':
        return 'Soft Summer'
    elif undertone == 'neutral' and hair_type == 'light' and eye_type == 'warm':
        return 'Soft Autumn'
    elif undertone == 'neutral' and hair_type == 'light' and eye_type == 'cool':
        return 'Soft Summer'
    elif undertone == 'neutral' and hair_type == 'warm' and eye_type == 'neutral':
        return 'Soft Autumn'
    elif undertone == 'neutral' and hair_type == 'neutral' and eye_type == 'warm':
        return 'Soft Autumn'
    elif undertone == 'neutral' and hair_type == 'neutral' and eye_type == 'neutral':
        return 'Soft Summer'
    elif undertone == 'neutral' and hair_type == 'warm' and eye_type == 'warm':
        return 'Autumn'
    elif undertone == 'neutral' and hair_type == 'cool' and eye_type == 'cool':
        return 'Summer'
    else:
        return 'Unknown'
  
@views.route("/show_results")
def show_results():
    # Get the seasonal_palette from the query parameters
    seasonal_palette = request.args.get('seasonal_palette')

    # Render the template with the seasonal_palette
    return render_template('results.html', seasonal_palette=seasonal_palette)