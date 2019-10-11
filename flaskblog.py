from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm, UpdateAccountForm
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
#from flaskblog import db, login_manager
from flask_login import UserMixin

from flask import render_template, url_for, flash, redirect, request
from flask_bcrypt import  Bcrypt
#from flaskblog.forms import RegistrationForm, LoginForm
#from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #title = db.Column(db.String(100), nullable=False)
    #date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    q1 = db.Column(db.Text, nullable=False)
    q2 = db.Column(db.Text, nullable=False)
    q3 = db.Column(db.Text, nullable=False)
    q4 = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.q1}', '{self.q2}', '{self.q3}', '{self.q4}')"

"""
posts = [
    {
        'author': 'Anu',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'Oct 11, 2019'
    },
    {
        'author': 'Sri',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'Oct 11, 2019'
    }
]
"""

@app.route("/")
@app.route("/home")
def home():
    posts=Post.query.all()
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        post = Post(q1=form.q1.data,q2=form.q2.data,q3=form.q3.data,q4=form.q4.data,author=current_user)
        db.session.add(post)
        db.session.commit()
    

        return redirect(url_for('home'))
    return render_template('account.html', title='Account', form=form)


if __name__ == '__main__':
    app.run(debug=True)