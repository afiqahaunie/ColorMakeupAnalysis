from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Post
from . import db

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

@views.route('/color')
def color():
    return render_template("color_page.html")

@views.route('/makeup')
def makeup():
    return render_template("makeup_page.html")

@views.route('/community')
def community():
    posts = Post.query.all()
    return render_template("community_page.html", user=current_user, posts=posts)

@views.route('/test_result', methods=['POST'])
def test_result():
    # Get user's answers from the form
    user_answers = {key: request.form.getlist(key) for key in request.form.keys()}
    
    # Calculate total count of "A" and "B" across all questions
    total_a = sum(answer.count("A") for answer in user_answers.values())
    total_b = sum(answer.count("B") for answer in user_answers.values())

    # Determine the result based on total counts
    if total_a > total_b:
        visual_type = "low"
    elif total_a < total_b:
        visual_type = "high"
    else:
        visual_type = "mixed"

    # Render a template with the result
    return render_template('views.test_result.html', visual_type=visual_type)

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