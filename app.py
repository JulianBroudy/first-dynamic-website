from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from datetime import datetime


app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = 'secretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
                           InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[
                           InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')


class SignUpForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(
        message='Invalid Email'), Length(max=50)])
    username = StringField('Username', validators=[
        InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[
        InputRequired(), Length(min=8, max=80)])


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


@app.route('/')
def index():
    signup_form = SignUpForm()
    login_form = LoginForm()
    return render_template('index.html', signup_form=signup_form, login_form=login_form)


@app.route('/login', methods=['POST'])
def login():
    signup_form = SignUpForm()
    login_form = LoginForm()

    if login_form.validate_on_submit():
        return "<h1>HI</h1>"
    # handle the login form
    # render the same template to pass the error message
    # or pass `form.errors` with `flash()` or `session` then redirect to /
    return render_template('index.html', signup_form=signup_form, login_form=login_form)


@app.route('/signup', methods=['POST'])
def register():
    signup_form = SignUpForm()
    login_form = LoginForm()

    if signup_form.validate_on_submit():
        username = signup_form.username.data
        email = signup_form.email.data
        password = signup_form.password.data
        new_user = User(username=username, email=email,password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            return render_template('about.html')
            # return redirect('/about')
        except:
            return "Oopsie, there was an error, please try again!"
    # handle the register form
    # render the same template to pass the error message
    # or pass `form.errors` with `flash()` or `session` then redirect to /
    return render_template('index.html', signup_form=signup_form, login_form=login_form)


@app.route('/about')
def about():
    return render_template("about.html")
