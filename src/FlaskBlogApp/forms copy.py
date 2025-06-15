from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, DateTimeField, SelectMultipleField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from FlaskBlogApp.models import User, Booking
from flask_login import current_user



def maxImageSize(max_size=2):
   max_bytes = max_size * 1024 * 1024
   def _check_file_size(form, field):
      if len(field.data.read()) > max_bytes:
         raise ValidationError(f'Το μέγεθος της εικόνας δε μπορεί να υπερβαίνει τα {max_size} MB')

   return _check_file_size




def validate_email(form, email):
   user = User.query.filter_by(email=email.data).first()
   if user:
      raise ValidationError('Αυτό το email υπάρχει ήδη!')


class SignupForm(FlaskForm):
    username = StringField(label="Username",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."),
                                       Length(min=3, max=15, message="Αυτό το πεδίο πρέπει να είναι από 3 έως 15 χαρακτήρες")])

    email = StringField(label="email",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."), 
                                       Email(message="Παρακαλώ εισάγετε ένα σωστό email"), validate_email])

    password = StringField(label="password",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."),
                                       Length(min=3, max=15, message="Αυτό το πεδίο πρέπει να είναι από 3 έως 15 χαρακτήρες")])
    
    password2 = StringField(label="Επιβεβαίωση password",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."),
                                       Length(min=3, max=15, message="Αυτό το πεδίο πρέπει να είναι από 3 έως 15 χαρακτήρες"),
                                       EqualTo('password', message='Τα δύο πεδία password πρέπει να είναι τα ίδια')])
    
    submit = SubmitField('Εγγραφή')


    def validate_username(self, username):
      user = User.query.filter_by(username=username.data).first()
      if user:
         raise ValidationError('Αυτό το username υπάρχει ήδη!')




class LoginForm(FlaskForm):
 
    email = StringField(label="email",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."), 
                                       Email(message="Παρακαλώ εισάγετε ένα σωστό email")])

    password = StringField(label="password",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό.")])
    
    remember_me = BooleanField(label="Remember me")

    submit = SubmitField('Είσοδος')



class NewArticleForm(FlaskForm):
    article_title = StringField(label="Τίτλος Σχεδίου (χωρίς κενά)",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."),
                                       Length(min=3, max=50, message="Αυτό το πεδίο πρέπει να είναι από 3 έως 50 χαρακτήρες")])

    article_body = TextAreaField(label="Κώδικας Σχεδίου",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."), 
                                       Length(min=5, message="Το κείμενο του άρθρου πρέπει να έχει τουλάχιστον 5 χαρακτήρες")])
    
    article_image = FileField('Εικόνα Άρθρου', validators=[Optional(strip_whitespace=True),
                                                           FileAllowed([ 'jpg', 'jpeg', 'png' ],
                                                            'Επιτρέπονται μόνο αρχεία εικόνων τύπου jpg, jpeg και png!'),
                                                           maxImageSize(max_size=2)])

    submit = SubmitField('Αποστολή')

class NewActivityForm(FlaskForm):
    activity_title = StringField(label="Activity Title",
                           validators=[DataRequired(message="This field can't be empty."),
                                       Length(min=3, max=50, message="This field must have 3 to 50 characters")])

    activity_body = TextAreaField(label="Activity Description",
                           validators=[DataRequired(message="This field can't be empty."), 
                                       Length(min=4, message="Activity description must be at least 5 characters")])
    
    activity_ctrl_sketch = TextAreaField(label="Shadow microcontroller sketch.",
                           validators=[DataRequired(message="This field can't be empty."), 
                                       Length(min=4, message="Sketch characters are to few")])                                   
    
    activity_image = FileField("Activitys' Image", validators=[Optional(strip_whitespace=True),
                                                           FileAllowed([ 'jpg', 'jpeg', 'png' ],
                                                            'Allowed image types jpg, jpeg and png!'),
                                                           maxImageSize(max_size=2)])

    activity_microacts=TextAreaField(label="Microactivities path",
                           validators=[DataRequired(message="This field can't be empty."), 
                                       Length(min=4, message="Microactivities path must be have at least 5 characters")])
   
    activity_ml_model = TextAreaField(label="Machine Learning Model", validators=[Optional()])

    activity_type = StringField('Activity Type', validators=[Length(max=10)])
    
    submit = SubmitField('Submit')

    





