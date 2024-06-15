from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from functools import wraps
from .models import Post, Upload, Comment, Like, ColorAnalysis, Result
from . import db
import os

views = Blueprint("views", __name__)

def custom_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('views.login'))  # Redirect to the login page without flashing a message
        return f(*args, **kwargs)
    return decorated_function

@views.route("/")
@views.route("/home")
def home():
    return render_template("home.html", user=current_user)

@views.route('/makeup')
def makeup():
    return render_template("makeup_page.html", user=current_user)

@views.route("/community")
def community():
    posts = Post.query.order_by(Post.date.desc()).all()
    comments = Comment.query.order_by(Comment.date.desc()).all()

    if current_user.is_authenticated:
        visual_type = request.args.get('visual_type')
        seasonal_palette = request.args.get('seasonal_palette')

        # Fetching posts based on filters
        if visual_type:
            posts = Post.query.filter_by(visual_type=visual_type).order_by(Post.date.desc()).all()
        elif seasonal_palette:
            posts = Post.query.filter_by(seasonal_palette=seasonal_palette).order_by(Post.date.desc()).all()
        else:
            posts = Post.query.order_by(Post.date.desc()).all()
            comments = Comment.query.order_by(Comment.date.desc()).all()
            
        # Fetch user's latest result from result table
        latest_result = Result.query.filter_by(user_id=current_user.id).order_by(Result.id.desc()).first()
        visual_type = latest_result.result_data if latest_result else None 
        seasonal_palette = current_user.coloranalysis[-1].seasonal_palette if current_user.coloranalysis else None
        if visual_type:
            related_posts = Post.query.filter_by(visual_type=visual_type).all() # Relate the post with user's result of makeup test
        elif seasonal_palette:
            related_posts = Post.query.filter_by(seasonal_palette=seasonal_palette).all() # Relate the post with user's seasonal palette
        else:
            related_posts = []

    else:
        visual_type = None
        seasonal_palette = None
        related_posts = []

    return render_template("community_page.html", user=current_user, posts=posts, related_posts=related_posts, comments=comments)


@views.route('/login')
def login():
    return render_template("login.html")

@views.route('/signup')
def signup():
    return render_template("signup.html")

@views.route("/community_page", methods=['GET', 'POST'])
@custom_login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')
        photo = request.files.get('photo')

        if not text and (not photo or photo.filename == ''):
            return jsonify({'success': False, 'message': 'Post cannot be empty. Please provide text or photo.'})
        
        else:
            # User has result of both tests
            if current_user.result and current_user.coloranalysis:
                latest_result = current_user.results[-1]
                visual_type = latest_result.result_data
                seasonal_palette = current_user.coloranalysis[-1].seasonal_palette
            
            # User has makeup test result only
            elif current_user.result:
                latest_result = current_user.results[-1]
                visual_type = latest_result.result_data if latest_result else None # Relate the post with user's result of makeup test
                seasonal_palette = None
            
            # User has color analysis result only
            elif current_user.coloranalysis:
                seasonal_palette = current_user.coloranalysis[-1].seasonal_palette if current_user.coloranalysis else None # Relate the post with user's result of color analysis test
                visual_type = None

            else:
                seasonal_palette = None
                visual_type = None

            filename = None

            if photo and allowed_file(photo.filename):
                # Save the uploaded photo
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

            elif photo and not allowed_file(photo.filename):
                return jsonify({'success': False, 'message': 'Invalid file type'})
            
             # Only create the post if text is provided or photo is successfully uploaded
            if text or filename:
                post = Post(text=text, author=current_user.id, photo=filename, visual_type=visual_type, seasonal_palette=seasonal_palette)
                
                db.session.add(post)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Post created successfully'})  # Redirect to the community page after successfully creating the post

    # Fetch posts to display on the page
    posts = Post.query.order_by(Post.date.desc()).all()
    return render_template('community_page.html', user=current_user, posts=posts)

@views.route("/delete-post/<int:id>")
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)

    if current_user != post.user:
        pass 
    else:
        db.session.delete(post)
        db.session.commit()

    return redirect(url_for('views.community'))

@views.route("/create-comment/<int:post_id>", methods=['POST'])
@custom_login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        pass  
    else:
        post = Post.query.filter_by(id=post_id).first()
        if post:
            comment = Comment(text=text, author=current_user.id, post_id=post_id)  # Use current_user.id
            db.session.add(comment)
            db.session.commit()
        else:
            pass  

    return redirect(url_for('views.community'))

@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        pass  
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        pass  
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.community'))

@views.route("/like-post/<post_id>", methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(author=current_user.id, post_id=post_id).first()

    if not post:
        # No error message returned, only an empty response with a 400 status code
        return '', 400

    if like:
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
        
    return render_template('color_page.html', user=current_user)

@views.route("/display_image", methods=['GET','POST'])
def display_image():
    image = Upload.query.order_by(Upload.id.desc()).first()
    return render_template('display_image.html', image=[image], user=current_user)

#COLOR ANALYSIS
@views.route("/results", methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        # Get form data
        hair_color = request.form.get('hair_color')
        skin_color = request.form.get('skin_color')
        eye_color = request.form.get('eye_color')

        # Process the form data
        seasonal_palette = analyze_colors(hair_color, skin_color, eye_color)

        print("Seasonal Palette:", seasonal_palette)

        image = Upload.query.order_by(Upload.id.desc()).first()
        image.hair_color = hair_color
        image.skin_color = skin_color
        image.eye_color = eye_color
        db.session.commit()

        # Save user's result in session if they are not signed up yet
        if not current_user.is_authenticated:
            session['coloranalysis'] = seasonal_palette

        previous_seasonal_palette = session.get('coloranalysis')
        related_posts_color = []

        if current_user.is_authenticated:
                new_analysis = ColorAnalysis(seasonal_palette=seasonal_palette, user=current_user)
                db.session.add(new_analysis)
                db.session.commit()

                # Get the previous seasonal palette of the user
                if current_user.palette:
                    previous_seasonal_palette = current_user.palette[-1].seasonal_palette

                # Get related posts with the previous seasonal palette
                if previous_seasonal_palette:
                    related_posts_color = Post.query.filter_by(seasonal_palette=previous_seasonal_palette).all()

        return redirect(url_for('views.show_results', user=current_user, seasonal_palette=seasonal_palette, previous_seasonal_palette=previous_seasonal_palette, related_posts_color=related_posts_color))

    return render_template('results.html')

@views.route('/previous_seasonal_palette', methods=['GET'])
@login_required
def previous_seasonal_palette():
    previous_seasonal_palette = current_user.coloranalysis[-1].seasonal_palette if current_user.coloranalysis else None  
    related_posts_color = []

    if previous_seasonal_palette:
        related_posts_color = Post.query.filter_by(seasonal_palette=previous_seasonal_palette).all()
    
    return render_template('results.html', seasonal_palette=previous_seasonal_palette, user=current_user, related_posts_color=related_posts_color)

# Function to analyze colors and determine seasonal palette
def analyze_colors(hair_color, skin_color, eye_color):
    undertone = determine_undertone(skin_color)
    hair_type = analyze_hair_color(hair_color)
    eye_type = analyze_eye_color(eye_color)
    seasonal_palette = determine_seasonal_palette(undertone, hair_type, eye_type)

    print("Undertone:", undertone)
    print("Hair Type:", hair_type)
    print("Eye Type:", eye_type)

    return seasonal_palette

# Convert hex color to rgb
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

# Match undertone, hair_type and eye_type to get seasonal palette
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
    return render_template('results.html', seasonal_palette=seasonal_palette, user=current_user)