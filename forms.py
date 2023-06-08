from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FileField, IntegerField
from wtforms.validators import InputRequired, Email, Length, Regexp, NumberRange


# class CSRFProtection(FlaskForm):
#     """CSRFProtection form, intentionally has no fields."""


class SignUpForm(FlaskForm):
    """Form for new users to sign up."""

    username = StringField(
        'Username',
        validators=[InputRequired(), Length(min=1,max=30)],
    )

    email = StringField(
        'Email',
        validators=[InputRequired(), Email(), Length(min=1,max=50)],
    )

    password = PasswordField(
        'Password',
        validators=[InputRequired(), Length(min=6, max=50)],
    )

    first_name = StringField(
        'First Name',
        validators=[InputRequired(), Length(min=1,max=30)],
    )

    last_name = StringField(
        'Last Name',
        validators=[InputRequired(), Length(min=1,max=30)],
    )

    hobbies = TextAreaField(
        'Hobbies',
        validators=[InputRequired(), Length(min=1,max=256)]
    )

    interests = TextAreaField(
        'Interests',
        validators=[InputRequired(), Length(min=1,max=256)]
    )

    zipcode = StringField(
        'Zip Code',
        validators=[InputRequired(), Length(min=5,max=5), Regexp(r'^[0-9]+$')]
    )

    friend_radius = IntegerField(
        'Friend Radius',
        validators=[InputRequired(), NumberRange(min=1, max=50)]
    )

    image = FileField(
        '(Optional) Image'
    )
