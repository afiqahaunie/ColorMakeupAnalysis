from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("main_page.html")

@app.route('/color')
def color():
    return render_template("color_page.html")

@app.route('/makeup')
def makeup():
    return render_template("makeup_page.html")

@app.route('/community')
def community():
    return render_template("community_page.html")

if __name__ == '__main__' :
    app.run(debug=True)