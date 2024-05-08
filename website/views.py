from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import Post
from . import db
from flask import request

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

    return render_template("home.html")

@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    return render_template('create_post.html', user=current_user)

@views.route('/color')
def color():
    return render_template("color_page.html")

@views.route('/makeup')
def makeup():
    return render_template("makeup_page.html")

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

@views.route('/community')
def community():
    return render_template("community_page.html")

@views.route('/login')
def login():
    return render_template("login.html")

@views.route('/signup')
def signup():
    return render_template("signup.html")