from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from clarifai.rest import ClarifaiApp
import sys
from PIL import Image
from wordcloud import WordCloud
from io import BytesIO
import base64
import os


app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = 'secretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

clariApp = ClarifaiApp(api_key='42e02d92f61c4c8b9ced1dd81065df1b')
model = clariApp.public_models.general_model

uploads_dir = os.path.join(app.instance_path, 'uploads')
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(
        message='Invalid Email'), Length(max=50)])
    password = PasswordField('Password', validators=[
        InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')


class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[InputRequired(), Email(
        message='Invalid Email'), Length(max=50)])
    password = PasswordField('Password', validators=[
        InputRequired(), Length(min=8, max=80)])


@app.route('/')
def index():
    signup_form = SignUpForm()
    login_form = LoginForm()
    return render_template('index.html', signup_form=signup_form, login_form=login_form, show_signup=False)


@app.route('/login', methods=['GET', 'POST'])
def login():
    signup_form = SignUpForm()
    login_form = LoginForm()

    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user:
            if user.password == login_form.password.data:
                login_user(user, remember=login_form.remember.data)
                return redirect(url_for('dashboard'))
            flash("Incorrect password.", "login_flashes")
        else:
            flash("E-mail doesn not exist.", "login_flashes")

    return render_template('index.html', signup_form=signup_form, login_form=login_form, show_signup=False)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    signup_form = SignUpForm()
    login_form = LoginForm()

    if signup_form.validate_on_submit():
        username = signup_form.username.data
        email = signup_form.email.data
        password = signup_form.password.data
        new_user = User(username=username, email=email, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Thanks for registering', "register_flashes")
            login_user(new_user)
            return redirect(url_for('dashboard'))
        except IntegrityError:
            db.session.rollback()
            flash("E-mail already exists. Log-in instead.", "signup_flashes")

    return render_template('index.html', signup_form=signup_form, login_form=login_form, show_signup=True)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html", username=current_user.username)


@app.route('/generator', methods=['GET', 'POST'])
@login_required
def generator():
    return render_template("generator.html")


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == "POST":
        if request.files:
            image = request.files["image"]
            app.logger.info(image.filename)
            if image.filename != "":
                image.save(os.path.join(uploads_dir, image.filename))
                response = model.predict_by_filename(
                    os.path.join(uploads_dir, image.filename))
                resulting_concepts = response['outputs'][0]['data']['concepts']
                concepts = dict()
                for concept in resulting_concepts:
                    concepts[concept['name']] = concept['value']
                app.logger.info(concepts)
                cloud = WordCloud().generate_from_frequencies(concepts)
                image = BytesIO()
                cloud.to_image().save(image, 'PNG')
                img_str = base64.b64encode(image.getvalue())
                return render_template("generator.html", image=img_str.decode('utf-8'))
    return render_template("generator.html")


@ app.route('/logout')
@ login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
