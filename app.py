import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, session, g, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import or_, and_, not_
from sqlalchemy.exc import IntegrityError

from forms import SignUpForm, LoginForm, CSRFProtection
from models import db, connect_db, User, Match
from utils import upload_image, get_zipcodes

load_dotenv()

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
toolbar = DebugToolbarExtension(app)

connect_db(app)


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
            flash("Username/email already taken", 'danger')
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


@app.post("/logout")
def logout():
    """logout user and redirect to login page. Show success or unauthorized
    message"""

    form = g.csrf_form

    if not form.validate_on_submit() or not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect("/")


##############################################################################
# User routes
# @app.get('/')
# def homepage():
#     """Show homepage:

#     - anon users: login/signup message
#     - logged in:
#     """

@app.post("/users/<username>/no-match")
def no_match(username):
    """route for when there isn't a match"""

    form = g.csrf_form

    if not form.validate_on_submit() or not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    match = Match(
                user_being_matched=username,
                user_matching=g.user.username,
                match_status=False,
    )

    db.session.add(match)
    db.session.commit()

    return redirect("/")


@app.post("/users/<username>/match")
def match(username):
    """route for when there is a match"""

    form = g.csrf_form

    if not form.validate_on_submit() or not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    match = Match(
                user_being_matched=username,
                user_matching=g.user.username,
                match_status=True,
    )

    db.session.add(match)
    db.session.commit()

    return redirect("/")


@app.get('/users/<username>/potential-matches')
def potential_matches(username):
    """Show other users who want to be friends"""

    if g.user:

        matches_list = (Match
                  .query
                  .join(User, User.username == Match.user_being_matched)
                  .filter(Match.match_status.is_(True))
                  .all())
        matches = User.query.filter(User.username.in_(
            [m.user_matching for m in matches_list])).filter(
            User.username.not_in([m.user_being_matched for m in matches_list])).all()
        return render_template("potential-matches.html", matches=matches)

    else:
        return render_template("not-user-home.html")


@app.get('/users/<username>/matches')
def matches(username):
    """Show matches/friends"""

    if g.user:

        # matches_list = (Match
        #           .query
        #           .filter
        #           (and_(and_(Match.user_being_matched == username,
        #                        Match.match_status.is_(True))),
        #                (and_(Match.user_matching == username,
        #                        Match.match_status.is_(True))))
        #           .all())

        matches_list1 = (Match
                  .query
                  .filter
                    (and_(Match.user_being_matched == username,
                               Match.match_status.is_(True)))
                  .all())

        matches_list2 = (Match
                  .query
                  .filter
                    (and_(Match.user_matching == username,
                               Match.match_status.is_(True)))
                  .all())

        matches_list3 = []
        for match in matches_list1:
            name1 = match.user_matching
            for match in matches_list2:
                name2 = match.user_being_matched
                if name1 == name2:
                    matches_list3.append(name1)

        matches = []
        for name in matches_list3:
            matches.append(User.query.get(name))

        # matches = User.query.filter(User.username.in_([m.user_matching for m in matches_list])).all()
        # breakpoint()
        return render_template("matches.html", matches = matches)

    else:
        return render_template("not-user-home.html")


##############################################################################
# Homepage and error pages

@app.get('/')
def homepage():
    """Show user users who want to match with them or who they might
    want to match with"""

    if g.user:
        distance = g.user.friend_radius
        zipcode = g.user.zipcode
        friend_zipcodes = get_zipcodes(distance, zipcode)

        matches = (User
                   .query
                   .filter(and_(User.username != g.user.username,
                            (or_(User.zipcode.in_(friend_zipcodes), User.zipcode == zipcode))))
                   .limit(10)
                   .all())

        return render_template("user-home.html", matches=matches)


    else:
        return render_template("not-user-home.html")



