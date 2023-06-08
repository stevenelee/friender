import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, session, g, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import SignUpForm
from utils import upload_image

load_dotenv()

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
toolbar = DebugToolbarExtension(app)

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


##############################################################################
# User signup/login/logout
@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = SignUpForm()

    if form.validate_on_submit():
        upload_image(request.files['image'], form.username.data)
        # try:

        # except IntegrityError:
        #     flash("Username already taken", 'danger')
        #     return render_template('users/signup.html', form=form)

        # do_login(user)

        # return redirect("/")

    else:
        return render_template('form.html', form=form)


# @app.post('/')
# def upload_image():
#     """Test upload of Image to S3.
#     """
#     print("printing request.files", request.files['image'])
#     new_file = request.files['image']

#     upload_file(new_file, "s3://jstern-friendly")

#     # g.image = request.files.

#     # upload_file(file)
#     return redirect('/')


