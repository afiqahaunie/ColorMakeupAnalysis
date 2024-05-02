from flask import Blueprint, render_template
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
    return render_template('test_result.html')

@views.route('/community')
def community():
    return render_template("community_page.html")

@views.route('/login')
def login():
    return render_template("login.html")

@views.route('/signup')
def signup():
    return render_template("signup.html")