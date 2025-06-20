from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from flask_bcrypt import Bcrypt

from flask_login import LoginManager








import requests 
import threading
from flask_jwt_extended import JWTManager
from FlaskBlogApp.api import api  # Import the Blueprint from api.py



app = Flask(__name__)
# Initialize JWT Manager

jwt = JWTManager(app)

# Register the Blueprint with the app
app.register_blueprint(api, url_prefix='/api')

app.config["SECRET_KEY"] = 'b668cbc68d29fd2b7f5976c54c39f6ec'
app.config['WTF_CSRF_SECRET_KEY'] = 'fe9d487ba2c9a1f13a5d72fa0d76d3fb'

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flask_course_database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False



db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)

login_manager.login_view = "login"

login_manager.login_message_category = "warning"

login_manager.login_message = "Παρακαλούμε κάντε login για να μπορέσετε να δείτε αυτή τη σελίδα."







Activity_MicroActs=[]
UserActivities=[]
ActiveActivity=-1


from FlaskBlogApp import routes, models
