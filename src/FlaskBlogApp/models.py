from FlaskBlogApp import db, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(36), nullable=False)
    profile_image = db.Column(db.String(30), default='default_profile_image.jpg')
    usergroup = db.Column(db.String(15),default='student')    
    articles = db.relationship('Article', backref='author', lazy=True)
    activities = db.relationship('Activities', backref='author', lazy=True)    
    workingStatus = db.relationship('WorkingSessions', backref='useremail')
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def __repr__(self):
        return f"{self.username}: {self.email}"


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_title = db.Column(db.String(50), nullable=False)
    article_body = db.Column(db.Text(), nullable=False)
    article_image = db.Column(db.String(30), nullable=False, default='default_article_image.jpg')
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"{self.date_created}: {self.article_title}"

class Activities(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_title = db.Column(db.String(50), nullable=False)
    activity_body = db.Column(db.Text(), nullable=False)
    activity_ctrl_sketch = db.Column(db.Text(), nullable=False, default='NOTHING')
    activity_image = db.Column(db.String(30), nullable=False, default='default_activity_image.jpg')
    activity_microacts = db.Column(db.String(250), nullable=False, default='Nothing')
    activity_ml_model = db.Column(db.Text(), nullable=True)  # New field accepting big number of characters and nullable
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(10), nullable=True)
    activity_metadata = db.Column(db.Text, nullable=True)


    def __repr__(self):
        return f"{self.date_created}: {self.activity_title}"

class ActiveActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer,nullable=False)
    user_microacts=db.Column(db.String(250), nullable=False,default='Nothing')
    
    def __repr__(self):
        return f"{self.activity_id}: {self.user_microacts}"        

class MicroActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(50), nullable=False)
    instructions=db.Column(db.String(250))
    
    def __repr__(self):
        return f"{self.name}: {self.instructions}"

class Actions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    PIN8 = db.Column(db.Boolean, unique=False)
    PIN7 = db.Column(db.Boolean, unique=False)
    PIN6 = db.Column(db.Boolean, unique=False)
    PIN5 = db.Column(db.Boolean, unique=False)
    PIN4 = db.Column(db.Boolean, unique=False)
    PIN3 = db.Column(db.Boolean, unique=False)
    PIN2 = db.Column(db.Boolean, unique=False)
    PIN1 = db.Column(db.Boolean, unique=False)
    pot1 = db.Column(db.Integer, nullable=False, default=0)
    pot2 = db.Column(db.Integer, nullable=False, default=0)
    pot3 = db.Column(db.Integer, nullable=False, default=0)
    
    def __repr__(self):
        return f"{self.PIN1}: {self.PIN2}: {self.PIN3}: {self.PIN4}: {self.PIN5}: {self.PIN6}: {self.PIN7}: {self.PIN8}" 

class WorkingSessions(db.Model):
    email = db.Column(db.String(150), db.ForeignKey('user.email'), primary_key=True)    
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    workingStatus = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"{self.workingStatus}"

class AppConfiguration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ActiveActivity = db.Column(db.Integer, unique=False)
    ShadowController = db.Column(db.Boolean, unique=False)
    Activity_MicroActs = db.Column(db.String(250), nullable=False, default='Nothing')
    UserActivities = db.Column(db.String(250), nullable=False, default='Nothing')
    BookingSystem = db.Column(db.Boolean, unique=False)
    TimerMinutes = db.Column(db.Integer, unique=False)
    DebugLevel = db.Column(db.Integer, unique=False)  # New field for DebugLevel
    UsexAPI = db.Column(db.Boolean, unique=False)  # New field for UsexAPI
    UseAI = db.Column(db.Boolean, unique=False)  # New field for AI assessment
    ApplicationLanguage = db.Column(db.String(50), nullable=False, default='English')  # New field for ApplicationLanguage

    # New field for Board
    Board = db.Column(db.String(50), nullable=False, default='Option 1')  # Default value, adjust as needed

    def __repr__(self):
        return (
            f"{self.id}: {self.ActiveActivity} {self.ShadowController} {self.Activity_MicroActs} "
            f"{self.UserActivities} {self.BookingSystem} {self.TimerMinutes} {self.DebugLevel} "
            f"{self.UsexAPI} {self.UseAI} {self.ApplicationLanguage} {self.Board}"
        )





class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    user_email = db.Column(db.String(150), db.ForeignKey('user.email'), nullable=False)    
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    __table_args__ = (db.UniqueConstraint('date', 'start_time', name='_date_timeslot_uc'),)

    def __repr__(self):
        return f"{self.user_email}: {self.date} {self.start_time} {self.end_time}"


class UserLastSketchUploaded(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), nullable=False)
    last_sketch = db.Column(db.Text(), nullable=False)
    date_uploaded = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<UserLastSketchUploaded {self.id}>"

class GlobalsTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    LaunchId = db.Column(db.Text, nullable=False)

class LanguageConvertions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    greek_chars = db.Column(db.String(200), nullable=True)
    english_chars = db.Column(db.String(200), nullable=True)
    spanish_chars = db.Column(db.String(200), nullable=True)
    french_chars = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"ID: {self.id}, Greek Chars: {self.greek_chars}, English Chars: {self.english_chars}, Spanish Chars: {self.spanish_chars}, French Chars: {self.french_chars}"

class T1_GeneralMeta(db.Model):  # Use 'Model' with a capital 'M'
    __tablename__ = "t1_general_meta" 
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    terms_of_service_url = db.Column(db.String(500), nullable=False)
    contact_email = db.Column(db.String(255), nullable=False)
    license = db.Column(db.String(100), nullable=False)
    license_url = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"<T1_GeneralMeta(id={self.id}, title='{self.title}', contact_email='{self.contact_email}')>"

class t2_binding_metadata(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    basePath = db.Column(db.String, nullable=False)
    apis = db.Column(db.Integer, nullable=False, default=0)
    models = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f'<t2_binding_metadata {self.id}, {self.basePath}, {self.apis}, {self.models}>'