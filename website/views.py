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
        visual_type = current_user.result.result_data if current_user.result else None
        if visual_type:
            related_posts = Post.query.filter_by(visual_type=visual_type).all()
        else:
            related_posts = []

    else:
        visual_type = None
        related_posts = []

    return render_template("community_page.html", user=current_user, posts=posts, comments=Comment, related_posts=related_posts)


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
        
        if not text:
            flash('Post cannot be empty', category='error')
        else:
            visual_type = None
            if current_user.result:
                visual_type = current_user.result.result_data 
            
             
            post = Post(text=text, author=current_user.id, visual_type=visual_type)  

            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.community'))  # Redirect to the community page after successfully creating the post
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

    # Initialize variables
    hair_color = None
    skin_color = None
    eye_color = None
    seasonal_palette = None
    suggested_palette = None

    if request.method == 'POST':
        hair_color = request.form.get('hair_color')
        skin_color = request.form.get('skin_color')
        eye_color = request.form.get('eye_color')
        
        # Print the form data for debugging
        print("Received form data:")
        print("Hair color:", hair_color)
        print("Skin color:", skin_color)
        print("Eye color:", eye_color)

        # Get the latest Upload object
        image = Upload.query.order_by(Upload.id.desc()).first()

        # Update the Upload object with the received form data
        image.hair_color = hair_color
        image.skin_color = skin_color
        image.eye_color = eye_color

        # Save the changes to the database
        db.session.commit()

        seasonal_palette = determine_seasonal_palette(hair_color, skin_color, eye_color)
        suggested_palette = suggest_color_palette(seasonal_palette)

        print("Seasonal Palette:", seasonal_palette)
        print("Suggested Palette:", suggested_palette)
 
        return render_template('display_image.html', image=[image], hair_color=hair_color, skin_color=skin_color, eye_color=eye_color, seasonal_palette=seasonal_palette, suggested_palette=suggested_palette)
    
    image = Upload.query.order_by(Upload.id.desc()).first()
    return render_template('display_image.html', image=[image], hair_color=hair_color, skin_color=skin_color, eye_color=eye_color)

#COLOR ANALYSIS
def analyze_colors(hair_color, skin_color, eye_color):
    # Convert hex colors to RGB
    hair_rgb = hex_to_rgb(hair_color)
    skin_rgb = hex_to_rgb(skin_color)
    eye_rgb = hex_to_rgb(eye_color)

    # Calculate the average color
    avg_rgb = [(hair_rgb[0] + skin_rgb[0] + eye_rgb[0]) / 3,
               (hair_rgb[1] + skin_rgb[1] + eye_rgb[1]) / 3,
               (hair_rgb[2] + skin_rgb[2] + eye_rgb[2]) / 3]

    # Calculate the dominant color (highest luminance)
    dominant_color = max([hair_rgb, skin_rgb, eye_rgb], key=lambda x: luminance(x))

    
    # Create a color palette based on the dominant color
    palette = []
    for i in range(5):
        hue = (dominant_color[0] + i * 30) % 360
        saturation = dominant_color[1] * 0.8
        lightness = dominant_color[2] * 0.8
        rgb = hls_to_rgb(hue, saturation, lightness)
        palette.append(rgb_to_hex(rgb))

    return palette

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def luminance(rgb):
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(round(rgb[0]), round(rgb[1]), round(rgb[2]))

@views.route("/color_palette", methods=['GET'])
def color_palette():
    hair_color = request.args.get('hair_color')
    skin_color = request.args.get('skin_color')
    eye_color = request.args.get('eye_color')

    palette = analyze_colors(hair_color, skin_color, eye_color)

    return jsonify({'palette': palette})