class AccountUpdateForm(FlaskForm):
    username = StringField(label="Username",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."),
                                       Length(min=3, max=15, message="Αυτό το πεδίο πρέπει να είναι από 3 έως 15 χαρακτήρες")])

    email = StringField(label="email",
                           validators=[DataRequired(message="Αυτό το πεδίο δε μπορεί να είναι κενό."), 
                                       Email(message="Παρακαλώ εισάγετε ένα σωστό email")])

    profile_image = FileField('Εικόνα Προφίλ', validators=[Optional(strip_whitespace=True),
                                                           FileAllowed([ 'jpg', 'jpeg', 'png' ],
                                                            'Επιτρέπονται μόνο αρχεία εικόνων τύπου jpg, jpeg και png!'),
                                                           maxImageSize(max_size=2)])
   
    submit = SubmitField('Αποστολή')


    def validate_username(self, username):
      if username.data != current_user.username:
         user = User.query.filter_by(username=username.data).first()
         if user:
            raise ValidationError('Αυτό το username υπάρχει ήδη!')

    def validate_email(self, email):
      if email.data != current_user.email:
         user = User.query.filter_by(email=email.data).first()
         if user:
            raise ValidationError('Αυτό το email υπάρχει ήδη!')


class ActionsForm(FlaskForm):   
   PIN8 = BooleanField(label="GPIO")
   PIN7 = BooleanField(label="GPIO")
   PIN6 = BooleanField(label="GPIO")
   PIN5 = BooleanField(label="GPIO")
   PIN4 = BooleanField(label="GPIO")
   PIN3 = BooleanField(label="GPIO")
   PIN2 = BooleanField(label="GPIO")
   PIN1 = BooleanField(label="GPIO")
   submit = SubmitField('Υποβολή')

class BookingForm(FlaskForm):
   date = StringField('Ημερομηνία κράτησης', validators=[DataRequired()])
   start_hour = SelectField('Ώρα έναρξης', choices=[(i, f'{i:02d}') for i in range(24)], coerce=int)
   submit = SubmitField('Κράτηση')


class AppConfigurationForm(FlaskForm):
    active_activity = StringField('Active Activity', validators=[DataRequired()])
    shadow_controller = SelectField('Shadow Controller', choices=[(0, 'False'), (1, 'True')], coerce=int)
    activity_micro_acts = StringField('Activity Micro Acts', default='Nothing')
    user_activities = StringField('User Activities', default='Nothing')
    booking_system = SelectField('Booking System', choices=[(0, 'False'), (1, 'True')], coerce=int)
    timer_minutes = StringField('Timer Minutes', validators=[DataRequired()])
    debug_level = StringField('Debug Level', validators=[DataRequired()])
    usex_api = SelectField('Usex API', choices=[(0, 'False'), (1, 'True')], coerce=int)
    use_ai = SelectField('Use AI', choices=[(0, 'False'), (1, 'True')], coerce=int)    
    application_language = SelectField('Application Language', choices=[('Greek','Greek'),('English', 'English'), ('Spanish', 'Spanish'), ('French', 'French')])  # Adjust choices accordingly
    
    submit = SubmitField('Αποθήκευση')


class UserGroupForm(FlaskForm):
    usergroup = SelectField('Usergroup', choices=[('student', 'Student'), ('admin', 'Admin')], validators=[DataRequired()])

class DeleteBookingForm(FlaskForm):
    selected_bookings = SelectMultipleField('Selected Bookings', coerce=int, validators=[DataRequired()])
    delete_button = SubmitField('Delete')

    def __init__(self, *args, **kwargs):
        super(DeleteBookingForm, self).__init__(*args, **kwargs)
        self.selected_bookings.choices = [(booking.id, f"Booking {booking.id}") for booking in Booking.query.all()]


class MicroactivityForm(FlaskForm):
    id = HiddenField()
    name = StringField('Name', validators=[DataRequired()])
    instructions = TextAreaField('Instructions', validators=[DataRequired()])
    submit = SubmitField('Save')        

