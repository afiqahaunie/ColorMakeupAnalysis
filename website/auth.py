from flask import Flask, Blueprint, render_template, redirect, url_for, request, jsonify, flash
from . import db 
from flask import session
from .models import User, Result, Post
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=['POST'])
def login():
       email = request.form.get("email")
       password = request.form.get("password")

       user = User.query.filter_by(email=email).first()
       if user:
          if check_password_hash(user.password, password):
             # Logged in successfully
            return jsonify({'success': True, 'message': 'Logged in!'})
          else:
              # Incorrect password
            return jsonify({'success': False, 'message': 'Password is incorrect.'})
       else: 
         # Email does not exist
        return jsonify({'success': False, 'message': 'Email does not exist.'})

@auth.route("/signup", methods=['POST'])
def signup():
    if request.method == 'POST':
      email = request.form.get("email")
      username = request.form.get("username")
      password1 = request.form.get("password1")
      password2 = request.form.get("password2")

      email_exists = User.query.filter_by(email=email).first()
      username_exists = User.query.filter_by(username=username).first()

      if email_exists:
         return jsonify({'success': False, 'message': 'Email is already used.'})
      elif username_exists:
         return jsonify({'success': False, 'message': 'Username is already used.'})
      elif password1 != password2: 
         return jsonify({'success': False, 'message': 'Passwords don\'t match. Please write again.'})
      elif len(username) < 2:
         return jsonify({'success': False, 'message': 'Username is too short.'})
      elif len(password1) < 5:
         return jsonify({'success': False, 'message': 'Password is too short.'})
      else:
         test_result = session.pop('test_result', None)
         # Delete user's result in session after they sign up

         if test_result:
             new_result = Result(result_data=test_result, user=new_user) # Save user's result in database
             db.session.add(new_result)
             db.session.commit()

         new_user = User(email=email, username=username, password=generate_password_hash(password1, method='pbkdf2:sha256'))
         db.session.add(new_user)
         db.session.commit()
         login_user(new_user, remember=True)
         return jsonify({'success': True, 'message': 'User created!'})

@auth.route("/login", methods=['GET'])
def login_page():
    return render_template("login.html")

@auth.route("/signup", methods=['GET'])
def signup_page():
    return render_template("signup.html")

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
            new_result = Result(result_data=visual_type, user=current_user) # Save user's result in database
            db.session.add(new_result)
            db.session.commit()

        else:
            session['result'] = visual_type # Save user's result in session if they not sign up yet

        previous_result = None
        if current_user.is_authenticated:
            if current_user.results:
                previous_result = current_user.results[-1].result_data

        related_posts =[]
        if previous_result:
            related_posts = Post.query.filter_by(visual_type=previous_result).all()
            # Display related post from community based on user's visual type

        return render_template('views.test_result.html', visual_type=visual_type, previous_result=previous_result, related_posts=related_posts)
        
    # Render a template with the result
    return render_template('views.test_result.html', user=current_user)

@auth.route('/previous_result/<username>', methods=['GET']) 
@login_required
def previous_result(username):
    user = User.query.filter_by(username=username).first()
    if user:
        previous_result = user.result.result_data if user.result else None
        # Fetch result from database and display user's previous result of the test

        related_posts =[]
        if previous_result:
            related_posts = Post.query.filter_by(visual_type=previous_result).all()
            # Display related post from community based on user's visual type

        return render_template('views.test_result.html', previous_result=previous_result, related_posts=related_posts)
    else:
        flash('User not found', category='error')
        return redirect(url_for('views.home'))

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))  


