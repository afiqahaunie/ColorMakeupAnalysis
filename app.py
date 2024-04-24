from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("main_page.html")

@app.route('/')
def color():
    return render_template("color_page.html")

@app.route('/')
def makeup():
    return render_template("makeup_page.html")

@app.route('/')
def community():
    return render_template("community_page.html")