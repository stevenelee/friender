from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_IMAGE_URL = ""

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    username = db.Column(
        db.String(16),
        primary_key=True,
    )

    email = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.String(256),
        nullable=False,
    )

    first_name = db.Column(
        db.String(50),
        nullable=False,
    )

    last_name = db.Column(
        db.String(30),
        nullable=False,
    )

    hobbies = db.Column(
        db.Text,
        nullable=False,
        default="",
    )

    interests = db.Column(
        db.Text,
        nullable=False,
        default="",
    )

    zipcode = db.Column(
        db.String(5),
        nullable=False,
    )

    friend_radius = db.Column(
        db.Integer,
        nullable=False,
    )

    image_url = db.Column(
        db.String(255),
        nullable=False,
        default=DEFAULT_IMAGE_URL,
    )

    # messages = db.relationship('Message', backref="user", cascade="all, delete-orphan")

    # followers = db.relationship(
    #     "User",
    #     secondary="follows",
    #     primaryjoin=(Follow.user_being_followed_id == id),
    #     secondaryjoin=(Follow.user_following_id == id),
    #     backref="following",
    # )

    # liked_messages = db.relationship('Message',
    #                                  secondary="likes",
    #                                  backref="liking_user")

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"


    @classmethod
    def signup(cls, username, first_name, last_name, email, password,
               hobbies, interests, zipcode, friend_radius,
               image_url=DEFAULT_IMAGE_URL):
        """Sign up user.

        Hashes password and adds user to session.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_pwd,
            hobbies=hobbies,
            interests=interests,
            zipcode=zipcode,
            friend_radius=friend_radius,
            image_url=image_url,
        )

        db.session.add(user)
        return user


    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If this can't find matching user (or if password is wrong), returns
        False.
        """

        user = cls.query.filter_by(username=username).one_or_none()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


    def is_followed_by(self, other_user):
        """Is this user followed by `other_user`?"""

        found_user_list = [
            user for user in self.followers if user == other_user]
        return len(found_user_list) == 1


    def is_following(self, other_user):
        """Is this user following `other_use`?"""

        found_user_list = [
            user for user in self.following if user == other_user]
        return len(found_user_list) == 1


    def is_liking(self, msg):
        """Is this user liking message?"""

        liked_message_list = [
            message for message in self.liked_messages if message == msg]
        return len(liked_message_list) == 1





def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)