from flask import Flask, render_template, request

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

@app.route('/test_result', methods=['POST'])
def test_result():
    return render_template('test_result.html')

@app.route('/community')
def community():
    return render_template("community_page.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/signup')
def signup():
    return render_template("sign_up.html")

if __name__ == '__main__' :
    app.run(debug=True)