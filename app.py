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
def register():
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
            return redirect(url_for('dashboard'))
        except IntegrityError:
            db.session.rollback()
            flash("E-mail already exists. Log-in instead.", "signup_flashes")

    return render_template('index.html', signup_form=signup_form, login_form=login_form, show_signup=True)


@app.route('/image_to_cloud')
@login_required
def image_to_cloud():
    response = model.predict_by_filename('static/images/cat.jpg')
    # get_relevant_tags('static/images/cat.jpg')
    # print(response, file=sys.stdout)
    resulting_concepts = response['outputs'][0]['data']['concepts']
    concepts = dict()
    words_list = list()
    for concept in resulting_concepts:
        # app.logger.info(concept['name'], concept['value'])
        concepts[concept['name']] = concept['value']
        words_list.append(concept['name'])
    # app.logger.info(resulting_concepts)
    # app.logger.info(concepts)
    app.logger.info(words_list)

    # cloud = WordCloud().generate((" ").join(words_list))
    # cloud = WordCloud().generate_from_frequencies(concepts)
    # image = BytesIO()
    # cloud.to_image().save(image, 'PNG')
    # img_str = base64.b64encode(image.getvalue())

    # return render_template("image_to_cloud.html", image=img_str.decode('utf-8'))
    return render_template("image_to_cloud.html")



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/about')
def about():
    return render_template("about.html")
