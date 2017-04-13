from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField, TextAreaField
from wtforms import ValidationError
from wtforms.validators import Length, DataRequired, Email, Regexp
from ..models import Role, User
from flask_pagedown.fields import PageDownField


class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = StringField('About me', validators=[Length(0, 64)])
    submit = SubmitField('Save')


class AdminEditProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z]\w*$', 0,
                                                                                         'Username only have letters, numbers or underscores.')])
    name = StringField('Name', validators=[Length(0, 64)])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = StringField('About me', validators=[Length(0, 64)])
    submit = SubmitField('Save')

    def __init__(self, user, *args, **kwargs):
        super(AdminEditProfileForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if self.user.email != field.data and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email has existed.')

    def validate_username(self, field):
        if self.user.username != field.data and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username has been in use.')


class EditPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 48)])
    summary = TextAreaField('Summary', validators=[Length(0, 256)])
    # content = TextAreaField('Content', validators=[DataRequired()])
    content = PageDownField('Content', validators=[DataRequired()])
    submit = SubmitField('Publish')


class EditCommentForm(FlaskForm):
    content = TextAreaField('Enter your comment', validators=[DataRequired(), Length(1, 256)])
    submit = SubmitField('Submit')
