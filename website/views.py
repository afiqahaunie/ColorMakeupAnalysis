from flask import Blueprint, render_template

views = Blueprint("views", __name__)

@views.route("/")
@views.route("/home")
def home():
    return render_template("home.html")

@views.route('/color')
def color():
    return render_template("color_page.html")

@views.route('/makeup')
def makeup():
    return render_template("makeup_page.html")

@views.route('/community')
def community():
    return render_template("community_page.html")

@views.route('/login')
def login():
    return render_template("login.html")

@views.route('/signup')
def signup():
    return render_template("signup.html")