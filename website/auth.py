from flask import Flask, Blueprint, render_template, redirect, url_for, request, flash
from . import db 
from flask import session
from .models import User, Result
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import urllib.request
import os

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
       email = request.form.get("email")
       password = request.form.get("password")

       user = User.query.filter_by(email=email).first()
       if user:
          if check_password_hash(user.password, password):
             flash("Logged in!", category='success')
             login_user(user, remember=True)
             return redirect(url_for('views.home'))
          else:
             flash('Password is incorrect.', category='error')
       else: 
          flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@auth.route("/signup", methods=['GET','POST'])
def signup():
    if request.method == 'POST':
      email = request.form.get("email")
      username = request.form.get("username")
      password1 = request.form.get("password1")
      password2 = request.form.get("password2")

      email_exists = User.query.filter_by(email=email).first()
      username_exists = User.query.filter_by(username=username).first()

      if email_exists:
         flash('Email is already used.', category='error')
      elif username_exists:
         flash('Username is already used.', category='error')
      elif password1 != password2: 
         flash('Password don\'t match. Please write again.', category='error')
      elif len(username) < 2:
         flash ('Username is too short.', category='error')
      elif len(password1) < 5:
         flash ('Password is too short.', category='error')
      else:
         new_user = User(email=email, username=username, password=generate_password_hash(password1, method='pbkdf2:sha256'))
         db.session.add(new_user)
         db.session.commit()
         login_user(new_user, remember=True)
         flash('User created!')

         if test_result:
             new_result = Result(result_data=test_result, user=new_user)
             db.session.add(new_result)
             db.session.commit()

         return redirect(url_for('views.home'))
      
    return render_template("signup.html", user=current_user)

@auth.route('/test_result', methods=['GET', 'POST'])
def test_result():
    if request.method == 'POST':

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

            if current_user.is_authenticated:
                new_result = Result(result_data=visual_type, user=current_user)
                db.session.add(new_result)
                db.session.commit()

            else:
                session['result'] = visual_type

            previous_result = None
            if current_user.is_authenticated:
                if current_user.results:
                    previous_result = current_user.results[-1].result_data

            return render_template('views.test_result.html', visual_type=visual_type, previous_result=previous_result)
        
    # Render a template with the result
    return render_template('views.test_result.html', user=current_user)

@auth.route('/previous_result/<int:username>', methods=['GET'])
@login_required
def previous_result(username):
    user = User.query.filter_by(username=username).first()
    if user:
        previous_result = user.result.result_data if user.result else None
        return render_template('views.test_result.html', previous_result=previous_result)
    else:
        flash('User not found', category='error')
        return redirect(url_for('views.home'))

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))  

app = Flask(__name__)
 
UPLOAD_FOLDER = 'static/uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
 
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
     
@auth.route('/color', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #print('upload_image filename: ' + filename)
        print('Filename:', filename)
        flash('Image successfully uploaded and displayed below')
        return render_template('color_page.html', filename=filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)
 
@auth.route('static/uploads')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='static/uploads/' + filename), code=301)
