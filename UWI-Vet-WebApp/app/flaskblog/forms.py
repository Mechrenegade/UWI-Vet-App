from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User, Student, User2, Comp


class RegistrationForm(FlaskForm):
    username = StringField('Username',
     validators=[DataRequired(), Length(min=2, max =20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    level = SelectField(
        'Authorization Level',
        choices = [('1', 'Admin'), 
        ('2', 'Normal')]
    )

    rotation = SelectField(
        'Designated Rotation',
        choices = [('All', 'All'), 
        ('Anatomic Pathology', 'Anatomic Patholgy'),
        ('Anaesthesiology', 'Anaesthesiology'), 
        ('Clinical Pathology', 'Clinical Pathology'),
        ('Diagnostic Imaging', 'Diagnostic Imaging')]
    )            
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):

        user = User2.query.filter_by(username=username.data).first()

        if user:
            raise ValidationError('That username is taken. Please choose another name')

    def validate_email(self, email):

        user = User2.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError('That email is taken. Please enter another email')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class EvaluateForm(FlaskForm):

    studentID = IntegerField('Student ID', 
                            validators=[DataRequired()])
    attitude = SelectField(u'Attitude', choices = [('5', 'Very Good'),('4', 'Good'), ('3', 'OK'), ('2', 'Passable'), ('1', 'Poor')], validators = [DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')
    next = SubmitField('Save & Continue')
    reset = SubmitField('Reset')


class StudentSearchForm(FlaskForm):

    studentID = IntegerField('Student ID')
    name = StringField('Name')
    enrolyear = StringField('Enrolment Year')
    search = SubmitField('Search')

class RotationForm(FlaskForm):
    studentID = IntegerField('Student ID')
    competency = IntegerField('Competency ID')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
     validators=[DataRequired(), Length(min=2, max =20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    
    password = PasswordField('New Password')
    confirm_password = PasswordField('Confirm New Password', 
                                    validators=[EqualTo('password')])
    
    picture = FileField('Upload a Picture', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User2.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose another name')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User2.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please enter another email')

class ChangePasswordForm(FlaskForm):
    
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', 
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):

        user = User2.query.filter_by(email=email.data).first()

        if user is None:
            raise ValidationError('There is no account with that email')
        
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class NewCompForm(FlaskForm):
    compid = StringField('Competancy ID', validators=[DataRequired()])
    content = TextAreaField('Description', validators=[DataRequired()])
    rotation = SelectField(
        'Rotation',
        choices = [ 
        ('Anatomic Pathology', 'Anatomic Patholgy'),
        ('Anaesthesiology', 'Anaesthesiology'), 
        ('Clinical Pathology', 'Clinical Pathology'),
        ('Diagnostic Imaging', 'Diagnostic Imaging')]
    ) 
    

    submit = SubmitField('Submit')

    def validate_compid(self, compid):

        comp = Comp.query.filter_by(id=compid.data).first()

        if comp:
            raise ValidationError('That Competancy ID is taken. Please enter another. Hint: abriviate the first two letters of the rotation name followed by the last number in the database(Check the Rotation table)')

class EditCompForm(FlaskForm):
   
    content = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')
