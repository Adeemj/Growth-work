from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.fields.html5 import DateField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from images_query_interface.models import User


class QueryForm(FlaskForm):

    tar_name = StringField('Target name', )

    jd_min = DecimalField('Min JD')
    jd_max = DecimalField('Max JD')

    filter_used = StringField('Filter Used')

    date_observed = DateField('Date Observed',format='%d/%m/%Y')

    exposure_min = DecimalField('Min Exposure')
    exposure_max = DecimalField('Max Exposure')

    air_mass_min = DecimalField('Min Air Mass')
    air_mass_max = DecimalField('Max Air Mass')

    ccd_temp_min = DecimalField('Min CCD Temp')
    ccd_temp_max = DecimalField('Max CCD Temp')

    ra = DecimalField('RA')
    dec = DecimalField('DEC')

    query = SubmitField('Query Targets')


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                    validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class NightDate(FlaskForm):
    date = DateField('Date',format='%d/%m/%Y')
    submit = SubmitField('Generate Nightly')

