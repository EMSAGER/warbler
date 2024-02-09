from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, Length, Optional

class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail',validators=[DataRequired(), Email(message='Invalid email')])
    password = PasswordField('Password', validators=[Length(min=6)])
    location = StringField("Location", validators=[DataRequired()])
    bio = StringField("(Optional)Bio")
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UserEditForm(FlaskForm):
    """Form for editing users"""
    username = StringField('Username')
    email = StringField('E-mail',validators=[Optional(), Email(message='Invalid email')])
    image_url = StringField('Image URL')
    header_image_url = StringField('Header Image URL')
    bio = StringField("(Optional)Bio")
    password = PasswordField('Password')
    
class LikeForm(FlaskForm):
    """the purpose of this form is to pass CSRF TOKEN through"""
    pass
    

    