def determine_seasonal_palette(hair_color, skin_color, eye_color):
    print("Hair color:", hair_color)
    print("Skin color:", skin_color)
    print("Eye color:", eye_color)

    undertone = determine_undertone(skin_color)
    print("Undertone:", undertone)

    hair_type = analyze_hair_color(hair_color)
    print("Hair type:", hair_type)

    eye_type = analyze_eye_color(eye_color)
    print("Eye type:", eye_type)

    if undertone == 'cool' and hair_type == 'cool' and eye_type == 'cool':
        return 'Deep Winter'
    elif undertone == 'cool' and hair_type == 'cool' and eye_type == 'neutral':
        return 'Winter'
    elif undertone == 'cool' and hair_type == 'neutral' and eye_type == 'cool':
        return 'Summer'
    elif undertone == 'cool' and hair_type == 'neutral' and eye_type == 'neutral':
        return 'Summer'
    elif undertone == 'cool' and hair_type == 'light' and eye_type == 'cool':
        return 'Summer'
    elif undertone == 'cool' and hair_type == 'warm' and eye_type == 'warm':
        return 'Autumn'
    elif undertone == 'cool' and hair_type == 'light' and eye_type == 'warm':
        return 'Spring'
    elif undertone == 'cool' and hair_type == 'cool' and eye_type == 'warm':
        return 'Soft Autumn'
    elif undertone == 'cool' and hair_type == 'warm' and eye_type == 'cool':
        return 'Soft Summer'
    elif undertone == 'cool' and hair_type == 'warm' and eye_type == 'neutral':
        return 'Soft Autumn'
    elif undertone == 'cool' and hair_type == 'neutral' and eye_type == 'warm':
        return 'Soft Autumn'
    elif undertone == 'warm' and hair_type == 'light' and eye_type == 'neutral':
        return 'Spring'
    elif undertone == 'warm' and hair_type == 'warm' and eye_type == 'warm':
        return 'Autumn'
    elif undertone == 'warm' and hair_type == 'light' and eye_type == 'warm':
        return 'Spring'
    elif undertone == 'warm' and hair_type == 'warm' and eye_type == 'cool':
        return 'Deep Winter'
    elif undertone == 'warm' and hair_type == 'cool' and eye_type == 'warm':
        return 'Soft Autumn'
    elif undertone == 'warm' and hair_type == 'warm' and eye_type == 'neutral':
        return 'Autumn'
    elif undertone == 'warm' and hair_type == 'neutral' and eye_type == 'warm':
        return 'Autumn'
    elif undertone == 'warm' and hair_type == 'light' and eye_type == 'cool':
        return 'Soft Autumn'
    elif undertone == 'warm' and hair_type == 'cool' and eye_type == 'neutral':
        return 'Soft Summer'
    elif undertone == 'warm' and hair_type == 'neutral' and eye_type == 'cool':
        return 'Soft Summer'
    elif undertone == 'neutral' and hair_type == 'warm' and eye_type == 'cool':
        return 'Soft Summer'
    elif undertone == 'neutral' and hair_type == 'cool' and eye_type == 'warm':
        return 'Deep Autumn'
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
    else:
        return 'Unknown'

def determine_undertone(skin_color):
    r, g, b = hex_to_rgb(skin_color)
    if r > g and r > b:
        return 'warm'
    elif g > r and g > b:
        return 'cool'
    else:
        return 'neutral'

def analyze_hair_color(hair_color):
    r, g, b = hex_to_rgb(hair_color)
    if r > g and r > b:
        return 'warm'
    elif g > r and g > b:
        return 'cool'
    elif r < 100 and g < 100 and b < 100:
        return 'light'
    else:
        return 'neutral'

def analyze_eye_color(eye_color):
    r, g, b = hex_to_rgb(eye_color)
    if r > g and r > b:
        return 'warm'
    elif g > r and g > b:
        return 'cool'
    else:
        return 'neutral'
    
def suggest_color_palette(seasonal_palette):
    """
    Suggests a color palette based on the user's seasonal color palette.
    """
    if seasonal_palette == 'Deep Winter':
        return 'Dark, cool colors like navy blue, black, and dark gray. Avoid warm colors like orange and yellow.'
    elif seasonal_palette == 'Winter':
        return 'Cool, bright colors like icy blue, silver, and frosty pink. Avoid warm colors like orange and yellow.'
    elif seasonal_palette == 'Spring':
        return 'Warm, bright colors like sunshine yellow, orange, and coral. Avoid cool colors like blue and green.'
    elif seasonal_palette == 'Summer':
        return 'Light, cool colors like pale blue, mint green, and lavender. Avoid warm colors like orange and yellow.'
    elif seasonal_palette == 'Autumn':
        return 'Warm, earthy colors like olive green, terracotta, and golden brown. Avoid cool colors like blue and green.'
    elif seasonal_palette == 'Soft Autumn':
        return 'Embrace warm, muted hues like soft peach and dusty rose. Opt for subtle earthy tones such as warm browns and muted oranges. Avoid cooler shades like icy blues and stark greens.'
    elif seasonal_palette == 'Soft Summer':
        return 'Embrace soft, cool-toned hues like dusty blue and lavender. Opt for muted pastels such as soft pink and sage green. Avoid overly warm or vibrant colors, opting for subtle tones instead.'
    elif seasonal_palette == 'Deep Autumn':
        return 'Embrace rich, warm hues like deep rust and chocolate brown. Opt for saturated colors such as burgundy and mustard yellow. Avoid overly light or cool tones, sticking to deep, earthy shades.'
    else:
        return 'Unknown'