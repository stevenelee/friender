from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FileField
from wtforms.validators import InputRequired, Email, Length, URL, Optional


# class CSRFProtection(FlaskForm):
#     """CSRFProtection form, intentionally has no fields."""


class AddImageForm(FlaskForm):
    """Form for adding users."""

    image = FileField(

    )
