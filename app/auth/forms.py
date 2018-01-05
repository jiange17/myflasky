from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])

    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Usernames must have only letters, '
                                              'numbers, dots or underscores')])
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])

    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    @staticmethod
    def validate_email(self, field):    # 不能舍去self，实际上会传入该参数，虽然方法里面没有使用它。
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    @staticmethod
    def validate_username(self, field):     # 不能舍去self，实际上会传入该参数，虽然方法里面没有使用它。
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in user.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])

    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('old_password', validators=[DataRequired(), Length(1, 64)])
    new_password = PasswordField('new_password', validators=[DataRequired(), Length(1, 64),
                                 EqualTo('new_password2', message='new_password must match.')])
    new_password2 = PasswordField('new_password2', validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField('Change')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email(), Length(1, 64)])
    submit = SubmitField('Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])

    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Reset')


class ChangeEmailForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email(), Length(1, 64)])
    submit = SubmitField('Reset')

    @staticmethod
    def validate_email(self, field):  # 不能舍去self，实际上会传入该参数，虽然方法里面没有使用它。
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
