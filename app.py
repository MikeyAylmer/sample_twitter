from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Tweet
from forms import UserForm, TweetForm

app = Flask(__name__)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///user_demo_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Sunniva2023'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_ECHO'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.route('/')
def show_homepage():
    """Shows homepage"""
    return render_template('index.html')

@app.route('/tweets', methods=["GET", "POST"])
def show_tweets():
    """Show tweet html"""
    if "user_id" not in session:
        flash('Please Login First')
        return redirect('/')
    form = TweetForm()
    all_tweets = Tweet.query.all()
    if form.validate_on_submit():
        text = form.text.data
        new_tweet = Tweet(text=text, user_id=session["user_id"])
        db.session.add(new_tweet)
        db.session.commit()
        flash("Tweet Created")
        return redirect('/tweets')

    return render_template('tweets.html', form=form, tweets=all_tweets)

@app.route('/tweets/<int:id>', methods=["POST"])
def delete_tweet(id):
    """Delete Tweet"""
    if 'user_id' not in session:
        flash("Please log in first")
        return redirect('/login')
    tweet = Tweet.query.get_or_404(id)
    if tweet.user_id == session["user_id"]:
        db.session.delete(tweet)
        db.session.commit()
        flash("Tweet Deleted")
        return redirect('/tweets')
    flash("You dont have permission to do that")
    return redirect('/tweets')

@app.route('/register', methods=["GET", "POST"])
def register_useer():
    """Define register route"""
    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        new_user = User.register(username, password)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        flash('Welcome, Successfuly Created Your Account!')
        return redirect('/tweets')
    return render_template('register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login_user():
    """creates template for authentication"""
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back! {user.username}")
            session['user_id'] = user.id
            return redirect('/tweets')
        else:
            form.username.errors = ["Invalid Username/Password."]

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('user_id')
    flash('Goodbye!')
    return redirect('/')