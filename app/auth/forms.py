from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp
from ..models import User
from flask_login import current_user

_Pwd_diff = 'Two passwords not match.'


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log In')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z]\w*$', 0,
                                                                                         'Username only have letters, numbers or underscores.')])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password',
                              validators=[DataRequired(), EqualTo('password', message=_Pwd_diff)])
    register = SubmitField('Register')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username has been in use.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email has existed.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    new_password2 = PasswordField('Confirm New Password',
                                  validators=[DataRequired(), EqualTo('new_password', message=_Pwd_diff), ])
    submit = SubmitField('Update Password')

    def validate_old_password(self, field):
        if not current_user.check_password(field.data):
            raise ValidationError('Old password not correct.')

    def validate_new_password(self, field):
        if field.data == self.old_password.data:
            raise ValidationError('New Password is equal to the old.')


class RequestResetPassword(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Request')

    # def validate_email(self, field):
    #     if not current_user.query.filter_by(email=field.data).first():
    #         raise ValidationError('The email not existed.')


class ResetPasswordForm(FlaskForm):
    user_id = HiddenField('user_id', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    new_password2 = PasswordField('Confirm New Password',
                                  validators=[DataRequired(), EqualTo('new_password', message=_Pwd_diff)])

    submit = SubmitField('Reset Password')
