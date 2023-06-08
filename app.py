import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, session, g, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import SignUpForm, LoginForm, CSRFProtection
from models import db, connect_db, User
from utils import upload_image

load_dotenv()

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
print(os.environ['DATABASE_URL'])
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
toolbar = DebugToolbarExtension(app)

connect_db(app)

##############################################################################
# Homepage and error pages
# @app.get('/')
# def homepage():
#     """Show homepage:

#     - anon users: login/signup message
#     - logged in: two lists of users:
#                     1. users who have chosen match status:yes
#                     2. users with status:unanswered
#     """


#############################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


@app.before_request
def add_csrf_only_form():
    """Add a CSRF-only form so that every route can use it."""

    g.csrf_form = CSRFProtection()


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.username


def do_logout():
    """Log out user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]





@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    do_logout()

    form = SignUpForm()

    if form.validate_on_submit():
        if request.files['image']:
            db_image_url = upload_image(request.files['image'], form.username.data)
        else: db_image_url = User.image_url.default.arg
        try:
            user = User.signup(
                username=form.username.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                password=form.password.data,
                hobbies=form.hobbies.data,
                interests=form.interests.data,
                zipcode=form.zipcode.data,
                friend_radius=form.friend_radius.data,
                image_url=db_image_url
            )
            db.session.commit()

        except IntegrityError:
            # todo: add flash to templates
            flash("Username already taken", 'danger')
            return render_template('signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('signup.html', form=form)



@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login and redirect to homepage on success."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            form.username.data,
            form.password.data,
        )

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form)


@app.route('/', methods=["GET", "POST"])
def homepage():
    """Show user users who want to match with them or who they might
    want to match with"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return render_template("not-user-home.html")

    distance = g.user.friend_radius
    zipcode - g.user.zipcode



