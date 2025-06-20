from flask import (render_template,
                   redirect,
                   url_for,
                   request,
                   flash, 
                   abort,
                   Response,
                   jsonify,
                   sessions)
from FlaskBlogApp import api  # Import the Blueprint from api.py
from FlaskBlogApp import app, db, bcrypt, Activity_MicroActs,ActiveActivity,UserActivities
from FlaskBlogApp.forms import SignupForm, LoginForm, NewArticleForm, AccountUpdateForm, ActionsForm 
from FlaskBlogApp.forms import NewActivityForm, BookingForm, AppConfigurationForm, UserGroupForm, DeleteBookingForm
from FlaskBlogApp.models import User, Article, Activities, MicroActivity, Actions, WorkingSessions, AppConfiguration, Booking, MicroActivity, UserLastSketchUploaded, GlobalsTable, LanguageConvertions
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import or_
import secrets, os, subprocess
from os import path
import requests
import socket 
from PIL import Image
import time
from datetime import datetime, date, timedelta, time as time_
import threading
import FlaskBlogApp.mylrs as mylrs
import FlaskBlogApp.ml as ml
import os
import pprint
import serial
import smbus
#for audio transmition
import pyaudio
import numpy as np
import base64
import sys
import io
from sqlalchemy.exc import IntegrityError

from tempfile import mkdtemp
#from flask import Flask, jsonify, request, render_template, url_for
from flask_caching import Cache
from werkzeug.exceptions import Forbidden
from pylti1p3.contrib.flask import FlaskOIDCLogin, FlaskMessageLaunch, FlaskRequest, FlaskCacheDataStorage
from pylti1p3.deep_link_resource import DeepLinkResource
from pylti1p3.grade import Grade
from pylti1p3.lineitem import LineItem
from pylti1p3.tool_config import ToolConfJsonFile
from pylti1p3.registration import Registration
from flask_apscheduler import APScheduler


import pandas as pd
from pygments.lexers.c_cpp import CppLexer
from pygments.token import Token
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report

@app.route('/serial-experiment-open/')
def open_serial_port():
    global ser
    ttyACM = get_EXPERIMENT_tty()  # You need to define this function
    if ttyACM == "None":
        flash("No Experiment Board found.", "warning")
        return False
    elif ttyACM == "ttyACM0":
        ser = serial.Serial('/dev/ttyACM0', 115200)  # Adjust baud rate as needed
        return True
    elif ttyACM == "ttyACM1":
        ser = serial.Serial('/dev/ttyACM1', 115200)  # Adjust baud rate as needed
        return True
@app.route('/serial-experiment-close/')
def close_serial_port():
    global ser
    ser.close()
    return True

@app.route('/serial-data/')
def serial_data():
    global ser
    # Check if serial port is open, if not, open it
    if ser is None or not ser.is_open:
        if not open_serial_port():
            return jsonify({'data': 'No data available'})
    # Read a line from the serial port
    line = ser.readline().decode().strip()
    # Return the received data as JSON
    return jsonify({'data': line})

#@app.route('/serial-data/')
#def serial_data():
#    # Open the serial port
#    ttyACM=get_EXPERIMENT_tty()        
#    if ttyACM=="None":
#        flash("No Experiment Board found.", "warning")
#        return redirect(url_for('root'))        
#    elif ttyACM=="ttyACM0":
#        ser = serial.Serial('/dev/ttyACM0', 115200)  # Adjust baud rate as needed
#    elif ttyACM=="ttyACM1":
#        ser = serial.Serial('/dev/ttyACM1', 115200)  # Adjust baud rate as needed            
#    try:
#        while True:
#            # Read a line from the serial port
#            line = ser.readline().decode().strip()
#            # Return the received data as JSON
#            return jsonify({'data': line})
#    finally:
#        # Close the serial port
#        ser.close()

@app.route('/serial-shadow-data/')
def serial_shadow_data():
    # Open the serial port
    ttyACM=get_SHADOW_tty()        
    if ttyACM=="None":
        flash("No Shadow Board found.", "warning")
        return redirect(url_for('root'))        
    elif ttyACM=="ttyACM0":
        ser = serial.Serial('/dev/ttyACM0', 9600)  # Adjust baud rate as needed
    elif ttyACM=="ttyACM1":
        ser = serial.Serial('/dev/ttyACM1', 9600)  # Adjust baud rate as needed            
    try:
        while True:
            # Read a line from the serial port
            line = ser.readline().decode().strip()
            # Return the received data as JSON
            return jsonify({'data': line})
    finally:
        # Close the serial port
        ser.close()


@app.route('/getShadowReport2/')
@login_required
def request_report():
    bus = smbus.SMBus(1)
    arduino_address = 0x08
	# Request report from Arduino
    bus.write_byte(arduino_address, ord('r'))  # Sending 'r' to request report
    time.sleep(3)  # Wait for response
        
    # Read the report from Arduino
    report = bus.read_i2c_block_data(arduino_address, 0, 32)  # Assuming max report length is 32 bytes
        
    # Convert bytes to string
    report_str = "".join([chr(byte) for byte in report]).strip()
        
    # Print the received report
    print("Received report from Arduino:", report_str)
    return report_str

@app.route('/getShadowReport/')
@login_required
def read_pins():
    # I2C address of Arduino UNO
    arduino_address = 0x08

    # Open I2C bus
    bus = smbus.SMBus(1)

    # Request data from Arduino
    bus.write_byte(arduino_address, 0)
    time.sleep(0.1)  # Wait for data to be available
    
    # Read the string data from Arduino
    data = bus.read_i2c_block_data(arduino_address, 0, 32)  # Read up to 32 bytes of data
    
    # Split the data into digital and analog parts
    digital_data = data[:12]
    analog_data = data[12:24]  # Limit to only 6 pairs of bytes for 6 analog pins
    
    # Process digital data
    digital_pin_statuses = [int(status) for status in digital_data]
    
    # Process analog data
    analog_pin_values = []
    for i in range(0, len(analog_data), 2):
        value = (analog_data[i] << 8) | analog_data[i+1]
        analog_pin_values.append(value)
    
    # Construct a dictionary containing the data
    data_dict = {
        "digital_pin_statuses": digital_pin_statuses,
        "analog_pin_values": analog_pin_values
    }
    
    # Print the data
    print(data_dict)
    
    # Return the data as JSON
    return data_dict

def clean_records():
    # Calculate the datetime threshold (more than an 25 minutes)
    cleanup_threshold = datetime.utcnow() - timedelta(minutes=25)

    # Define workingStatus values to be cleaned
    working_statuses_to_clean = ['owner', 'moodleowner']

    # Query and delete records based on conditions
    records_to_clean = WorkingSessions.query.filter(
        WorkingSessions.date_created < cleanup_threshold,
        WorkingSessions.workingStatus.in_(working_statuses_to_clean)
    ).all()
    if records_to_clean:
        for record in records_to_clean:
            db.session.delete(record)

        db.session.commit()
        if get_DebugLevel() > 0:
            print("Working Sessions Records cleaned successfully!")
        with app.app_context():    
            InitiateMaintenance()    
    if get_DebugLevel() > 0:
        print("Working Sessions Scheduler")

def update_launch_id(new_launch_id):
    # Update the LaunchId for the record with id=0
    global_record = GlobalsTable.query.filter_by(id=0).first()

    if global_record:
        global_record.LaunchId = new_launch_id
        db.session.commit()
        return True
    else:
        return False

def get_launch_id():
    # Retrieve the LaunchId for the record with id=0
    global_record = GlobalsTable.query.filter_by(id=0).first()
    return global_record.LaunchId if global_record else "NoLaunchId"

def get_Use_xAPI():  
    UseXAPI = AppConfiguration.query.filter_by(id=0).first()
    return UseXAPI.UsexAPI if UseXAPI else 0

def get_Language():  
    Language = AppConfiguration.query.filter_by(id=0).first()
    return Language.ApplicationLanguage

def translate_from_greek(GR_text,ToLanguage):
    TheRAW = LanguageConvertions.query.filter_by(Greek=GR_text).first


def get_DebugLevel():  
    DebugLevel = AppConfiguration.query.filter_by(id=0).first()
    return DebugLevel.DebugLevel if DebugLevel else 0

def get_EXPERIMENT_tty():
    result = "None"  # Default value
    ArdCLIcommand="udevadm info --query=property --name=/dev/ttyACM0 | grep SERIAL_SHORT"    
    cmd_out = subprocess.run( ArdCLIcommand,shell=True,stdout=subprocess.PIPE)
    second_part = cmd_out.stdout.decode().split("=", 1)[1].strip()
    if get_DebugLevel() > 0:
        print(second_part)
    if second_part == "8563334323935131B0D0":
        result="ttyACM0"            
        if get_DebugLevel() > 0:
            print("Experiment board on ttyACM0") 
        return result               
    ArdCLIcommand="udevadm info --query=property --name=/dev/ttyACM1 | grep SERIAL_SHORT"    
    cmd_out = subprocess.run( ArdCLIcommand,shell=True,stdout=subprocess.PIPE)
    second_part = cmd_out.stdout.decode().split("=", 1)[1].strip()
    if get_DebugLevel() > 0:
        print(second_part)
    if second_part == "8563334323935131B0D0":
        result="ttyACM1"            
        if get_DebugLevel() > 0:
            print("Experiment board on ttyACM1") 
        return result               
    if get_DebugLevel() > 0:
        print("ARDUINO EXPERIMENT BOARD NOT FOUND") 
    return result

def get_SHADOW_tty():
    result = "None"  # Default value
    ArdCLIcommand="udevadm info --query=property --name=/dev/ttyACM0 | grep SERIAL_SHORT"    
    cmd_out = subprocess.run( ArdCLIcommand,shell=True,stdout=subprocess.PIPE)
    second_part = cmd_out.stdout.decode().split("=", 1)[1].strip()
    if get_DebugLevel() > 0:
        print(second_part)
    #if second_part == "64934333235351A07241":
    if second_part == "55639303634351509102":    
        #64934333235351A07241
        #55639303634351509102
        result="ttyACM0"            
        if get_DebugLevel() > 0:
            print("Shadow board on ttyACM0") 
        return result               
    ArdCLIcommand="udevadm info --query=property --name=/dev/ttyACM1 | grep SERIAL_SHORT"    
    cmd_out = subprocess.run( ArdCLIcommand,shell=True,stdout=subprocess.PIPE)
    second_part = cmd_out.stdout.decode().split("=", 1)[1].strip()
    if get_DebugLevel() > 0:
        print(second_part)
    #if second_part == "64934333235351A07241":
    if second_part == "55639303634351509102":    
        result="ttyACM1"            
        if get_DebugLevel() > 0:
            print("Shadow board on ttyACM1") 
        return result               
    if get_DebugLevel() > 0:
        print("ARDUINO SHADOW NOT FOUND") 
    return result

def get_ttyACM0_serial():
    result = "None"  # Default value
    ArdCLIcommand="udevadm info --query=property --name=/dev/ttyACM0 | grep SERIAL_SHORT"    
    cmd_out = subprocess.run( ArdCLIcommand,shell=True,stdout=subprocess.PIPE)
    second_part = cmd_out.stdout.decode().split("=", 1)[1].strip()
    if get_DebugLevel() > 0:
        print(second_part)
    if second_part == "8563334323935131B0D0":
        result="ARDUINO_EXPERIMENT"            
        if get_DebugLevel() > 0:
            print("ARDUINO_EXPERIMENT")            
    elif second_part == "55639303634351509102":
        result="ARDUINO_SHADOW"    
        if get_DebugLevel() > 0:
            print("ARDUINO_SHADOW") 
    return result

@app.route('/check_code/')
@login_required
def check_code():
    ActiveActivity = get_ActiveActivity()
    if ActiveActivity==-1:
        flash('Δεν έχει ενεργοποιηθεί δρατηριότητα.', 'success')
        return('-1')
    activity = Activities.query.filter_by(id = ActiveActivity).first()        
    UserSketch = UserLastSketchUploaded.query.filter_by(user_email=current_user.email).first()
    if not UserSketch:
        #flash('Ο χρήστης δε έχει φορτώσει κώδικα στο Arduino UNO.', 'success')
        return('NoUpload')
    if not activity.activity_ml_model:
        #flash('Δεν έχει φορτωθεί μοντέλο μηχανικής μάθησης.', 'success')
        return('NoModelData')    
    if activity:        
        csv_data = activity.activity_ml_model
        data = pd.read_csv(io.StringIO(csv_data), sep='|')
        # Now you have the CSV data in the DataFrame 'df', and you can work with it as usual
        # For example, you can print the DataFrame to see its contents
        #print(data)

        # Step 1: Read data from the CSV file with the delimiter '|'
        data['tokenized_code'] = data['mycode'].apply(tokenize_code)


        # Step 3: Vectorization
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(data['tokenized_code']).toarray()
        y = data['label']


        # Step 4: Train the Decision Tree model
        model = DecisionTreeClassifier()
        model.fit(X, y)


        # Step 5: Read the test_code.ino file and make predictions
        test_code=UserSketch.last_sketch

        # Step 6: Tokenize the test code
        tokenized_test_code = tokenize_code(test_code)


        # Step 7: Vectorize the tokenized test code
        X_test = vectorizer.transform([tokenized_test_code]).toarray()


        # Step 8: Make predictions on the test code
        predicted_label = model.predict(X_test)[0]


        # Step 9: Provide feedback for incorrect predictions
        if predicted_label == 'correct':
            if get_DebugLevel() > 0:
                print("Prediction for test_code.ino: Correct")
            return('Correct')
        else:
            if get_DebugLevel() > 0:
                print("Prediction for test_code.ino: Incorrect")
            return('Incorrect')

        

def tokenize_code(code):
    lexer = CppLexer()
    tokens = lexer.get_tokens(code)

    token_list = []

    for token_type, token_value in tokens:
        if token_type in Token.Name:
            token_list.append('ID')
        elif token_type in Token.Keyword:
            token_list.append(token_value.upper())
        elif token_type in Token.Operator:
            token_list.append(token_value)
        elif token_type in Token.Literal:
            token_list.append(token_value)
        else:
            token_list.append(str(token_type))  # Convert other tokens to strings

    return ' '.join(token_list)







@app.route('/checkbox-states')
@login_required
def get_checkbox_states():
    # Retrieve the checkbox states from the database
    actions = Actions.query.first()  # Assuming there's only one row in the Actions table
    checkbox_states = {
        'checkbox1': actions.PIN1,
        'checkbox2': actions.PIN2,
        'checkbox3': actions.PIN3,
        'checkbox4': actions.PIN4,
        'checkbox5': actions.PIN5,
        'checkbox6': actions.PIN6,
        'checkbox7': actions.PIN7,
        'checkbox8': actions.PIN8
    }

    # Return the checkbox states as a JSON response
    return jsonify(checkbox_states)

@app.route('/get-slider-value/')
@login_required
def get_slider_value():
    # Retrieve the potentiometer state from the database
    actions = Actions.query.first()  # Assuming there's only one row in the Actions table
    slider_value = {
        'pot1': actions.pot1,        
    }

    
    return jsonify(slider_value)



@app.route('/microactivities/')
@login_required
def microactivities():
    microactivities = MicroActivity.query.all()
    return render_template('micro_activities.html', microactivities=microactivities)

@app.route('/save_microactivity/', methods=['POST'])
@login_required
def save_microactivity():
    microactivity_id = request.form['id']
    name = request.form['name']
    instructions = request.form['instructions']

    if microactivity_id:
        microactivity = MicroActivity.query.get(microactivity_id)
        microactivity.name = name
        microactivity.instructions = instructions
    else:
        microactivity = MicroActivity(name=name, instructions=instructions)
        db.session.add(microactivity)

    db.session.commit()

    return redirect('/microactivities/')

@app.route('/edit_microactivity/<int:microactivity_id>')
@login_required
def edit(microactivity_id):
    microactivity = MicroActivity.query.get(microactivity_id)
    microactivities = MicroActivity.query.all()
    return render_template('micro_activities.html', microactivity=microactivity, microactivities=microactivities)

@app.route('/delete_microactivity/<int:microactivity_id>')
@login_required
def delete(microactivity_id):
    microactivity = MicroActivity.query.get(microactivity_id)
    db.session.delete(microactivity)
    db.session.commit()

    return redirect('/microactivities/')



@app.route('/admin_bookings/', methods=['GET', 'POST'])
@login_required
def admin_bookings():
    form = DeleteBookingForm()
    all_bookings = Booking.query.all()

    if form.validate_on_submit():
        selected_bookings = form.selected_bookings.data

        for booking_id in selected_bookings:
            booking = Booking.query.get(booking_id)
            if booking:
                db.session.delete(booking)

        db.session.commit()
        return redirect(url_for('admin_bookings'))

    return render_template('admin_bookings.html', form=form, all_bookings=all_bookings)

@app.route('/user_bookings/', methods=['GET', 'POST'])
@login_required
def user_bookings():
    form = DeleteBookingForm()
    user_bookings = Booking.query.filter_by(user_email=current_user.email).all()
    if get_DebugLevel() > 0:
        print(user_bookings)
    if form.validate_on_submit():
        selected_bookings = form.selected_bookings.data

        for booking_id in selected_bookings:
            booking = Booking.query.get(booking_id)
            if booking:
                db.session.delete(booking)

        db.session.commit()
        return redirect(url_for('user_bookings'))

    return render_template('user_bookings.html', form=form, all_bookings=user_bookings)


@app.route('/change_usergroup/', methods=['GET', 'POST'])
@login_required
def change_usergroup():
    form = UserGroupForm()
    users = User.query.all()

    if request.method == 'POST':
        selected_users = request.form.getlist('selected_users')
        usergroup = form.usergroup.data

        for user_id in selected_users:
            user = User.query.get(user_id)
            if user:
                user.usergroup = usergroup

        db.session.commit()
        return redirect(url_for('change_usergroup'))

    return render_template('change_usergroup.html', form=form, users=users)

@app.route('/config/', methods=['GET', 'POST'])
@login_required
def config():
    config = AppConfiguration.query.filter_by(id=0).first()  # Fetch the existing configuration with id=0
    form = AppConfigurationForm()

    if form.validate_on_submit():
        config.id = 0
        config.ActiveActivity = form.active_activity.data
        config.ShadowController = form.shadow_controller.data
        config.Activity_MicroActs = form.activity_micro_acts.data
        config.UserActivities = form.user_activities.data
        config.BookingSystem = form.booking_system.data
        config.TimerMinutes = form.timer_minutes.data
        config.DebugLevel = form.debug_level.data
        config.UsexAPI = form.usex_api.data
        config.UseAI = form.use_ai.data
        config.ApplicationLanguage = form.application_language.data

        db.session.commit()  # Commit the changes to the database
        flash('Οι ρυθμίσεις αποθηκεύτηκαν με επιτυχία!', 'success')
        return redirect(url_for('config'))

    elif request.method == 'GET':
        form.active_activity.data = config.ActiveActivity
        form.shadow_controller.data = int(config.ShadowController)
        form.activity_micro_acts.data = config.Activity_MicroActs
        form.user_activities.data = config.UserActivities
        form.booking_system.data = int(config.BookingSystem)
        form.timer_minutes.data = int(config.TimerMinutes)
        form.debug_level.data = int(config.DebugLevel)  # Populate the new field
        form.usex_api.data = int(config.UsexAPI)  # Populate the new field
        form.use_ai.data = int(config.UseAI)
        form.application_language.data = config.ApplicationLanguage

        return render_template('app_configuration.html', title='App Configuration', form=form)



@app.route('/bookings/')
@login_required
def bookings():
    bookings = Booking.query.all() # Replace this with the actual method of getting your bookings
    return render_template('bookings.html', bookings=bookings)


@app.route("/new_booking/", methods=['GET', 'POST'])
@login_required
def new_booking():
    form = BookingForm()
    if form.validate_on_submit():
        date_str = form.date.data
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time = time_(hour=int(form.start_hour.data))
        end_time = time_(hour=(start_time.hour+1)%24)
        
        existing_booking = Booking.query.filter_by(date=date, start_time=start_time, end_time=end_time).first()

        if existing_booking:
            flash('Η χρονοθυρίδα είναι δεσμευμένη.')
            return redirect(url_for('new_booking'))

        booking = Booking(user_email=current_user.email, date=date, start_time=start_time, end_time=end_time)

        try:
            db.session.add(booking)
            db.session.commit()
            flash('Ολοκληρώθηκε η κράτηση της χρονοθυρίδας!', 'success')
            
            return redirect(url_for('root'))  # Redirect to the root page

        except IntegrityError as e:
            db.session.rollback()
            flash('An error occurred while making the booking. Please try again.', 'danger')
            
            return redirect(url_for('new_booking'))
        

    return render_template('new_booking.html', title='New Booking', form=form, legend='New Booking')






def handle_client(client_socket):
    # Handle the client connection
    
    while True:
        data = client_socket.recv(1024)  # Receive data from the client
        if not data:
            break  # Connection closed by the client
        # Process the received data as required
        if get_DebugLevel() > 0:
            print(data.decode())  # Print the received data
        sys.stdout.flush()        
        loggeduser=WorkingSessions.query.filter_by(workingStatus='owner').first()                
        loggeduser2=WorkingSessions.query.filter_by(workingStatus='noodleowner').first()                  
        loggeduser3=WorkingSessions.query.filter_by(workingStatus='admin').first()                  
        if loggeduser or loggeduser2 or loggeduser3:
            if loggeduser:
                user = User.query.filter_by(email=loggeduser.email).first()            
            if loggeduser2:
                user = User.query.filter_by(email=loggeduser2.email).first()                                
            if loggeduser3:
                user = User.query.filter_by(email=loggeduser3.email).first()
            if get_Use_xAPI():
                mylrs.SendStatement(user.username, user.email,data.decode(),'RemoteLab1')            

        else:
            if get_Use_xAPI():
                mylrs.SendStatement('Not Set Yet', 'Not Set Yet',data.decode(),'RemoteLab1')    
        # Add your logic to handle the data
        
    # Close the client socket after the connection is closed
    client_socket.close()
    


def run_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 5001))  # Bind to the desired IP address and port
    server_socket.listen(5)  # Listen for incoming connections

    while True:
        client_socket, address = server_socket.accept()  # Accept a new client connection
        # Handle the client connection in a separate thread or process
        # You can use threading or multiprocessing libraries for concurrent handling
        handle_client(client_socket)






@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('errors/404.html'), 404


@app.errorhandler(415)
def unsupported_media_type(e):
    # note that we set the 415 status explicitly
    return render_template('errors/415.html'), 415

#def set_launchId(launchId):
#    if 'launchId' not in g:
#        g.launchId = launchId
#    return g.launchId

#@app.before_request
#def before_request():
#    set_launchId("NoLaunchId")



# To size είναι ένα tuple της μορφής (640, 480)
def image_save(image, where, size):
    random_filename = secrets.token_hex(12)
    file_name, file_extension = os.path.splitext(image.filename)
    image_filename = random_filename + file_extension

    image_path = os.path.join(app.root_path, 'static/images', where, image_filename)

    img = Image.open(image)

    img.thumbnail(size)

    img.save(image_path)

    return image_filename



@app.route("/index/")
@app.route("/")
def root():
    page = request.args.get("page", 1, type=int)
    articles = Article.query.order_by(Article.date_created.desc()).paginate(per_page=5, page=page)
    return render_template("index.html", articles=articles)

@app.route("/remote_lab1/")
@login_required
def remote_lab1():        
    return render_template("remote_lab1.html")

@app.route("/remote_lab1_external/")
@login_required
def remote_lab1_external():
    return render_template("remote_lab1_external.html")
    
@app.route("/remote_lab1_embedded2/")
@login_required
def remote_lab1_embedded2():
    return render_template("remote_lab1_embedded_with_serial.html")

@app.route("/monitor_shadow_controller/")
@login_required
def monitor_shadow_controller():
    return render_template("monitor_shadow_serial.html")

@app.route('/checkbox/<checkbox_id>/<action>')
@login_required
def handle_checkbox(checkbox_id, action):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect(("127.0.0.1", 9090))
    ActiveActivity = get_ActiveActivity()

    # Extract the number from checkbox_id
    checkbox_number = int(checkbox_id.replace('checkbox', ''))

    # Update the Actions model based on the checkbox state change
    actions = Actions.query.first()  # Assuming there's only one row in the Actions table
    if action == 'on':
        setattr(actions, f'PIN{checkbox_number}', True)
    elif action == 'off':
        setattr(actions, f'PIN{checkbox_number}', False)
    db.session.commit()

    # Perform the necessary actions on the server
    data = checkbox_id + ":0" if action == 'on' else checkbox_id + ":1"
    clientSocket.send(data.encode())
    if ActiveActivity != -1:
        if checkbox_id == "checkbox1":
            UserActivities.append("YELLOW_BUTTON_ON" if action == 'on' else "YELLOW_BUTTON_OFF")
        elif checkbox_id == "checkbox2":
            UserActivities.append("RED_BUTTON_ON" if action == 'on' else "RED_BUTTON_OFF")
        elif checkbox_id == "checkbox3":
            UserActivities.append("HEATER_ON" if action == 'on' else "HEATER_OFF")
        elif checkbox_id == "checkbox4":
            UserActivities.append("FAN_ON" if action == 'on' else "FAN_OFF")
        elif checkbox_id == "checkbox5":
            UserActivities.append("LIGHTS_ON" if action == 'on' else "LIGHTS_OFF")
    clientSocket.close()

    return "Checkbox {} turned {}".format(checkbox_id, "ON" if action == 'on' else "OFF")


@app.route('/slider/<slider_value>/')
@login_required
def handle_slider(slider_value):
    # Perform the desired action based on the slider value
    # Perform the necessary operations
    #print(slider_value)
    clientSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect(("127.0.0.1",9090))
    ActiveActivity=get_ActiveActivity()
    
    # Update the pot1 field in the Actions table
    actions = Actions.query.first()  # Assuming there's only one row in the Actions table
    actions.pot1 = int(slider_value)
    db.session.commit()

    
    data="SLIDER:"+str(slider_value)
    clientSocket.send(data.encode())                                                            
    if ActiveActivity!=-1:
        UserActivities.append("SLIDER_CHANGE")    
    clientSocket.close()                        
    if get_DebugLevel() > 0:
        print(data)    
    return "Slider value changed to {}".format(slider_value)


@app.route("/remote_lab1_monitor/")
@login_required
def remote_lab1_monitor():
    return render_template("remote_lab1_monitor.html")
        

@app.route("/remote_lab1_embedded/",methods=["GET", "POST"])
@login_required
def remote_lab1_embedded():
    
        ActionChanged=[0,0,0,0,0,0,0,0]
        action = Actions.query.get_or_404(1)
        if get_DebugLevel() > 0:
            print(str(action))
        form=ActionsForm(PIN1=action.PIN1,
                        PIN2=action.PIN2,
                        PIN3=action.PIN3,
                        PIN4=action.PIN4,
                        PIN5=action.PIN5,
                        PIN6=action.PIN6,
                        PIN7=action.PIN7,
                        PIN8=action.PIN8)
        

        
        if request.method == 'POST':            
                        
            if (action.PIN1 != form.PIN1.data):
                action.PIN1 = form.PIN1.data
                ActionChanged[0]=1            
            
            if (action.PIN2 != form.PIN2.data):
                action.PIN2 = form.PIN2.data
                ActionChanged[1]=1            
            
            if (action.PIN3 != form.PIN3.data):
                action.PIN3 = form.PIN3.data
                ActionChanged[2]=1            
            
            if (action.PIN4 != form.PIN4.data):
                action.PIN4 = form.PIN4.data
                ActionChanged[3]=1            
            
            if (action.PIN5 != form.PIN5.data):
                action.PIN5 = form.PIN5.data
                ActionChanged[4]=1            
            
            if (action.PIN6 != form.PIN6.data):
                action.PIN6 = form.PIN6.data
                ActionChanged[5]=1            
            
            if (action.PIN7 != form.PIN7.data):
                action.PIN7 = form.PIN7.data
                ActionChanged[6]=1            
            
            if (action.PIN8 != form.PIN8.data):
                action.PIN8 = form.PIN8.data
                ActionChanged[7]=1
            
            #print(ActionChanged)
            #print(str(form.PIN1.data)+','+str(form.PIN2.data)+','+str(form.PIN3.data)+','+str(form.PIN4.data)+','+str(form.PIN5.data)+','+str(form.PIN6.data)+','+str(form.PIN7.data)+','+str(form.PIN8.data))
            #print(str(action))
            
            clientSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSocket.connect(("127.0.0.1",9090))
                    
            if (form.PIN1.data) :
                                        
                data = "0:"
                clientSocket.send(data.encode())                                                            
                if ActionChanged[0]==1:
                    if ActiveActivity!=-1:
                        UserActivities.append("PIN1_ON")    
            else :
                    
                data = "1:"
                clientSocket.send(data.encode())                                        
                if ActionChanged[0]==1:
                    if ActiveActivity!=-1:
                        UserActivities.append("PIN1_OFF")        
                
            if (form.PIN2.data) :
                        
                data = "0:"
                clientSocket.send(data.encode())                                                                                                                                   
                if ActionChanged[1]==1:
                    if ActiveActivity!=-1:
                        UserActivities.append("PIN2_ON")        
            else :
                        
                data = "1:"
                clientSocket.send(data.encode())     
                if ActionChanged[1]==1:
                    if ActiveActivity!=-1:
                        UserActivities.append("PIN2_OFF")            
                
            if (form.PIN3.data) :
                        
                data = "0:"
                clientSocket.send(data.encode())
                if ActionChanged[2]==1:
                    if ActiveActivity!=-1:
                        UserActivities.append("PIN3_ON")                                                                    
                        
            else :
                        
                data = "1:"
                clientSocket.send(data.encode())
                if ActionChanged[2]==1:
                    if ActiveActivity!=-1:
                        UserActivities.append("PIN3_OFF")            
                
            if (form.PIN4.data) :
                        
                data = "0:"
                clientSocket.send(data.encode())                                                            
                if ActionChanged[3]==1:
                    if ActiveActivity!=-1:
                        UserActivities.append("PIN4_ON")            
            else :
                        
                data = "1:"
                clientSocket.send(data.encode())     
                if ActionChanged[3]==1:
                    if ActiveActivity!=-1:
                        UserActivities.append("PIN4_OFF")            
                
            if (form.PIN5.data) :
                        
                data = "0:"
                clientSocket.send(data.encode())
                if ActionChanged[4]==1:
                    if ActiveActivity!=-1:
                        UserActivities.append("PIN5_ON")            
            else :
                        
                data = "1:"
                clientSocket.send(data.encode())     
                if ActionChanged[4]==1:
                    if ActiveActivity!=-1:
                        UserActivities.append("PIN5_OFF")                

            if (form.PIN6.data) :
                data = "0:"                    
                clientSocket.send(data.encode())                                                            
                if ActionChanged[5]==1:
                    if ActiveActivity!=-1:
                        UserActivities.append("PIN6_ON")            
            else :
                        
                data = "1:"
                clientSocket.send(data.encode())     
                if ActionChanged[5]==1:
                    if ActiveActivity!=-1:
                        UserActivities.append("PIN6_OFF")                
                
            if (form.PIN7.data) :
                        
                data = "0:"
                clientSocket.send(data.encode())                                                            
                if ActionChanged[6]==1:
                    if ActiveActivity!=-1:
                        UserActivities.append("PIN7_ON")            
            else :
                        
                data = "1:"
                clientSocket.send(data.encode())     
                if ActionChanged[6]==1:
                    if ActiveActivity!=-1:
                        UserActivities.append("PIN7_OFF")                
                
            if (form.PIN8.data) :
                        
                data = "0"
                #command="sudo echo out >/sys/class/gpio/gpio23/direction"
                #out = subprocess.run(command,shell=True,stdout=subprocess.PIPE)
                #command="sudo echo 0 > /sys/class/gpio23/value"
                #out = subprocess.run(command,shell=True,stdout=subprocess.PIPE)
                clientSocket.send(data.encode())                                                            
                if ActionChanged[7]==1:
                    if ActiveActivity!=-1:
                        UserActivities.append("PIN8_ON")            
            else :
                        
                data = "1"
                #command="sudo echo out >/sys/class/gpio/gpio23/direction"
                #out = subprocess.run(command,shell=True,stdout=subprocess.PIPE)
                #command="sudo echo 1 > /sys/class/gpio23/value"
                #out = subprocess.run(command,shell=True,stdout=subprocess.PIPE)
                clientSocket.send(data.encode())     
                if ActionChanged[7]==1:
                    if ActiveActivity!=-1:
                        UserActivities.append("PIN8_OFF")                

            clientSocket.close()                        
            db.session.commit()        
        return render_template("remote_lab1_embedded.html", form=form,action=action)
        
@app.context_processor
def utility_processor():
    def JinStr(TheObj):
        if TheObj:
            return str(TheObj)
        else:
            return "LoggedOut"
    return dict(JinStr=JinStr)

   

@app.route("/articles_by_author/<int:author_id>")
def articles_by_author(author_id):
    user = User.query.get_or_404(author_id)

    page = request.args.get("page", 1, type=int)
    articles = Article.query.filter_by(author=user).order_by(Article.date_created.desc()).paginate(per_page=5, page=page)

    return render_template("articles_by_author.html", articles=articles, author=user)

@app.route("/activities_by_author/<int:author_id>")
def activities_by_author(author_id):

    user = User.query.get_or_404(author_id)

    page = request.args.get("page", 1, type=int)
    activities = Activities.query.filter_by(author=user).order_by(Activities.date_created.desc()).paginate(per_page=5, page=page)

    return render_template("activities_by_author.html", activities=activities, author=user)

@app.route("/activities_active/")
def activities_active():
   
    page = request.args.get("page", 1, type=int)
    activities = Activities.query.order_by(Activities.date_created.desc()).paginate(per_page=5, page=page)

    return render_template("activities_active.html", activities=activities)

@app.route("/ShowWorkingSessions/")
def ShowWorkingSessions():
   
    page = request.args.get("page", 1, type=int)
    workingSessions = WorkingSessions.query.order_by(WorkingSessions.date_created.desc()).paginate(per_page=5, page=page)

    return render_template("ShowWorkingSessions.html", workingSessions=workingSessions)


@app.route("/signup/", methods=["GET", "POST"])
def signup():

    form = SignupForm()

    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        password2 = form.password2.data

        encrypted_password = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(username=username, email=email, password=encrypted_password)
        db.session.add(user)
        db.session.commit()

        flash(f"Ο λογαριασμός για τον χρήστη <b>{username}</b> δημιουργήθηκε με επιτυχία", "success")

        return redirect(url_for('login'))
    

    return render_template("signup.html", form=form)

def get_config_bookingsystem():
    config = AppConfiguration.query.get(0)
    if config:
        BookingSystem = config.BookingSystem
        
    return BookingSystem

def get_user_data():
    if current_user.is_authenticated:
        try:
            loggeduser = WorkingSessions.query.filter_by(email=current_user.email).first()
            userData_list = [loggeduser.email, loggeduser.workingStatus, loggeduser.date_created]
        except AttributeError:
            userData_list = ['-', '-', '-']
    else:
        userData_list = ['-', '-', '-']
    return userData_list    


    
def get_activity_data(activity_id):    
    activity = Activities.query.filter_by(id = activity_id).first()
    if activity:    
        activity_data_list=[activity_id,activity.activity_title,activity.activity_body]
    else:    
        activity_data_list=['-1','-','-']
    return activity_data_list    

def get_ActiveActivity():
    config = AppConfiguration.query.get(0)
    if config:
        active_activity = config.ActiveActivity
    else:
        # Handle the case when the record with id=0 does not exist
        active_activity = None
    return active_activity

def set_ActiveActivity(value):
    config = AppConfiguration.query.get(0)
    if config:
        config.ActiveActivity = value
        db.session.commit()
        return True
    else:
        return False

def get_TimerMinutes():
    config = AppConfiguration.query.get(0)
    if config:
        TimerMinutes = config.TimerMinutes
    else:
        # Handle the case when the record with id=0 does not exist
        TimerMinutes = 60
    return TimerMinutes

def CheckIf_UserBooked(email):    
    #date = datetime.strptime(str(datetime), '%Y-%m-%d').date()
    curr_date=date.today()    
    current_time = datetime.now().time()    
    current_hour = current_time.strftime('%H')
    # Add zeroes to the format
    formatted_hour = current_hour + ':00:00.000000'
    existing_booking = Booking.query.filter_by(date=curr_date, user_email=email,start_time=formatted_hour).first()
        
    if existing_booking:
        UserBooked='True'
    else:
        UserBooked='False'
    return UserBooked

def get_BookingTimeslot():
    curr_date=date.today()
    current_time = datetime.now().time()    
    current_hour = current_time.strftime('%H')
    # Add zeroes to the format
    formatted_hour = current_hour + ':00:00.000000'
    existing_booking = Booking.query.filter_by(date=curr_date, start_time=formatted_hour).first()            
    if existing_booking:
        if get_DebugLevel() > 0:
            print(existing_booking)
        booked_timeslot='True'                    
    else:
        if get_DebugLevel() > 0:
            print("booked_timeslot is false")
            print(curr_date)
            print(current_time)
            print(current_hour)
        booked_timeslot='False'                    
    return booked_timeslot


@app.context_processor        
def panel_data():
    ActiveActivity=get_ActiveActivity()    
    activityData=get_activity_data(ActiveActivity)
    userData=get_user_data()
    BookingSystem=get_config_bookingsystem()
    TimerMinutes=get_TimerMinutes()
    data = {
        'ActiveActivityID': activityData[0], #activityData.ActiveActivityID,
        'ActiveActivityTitle': activityData[1], #activityData.ActiveActivityTitle,
        'ActiveActivityBody': activityData[2], #activityData.ActiveActivityBody,
        'user_name': userData[0], #userData.user_name,
        'user_role': userData[1], #userData.user_role,
        'user_loggedTime':userData[2], #userData.user_loggedTime
        'BookingSystem':BookingSystem,
        'TimerMinutes':TimerMinutes

    }
    #print(data)
    return dict(panel_data=data)

@app.context_processor
def currentTS_booking_data():    
    curr_date=date.today()
    current_time = datetime.now().time()    
    current_hour = current_time.strftime('%H')
    # Add zeroes to the format
    formatted_hour = current_hour + ':00:00.000000'
    existing_booking = Booking.query.filter_by(date=curr_date, start_time=formatted_hour).first()            
    if existing_booking:
        data= {
            'BookedEmail': existing_booking.user_email,
            'start_time':existing_booking.start_time,
            'end_time':existing_booking.end_time
        }
    else:
        data= {
            'BookedEmail': 'N/A',
            'start_time': 'N/A',
            'end_time': 'N/A'
        }                                  
    return dict(currentTS_booking_data=data)

@app.route("/login_lab/", methods=["GET", "POST"])
def login_lab():
    global launchId
    update_launch_id('NoLaunchId')
    launchId=get_launch_id()
    if current_user.is_authenticated:
        return redirect(url_for("root"))        
    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        global ActiveActivity
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        workingSession = WorkingSessions.query.filter_by(workingStatus='owner').first()
        workingSession2 = WorkingSessions.query.filter_by(workingStatus='moodleowner').first()
        userLogged=WorkingSessions.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            if user.usergroup=="admin":
                AdminLogged = WorkingSessions.query.filter_by(email=user.email).first()
                if not AdminLogged:
                        InsertWorkingSession(email, 'admin')
                        flash(f"Συνδεθήκατε ως Διαχειριστής.", "success")
                else:        
                        flash(f"Διαπιστώθηκε προηγούμενη σύνδεση, χωρίς σωστή έξοδο. Σύνδεση ξανά.", "success")
                if get_Use_xAPI():
                    mylrs.SendStatement(user.username, user.email,'Login','RemoteLab1')
                login_user(user)
                return redirect(url_for("root"))
            else:
                BookingSystem=get_config_bookingsystem()
                if BookingSystem:
                    flash(f"Βρέθηκε ενεργοποιημένο το Booking System.", "success")                                         
                    if get_BookingTimeslot()=='True':
                        flash(f"Timeslot is not free.", "success")
                        UserBooked=CheckIf_UserBooked(email)
                        if UserBooked=='True':                                   
                            if not workingSession and not userLogged and not workingSession2:    
                                if InsertWorkingSession(email, 'owner'):                
                                    login_user(user, remember=form.remember_me.data)                                                                                
                                if set_ActiveActivity(-1) == False:
                                    flash(f"Δεν έγινε η αρχικοποίηση ActiveActivity", "success")     
                                if get_Use_xAPI():
                                    mylrs.SendStatement(user.username, user.email,'Login','RemoteLab1')
                                next_link = request.args.get("next")
                                flash(f"Η είσοδος του χρήστη με email: {email} στη σελίδα μας έγινε με επιτυχία.", "success")
                                flash(f"Έχει κάνει κράτηση τη παρουσα χρονοθυρίδα.<br>Συνδεθήκατε ως Κύριος Χρήστης Εργαστηρίου.", "success")                                                                 

                            else:
                                if userLogged:                    
                                    flash(f"Διαπιστώθηκε προηγούμενη σύνδεση, χωρίς σωστή έξοδο. Σύνδεση ξανά.", "success")                                                                                                     
                        else:    
                            flash(f"H χρονοθυρίδα είναι δεσμευμένη από άλλο χρηστη.<br>Συνδέεστε ως θεατής.<br>Κάποιες λειτουργίες στο εργαστήριο είναι απενεργοποιημένες.", "success")         
                            InsertWorkingSession(email, 'spectator')
                        login_user(user)
                        return redirect(url_for("root"))                                            
                    else:
                        #Δεσμευση timeslot επειδη είναι ελέυθερο και κάνει συνδεση του χρηστη
                        flash(f"Η χρονοθυρίδα της ώρας αυτής είναι διαθέσιμη.<br> Μπορείτε να κάνετε κράτηση και να συνδεθείτε ξανά ώς κύριος χρήστης.", "success")                        
                        flash(f"Συνδέεστε ως θεατής.<br>Κάποιες λειτουργίες στο εργαστήριο είναι απενεργοποιημένες.", "success")         
                        InsertWorkingSession(email, 'spectator')
                        login_user(user)
                        return redirect(url_for("root"))                                            
                else:
                    if not workingSession and not userLogged and not workingSession2:    
                        if InsertWorkingSession(email, 'owner'):                
                            login_user(user, remember=form.remember_me.data)                                                                                
                        if set_ActiveActivity(-1) == False:
                            flash(f"Δεν έγινε η αρχικοποίηση ActiveActivity", "success")     
                        if get_Use_xAPI():
                            mylrs.SendStatement(user.username, user.email,'Login','RemoteLab1')
                        next_link = request.args.get("next")
                        flash(f"Η είσοδος του χρήστη με email: {email} στη σελίδα μας έγινε με επιτυχία.", "success")
                        flash(f"Δεν υπάρχει χρήστης που χρησιμοποιεί το εργαστήριο.<br>Συνδεθήκατε ως Κύριος Χρήστης Εργαστηρίου.", "success")                                 
                        return redirect(url_for("root"))    
                    else:
                        if userLogged:                    
                            flash(f"Διαπιστώθηκε προηγούμενη σύνδεση, χωρίς σωστή έξοδο. Σύνδεση ξανά.", "success")                                         
                        else:    
                            flash(f"Yπάρχει ήδη χρήστης που χρησιμοποιεί το εργαστήριο.<br>Συνδέεστε ως θεατής.<br>Κάποιες λειτουργίες στο εργαστήριο είναι απενεργοποιημένες.", "success")         
                            InsertWorkingSession(email, 'spectator')                                
                        login_user(user)
                        return redirect(url_for("root"))     
        else:
            flash("Η είσοδος του χρήστη ήταν ανεπιτυχής, παρακαλούμε δοκιμάστε ξανά με τα σωστά email/password.", "warning")                
            return redirect(url_for("root"))    
    else:
        return render_template("login.html", form=form)
    

@app.route("/logout/")
def logout():
    user = User.query.filter_by(username=current_user.username).first()    
    workingUser=WorkingSessions.query.filter_by(email=current_user.email).first()
    #if (workingUser.workingStatus=='owner' or workingUser.workingStatus=='moodleowner'):
    #    scheduler.remove_job('update_timer', True)
        
    if workingUser:
        db.session.delete(workingUser)
        db.session.commit()
    logout_user()
    flash("Έγινε αποσύνδεση του χρήστη.", "success")    
    if get_Use_xAPI():
        mylrs.SendStatement(user.username, user.email,'Logout','RemoteLab1')
    if set_ActiveActivity(-1) != True:
        if get_DebugLevel() > 0:
            print("Δεν αποθηκεύτηκε η ActiveActivity")
        flash("Δεν αποθηκεύτηκε η ActiveActivity", "error")
    return redirect(url_for("root"))

@app.route("/activate_activity/<int:activity_id>")
@login_required
def activate_activity(activity_id):
    global ActiveActivity 
    config=AppConfiguration.query.filter_by(id = 0).first()
    user = User.query.filter_by(username=current_user.username).first()
    activity = Activities.query.filter_by(id = activity_id).first()
    ActiveActivity=activity_id
    if set_ActiveActivity(activity_id) != True:
        flash("Δεν αποθηκεύτηκε η ActiveActivity", "error")    

    ActiveActivityTitle=activity.activity_title
    Activity_MicroActs = activity.activity_microacts.split('|')
    UserActivities=[]   
    
    if config.ShadowController==True:
        if get_DebugLevel() > 1:
            flash('Shadow Controller is True')
        response=LoadMonitorSketch(str('monitor_' + str(ActiveActivity)),activity.activity_ctrl_sketch)
    flash("Ενεργοποιήθηκε η δραστηριότητα με τίτλο "+ str(activity.activity_title)+".", "success")    
    if get_DebugLevel() > 1:
        flash("Σειρα επιτυχίας " + str(Activity_MicroActs) + " Σειρα μικροδραστηριοτήτων " + str(UserActivities), "success")    
    
    flash("Τίτλος:" + str(activity.activity_title) + "-" + str(activity.activity_body),"middle_footer")
    if get_Use_xAPI():
        mylrs.SendStatement(user.username, user.email,'Attempted ' + str(activity.activity_title),'RemoteLab1')
    return redirect(url_for("root"))

@app.route("/reset_activity/")
@login_required
def reset_activity():
    global ActiveActivity 
    global UserActivities

    user = User.query.filter_by(username=current_user.username).first()
    activity = Activities.query.filter_by(id = ActiveActivity).first()
    UserActivities=[]
    
    flash("Οι μικροδραστηριότητες του χρήστη αρχικοποιήθηκαν.", "success")        
    mylrs.SendStatement(user.username, user.email,'Reset Activity ' + str(activity.activity_title),'RemoteLab1')
    return redirect(url_for("root"))


@app.route("/submit_activity/<int:activity_id>")
@login_required
def submit_activity(activity_id):
    global ActiveActivity
    global UserActivities
    global launchId
    launchId=get_launch_id()
    if get_DebugLevel() > 0:
        print('********* '+ launchId +' ********')

    user = User.query.filter_by(username=current_user.username).first()
    activity = Activities.query.filter_by(id = activity_id).first()    
    Activity_MicroActs=activity.activity_microacts.split('|')
    flash("Υποβλήθηκε η δραστηριότητα με τίτλο " + str(activity.activity_title) + ".", "success")    
    if get_Use_xAPI():
        mylrs.SendStatement(user.username, user.email,'Submited Activity '+ str(activity.activity_title),'RemoteLab1')
    Result=CheckResults(Activity_MicroActs, UserActivities)
    if get_DebugLevel() > 0:
        print("***********" + Result + "*********")    
    CodeResults=check_code()
    if CodeResults==-1:
        flash('Δεν έχει ενεργοποιηθεί δραστηριότητα για έλεγχο κώδικα.','warning')
    elif 'NoUpload' in CodeResults:
        flash('Ο χρήστης δεν έχει φορτώσει κώδικα στο μικροελεγκτή.','warning')
    elif 'NoModelData' in CodeResults:
        flash('Δεν έχουν φορτωθεί δεδομένα μηχανικής μάθησης.','warning')            
    elif 'Correct' in CodeResults:
        flash('Ο χρήστης έχει φορτώσει κώδικα στο μικροελεγκτή και βρέθηκε σωστός.','warning')    
    elif 'Incorrect' in CodeResults:
        flash('Ο χρήστης έχει φορτώσει κώδικα στο μικροελεγκτή και ΔΕΝ βρέθηκε σωστός.','warning')    
    else:
        if get_DebugLevel() > 0:
            print(CodeResults)
        flash('Άγνωστη απάντηση από τον έλεγχο του κωδικα με μηχανική μάθηση.','warning')    
    if Result=="Passed":
        flash("Η δραστηριότητα με τίτλο " + str(activity.activity_title) + " ολοκληρωθηκε με ΕΠΙΤΥΧΙΑ.", "success")    
        flash("Σειρα επιτυχίας " + str(Activity_MicroActs) + " Σειρά μικροδραστηριοτήτων" + str(UserActivities), "success")    
        if get_Use_xAPI():
            mylrs.SendStatement(user.username, user.email,' Passed '+ str(activity.activity_title),' RemoteLab1')
        if get_DebugLevel() > 0:
            print("********** LaunchId = " + launchId +"*********")
        if (launchId!="NoLaunchId"):
            if get_DebugLevel() > 0:
                print("************Update Grades Passed**********")
            remotelab_score(launchId, '1', '10')
    elif Result =="Failed":
        flash("Η δραστηριότητα με τίτλο " + str(activity.activity_title) + " ΔΕΝ ολοκληρωθηκε ΕΠΙΤΥΧΩΣ.", "success")    
        if get_DebugLevel() > 1:
            flash("Σειρα επιτυχίας " + str(Activity_MicroActs) + " Σειρά μικροδραστηριοτήτων" + str(UserActivities), "success")    
        if get_Use_xAPI():
            mylrs.SendStatement(user.username, user.email,' Failed '+ str(activity.activity_title),' RemoteLab1')
        if get_DebugLevel() > 0:
            print("**********LaunchId=" + launchId +"*********")
        if (launchId!="NoLaunchId"):
            if get_DebugLevel() > 0:
                print("**********Update Grades Failed***********")
            remotelab_score(launchId, '1', '0')
    ActiveActivity=-1
    if set_ActiveActivity(-1)==False:
        flash("Δεν αρχικοποιήθηκε η ActiveActivity", "error")    
    UserActivities=[]

    userData=get_user_data()
    if userData[1]=='moodleowner':
        if get_DebugLevel() > 0:
            print("moodleowner loging out")
        return redirect(url_for("logout"))    
    
    return redirect(url_for("root"))

@app.route("/activity_status/")
def activity_status():
    global ActiveActivity
    config=AppConfiguration.query.filter_by(id = 0).first()
    if ActiveActivity==-1:
        flash("Δεν έχει ενεργoποιηθεί δραστηριότητα.", "success")
        return redirect(url_for("root"))
        #return render_template("activity_status.html", activity=-1,UserActivities="Δεν έχουν καταγραφεί κινήσεις χρήστη")        
    else:            
        activity = Activities.query.filter_by(id = str(ActiveActivity)).first()
        flash("Ενεργή δραστηριότητα: " + activity.activity_title, "success")    
        
        UserMicroActivitiesDescs=GetMicroActivitiesDescs()
        ActivityMicroActivitiesDescs=GetActivityMActivitiesDescs(activity)
        if config.ShadowController==True:
            #flash('Shadow Controller is True')
            ControlerResult=GetControlerResult_SerialComm()
        else:    
            ControlerResult= "NO SHADOW microcontroller"  
        
        return render_template("activity_status.html", activity=activity,UserActivities=UserMicroActivitiesDescs,ActivityMicroActivitiesDescs=ActivityMicroActivitiesDescs,ControlerResult=ControlerResult)

def CheckResults(List1,List2):
    if List1 == List2:
        return "Passed"
    else:
        if List1[0]=='NONE':
            return "Passed"
        else:    
            return "Failed"    

@app.route('/getShadowReport3/')
@login_required
def GetControlerResult_SerialComm():
    print('Checking Controller')
    if get_DebugLevel() > 0:  
        print('Checking Controller')
    # Set up the serial connection
    ttyACM=get_SHADOW_tty()        
    if ttyACM=="None":
        flash("No Shadow Board found.", "warning")
        return redirect(url_for('root'))        
    elif ttyACM=="ttyACM0":
        ser = serial.Serial('/dev/ttyACM0', 9600)
    elif ttyACM=="ttyACM1":
        ser = serial.Serial('/dev/ttyACM1', 9600)    
    time.sleep(2)  # Give the Arduino some time to initialize

    # Send the "report" string to the Arduino
    print('Request Report Shadow Controller')
    ser.write(b'report')
    ser.flush()

    # Wait for the Arduino to respond
    time.sleep(1)

    # Read the response from the Arduino
    response = ser.readline().decode('utf-8').rstrip()

    # Print the received response
    if get_DebugLevel() > 0:
        print("Response from Arduino:", response)

    # Close the serial connection
    ser.close()  
    return response

@app.route('/Collect_Controller_data/')
@login_required
def Collect_Controller_data():
    result = "None"    
    # Open serial connection with Arduino
    print('Collecting from Shadow Controller')
    if get_DebugLevel() > 0:  
        print('Collecting from Shadow Controller')
    
    # Set up the serial connection
    ttyACM = get_SHADOW_tty()        
    if ttyACM == "None":
        flash("No Shadow Board found.", "warning")
        return redirect(url_for('root'))        
    elif ttyACM == "ttyACM0":
        ser = serial.Serial('/dev/ttyACM0', 9600)
    elif ttyACM == "ttyACM1":
        ser = serial.Serial('/dev/ttyACM1', 9600)    
    
    time.sleep(2)  # Give the Arduino some time to initialize
    
    # Send the command to the Arduino
    ser.write(b"report\n")
    
    # Read the reply from the Arduino
    line = ser.readline().decode().strip()
    
    # Process the reply
    print(f"Received reply from Arduino: {line}")
    # Add your processing logic here
    result = line
    
    # Close serial connection
    ser.close()    
    return result

def GetControlerResult_I2C():
    if get_DebugLevel() > 0:  
        print('Checking Controller')        
    
    bus = smbus.SMBus(1)
    arduino_address = 0x08
	# Request report from Arduino
    bus.write_byte(arduino_address, ord('r'))  # Sending 'r' to request report
    time.sleep(0.1)  # Wait for response
        
    # Read the report from Arduino
    report = bus.read_i2c_block_data(arduino_address, 0, 32)  # Assuming max report length is 32 bytes
        
    # Convert bytes to string
    report_str = "".join([chr(byte) for byte in report]).strip()
    if get_DebugLevel() > 0:
        print("Response from Arduino:", report_str)
    
    return report_str



def GetMicroActivitiesDescs():
    global UserActivities
    UserMicroActivitiesDescs=[]
    ActivityMicroActivitiesDescs=[]
    for m in  UserActivities:        
        UsermicroActivities=MicroActivity.query.filter_by(name = str(m)).first()
        UserMicroActivitiesDescs.append(UsermicroActivities.instructions)        
    return UserMicroActivitiesDescs

def GetActivityMActivitiesDescs(activity):
    ActivityMicroActivitiesDescs=activity.activity_microacts.split('|')
    Descs=[]
    for m in  ActivityMicroActivitiesDescs:
        if get_DebugLevel() > 0:
            print(str(m))     
        mActivity=MicroActivity.query.filter_by(name = str(m)).first()
        Descs.append(mActivity.instructions)
    if get_DebugLevel() > 0:    
        print(Descs)    
    return Descs

    
    



@app.route("/new_sketch/", methods=["GET", "POST"])
@login_required
def new_article():
    form = NewArticleForm()

    if request.method == 'POST' and form.validate_on_submit():
        article_title = form.article_title.data
        article_body = form.article_body.data


        if form.article_image.data:
            try:
                image_file = image_save(form.article_image.data, 'articles_images', (640, 360))
            except:
                abort(415)

            article = Article(article_title=article_title,
                              article_body=article_body,
                              author=current_user,
                              article_image=image_file)
        else:
            article = Article(article_title=article_title, article_body=article_body, author=current_user)
        if get_Use_xAPI():
            mylrs.SendStatement(current_user.username, current_user.email,'CreateSketch',article_title)
        db.session.add(article)
        db.session.commit()

        flash(f"Το Σχέδιο με τίτλο {article.article_title} δημιουργήθηκε με επιτυχία", "success")

        return redirect(url_for("root"))

    return render_template("new_article.html", form=form, page_title="Εισαγωγή Νέου Σχεδίου")

@app.route("/new_activity/", methods=["GET", "POST"])
@login_required
def new_activity():
    form = NewActivityForm()
    microActivities=MicroActivity.query.all()

    if request.method == 'POST' and form.validate_on_submit():
        activity_title = form.activity_title.data
        activity_body = form.activity_body.data
        activity_ctrl_sketch = form.activity_ctrl_sketch.data
        activity_microacts=form.activity_microacts.data
        activity_ml_model=form.activity_ml_model.data
        activity_type = form.activity_type.data

        if form.activity_image.data:
            try:
                image_file = image_save(form.activity_image.data, 'activities_images', (640, 360))
            except:
                abort(415)

            activity = Activities(activity_title=activity_title,
                              activity_body=activity_body,
                              author=current_user,
                              activity_image=image_file,
                              activity_microacts=activity_microacts,
                              activity_ctrl_sketch=activity_ctrl_sketch,
                              activity_ml_model=activity_ml_model,
                              activity_type=activity_type )
        else:
            activity = Activities(activity_title=activity_title,
                                 activity_body=activity_body, 
                                 author=current_user,
                                 activity_microacts=activity_microacts,
                                 activity_ctrl_sketch=activity_ctrl_sketch,
                                 activity_ml_model=activity_ml_model,
                                 activity_type=activity_type )
        print(activity)
        if get_Use_xAPI():
            mylrs.SendStatement(current_user.username, current_user.email,'CreatedActivity',activity_title)
        db.session.add(activity)
        db.session.commit()

        flash(f"Η δραστηριότητα με τίτλο {activity.activity_title} δημιουργήθηκε με επιτυχία", "success")

        return redirect(url_for("root"))

    return render_template("new_activity.html", form=form, page_title="Εισαγωγή Νέας Δραστηριότητας",microActivities=microActivities)

@app.route("/full_article/<int:article_id>", methods=["GET"])
def full_article(article_id):

    article = Article.query.get_or_404(article_id)

    return render_template("full_article.html", article=article)

@app.route("/full_activity/<int:activity_id>", methods=["GET"])
def full_activity(activity_id):
    activity = Activities.query.get_or_404(activity_id)
    return render_template("full_activity.html", activity=activity)


@app.route("/delete_article/<int:article_id>", methods=["GET", "POST"])
@login_required
def delete_article(article_id):

    article = Article.query.filter_by(id=article_id, author=current_user).first_or_404()

    if article:

        db.session.delete(article)
        db.session.commit()

        flash("Το άρθρο διεγράφη με επιτυχία.", "success")

        return redirect(url_for("root"))

    flash("Το άρθρο δε βρέθηκε.", "warning")

    return redirect(url_for("root"))

@app.route("/delete_activity/<int:activity_id>", methods=["GET", "POST"])
@login_required
def delete_activity(activity_id):

    activity = Activities.query.filter_by(id=activity_id, author=current_user).first_or_404()

    if activity:

        db.session.delete(activity)
        db.session.commit()

        flash("Η δραστηριότητα διεγράφη με επιτυχία.", "success")

        return redirect(url_for("root"))

    flash("Η δραστηριότητα δε βρέθηκε.", "warning")

    return redirect(url_for("root"))

@app.route("/clear_workingSessions/", methods=["GET", "POST"])
@login_required
def clear_workingSessions():

    workingSessions = WorkingSessions.query.all()

    if workingSessions:
        for WS in workingSessions:
            db.session.delete(WS)
        db.session.commit()

        flash("Οι συνεδρίες διεγράφησαν με επιτυχία.", "success")

        return redirect(url_for("ShowWorkingSessions"))

    flash("Δεν βρέθηκαν συνεδρίες προς διαγραφή.", "warning")

    return redirect(url_for("ShowWorkingSessions"))

@app.route("/compile_sketch/<int:article_id>", methods=["GET", "POST"])
@login_required
def compile_sketch(article_id):

    article = Article.query.filter_by(id=article_id, author=current_user).first_or_404()

    if article:
        if not path.exists("FlaskBlogApp/sketches/" + article.article_title):
            os.mkdir("FlaskBlogApp/sketches/" + article.article_title)
        sketchDir="FlaskBlogApp/sketches/" +  article.article_title +"/" + article.article_title + ".ino"
        fo= open( sketchDir , "w")
        filebuffer = article.article_body
        fo.writelines(filebuffer)
        fo.close()
        flash("Το σχέδιο δημιουργήθηκε στον εξυπηρετητή.", "success")
        ArdCLIcommand="arduino-cli compile -b arduino:avr:uno " + sketchDir
        out = subprocess.run( ArdCLIcommand,shell=True,stdout=subprocess.PIPE) 
        flash(out.stdout, "success")
        UserActivities.append("CompileSketch")
        return render_template("full_article.html", article=article)

    flash("Το σχέδιο δε βρέθηκε.", "warning")

    return redirect(url_for("root"))

@app.route("/upload_sketch/<int:article_id>", methods=["GET", "POST"])
@login_required
def upload_sketch(article_id):

    article = Article.query.filter_by(id=article_id, author=current_user).first_or_404()
    existing_row = UserLastSketchUploaded.query.first()

    if existing_row:
        # Update the existing row
        existing_row.user_email = current_user.email
        existing_row.last_sketch = article.article_body
        existing_row.date_uploaded = datetime.utcnow()
    else:
        # Create a new row
        new_row = UserLastSketchUploaded(user_email=current_user.email, last_sketch=article.article_body)
        db.session.add(new_row)

    db.session.commit()


    if article:
        if not path.exists("FlaskBlogApp/sketches/" + article.article_title):
            os.mkdir("FlaskBlogApp/sketches/" + article.article_title)
        sketchDir="FlaskBlogApp/sketches/" +  article.article_title +"/" + article.article_title + ".ino"
        fo= open( sketchDir , "w")
        filebuffer = article.article_body
        fo.writelines(filebuffer)
        fo.close()
        flash("Το σχέδιο δημιουργήθηκε στον εξυπηρετητή.", "success")
        
        ttyACM=get_EXPERIMENT_tty()        
        if ttyACM=="None":
            flash("No Experiment Board found.", "warning")
            return redirect(url_for('root'))        
        elif ttyACM=="ttyACM0":
            ArdCLIcommand="arduino-cli upload -b arduino:avr:uno -p /dev/ttyACM0 " + sketchDir
        elif ttyACM=="ttyACM1":
            ArdCLIcommand="arduino-cli upload -b arduino:avr:uno -p /dev/ttyACM1 " + sketchDir
        out = subprocess.run( ArdCLIcommand,shell=True,stdout=subprocess.PIPE) 
        flash(out.stdout, "success")
        UserActivities.append("UploadSketch")
        return render_template("full_article.html", article=article)

    flash("Το σχέδιο δε βρέθηκε.", "warning")
    return redirect(url_for("root"))


#@app.route("/InitiateMaintenance/", methods=["GET", "POST"])
#@login_required
def InitiateMaintenance():

    
    
    
    sketchDir="/home/pi/lti-remote-lab/src/FlaskBlogApp/sketches/reset/Test_3_LEDs/Test_3_LEDs.ino"
    ArdCLIcommand="/home/pi/bin/arduino-cli compile -b arduino:avr:uno " + sketchDir
    out = subprocess.run( ArdCLIcommand,shell=True,stdout=subprocess.PIPE)
    # Run the command and capture the output
    process = subprocess.Popen(ArdCLIcommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for the process to complete and capture the output
    stdout, stderr = process.communicate()

    # Check the return code to see if the process was successful
    return_code = process.returncode
    if get_DebugLevel() > 0:
        print(return_code)
    # Print the output
    if get_DebugLevel() > 0:
        print("STDOUT:", stdout.decode())
        print("STDERR:", stderr.decode())
        print("Return Code:", return_code)
    if get_DebugLevel() > 0:
        print("Το σχέδιο Αρχικοποίησης μεταλωτίστηκε στον εξυπηρετητή.")
        #flash("Το σχέδιο δημιουργήθηκε στον εξυπηρετητή.", "success")

    ttyACM=get_EXPERIMENT_tty()        
    if ttyACM=="None":
        flash("No Experiment Board found.", "warning")
        return redirect(url_for('root'))        
    elif ttyACM=="ttyACM0":
        ArdCLIcommand="/home/pi/bin/arduino-cli upload -b arduino:avr:uno -p /dev/ttyACM0 " + sketchDir
    elif ttyACM=="ttyACM1":
        ArdCLIcommand="/home/pi/bin/arduino-cli upload -b arduino:avr:uno -p /dev/ttyACM1 " + sketchDir    
    out = subprocess.run( ArdCLIcommand,shell=True,stdout=subprocess.PIPE) 
    if get_DebugLevel() > 0:
        print(out.stdout)
        #flash(out.stdout, "success")        
    return "Reset Firmware"



def LoadMonitorSketch(MonitorSketchName,MonitorSketch):
    if not path.exists("FlaskBlogApp/monitorSketches/" + MonitorSketchName):
            os.mkdir("FlaskBlogApp/monitorSketches/" + MonitorSketchName)
    sketchDir="FlaskBlogApp/monitorSketches/" +  MonitorSketchName +"/" + MonitorSketchName + ".ino"
    fo= open( sketchDir , "w")
    filebuffer = MonitorSketch
    fo.writelines(filebuffer)
    fo.close()
    flash("Το σχέδιο ελεγκτή παρακολούθησης δημιουργήθηκε στον εξυπηρετητή.", "success")    
    ttyACM=get_SHADOW_tty()        
    if ttyACM=="None":
        flash("No Shadow Board found.", "warning")
        return redirect(url_for('root'))        
    elif ttyACM=="ttyACM0":
        ArdCLIcommand="arduino-cli compile -b arduino:avr:uno -p /dev/ttyACM0 " + sketchDir
    elif ttyACM=="ttyACM1":
        ArdCLIcommand="arduino-cli compile -b arduino:avr:uno -p /dev/ttyACM1 " + sketchDir    
    out = subprocess.run( ArdCLIcommand,shell=True,stdout=subprocess.PIPE) 
    flash(out.stdout, "success")
    #UserActivities.append("UploadSketch")
    if ttyACM=="None":
        flash("No Experiment Board found.", "warning")
        return redirect(url_for('root'))        
    elif ttyACM=="ttyACM0":
        ArdCLIcommand="arduino-cli upload -b arduino:avr:uno -p /dev/ttyACM0 " + sketchDir
    elif ttyACM=="ttyACM1":
        ArdCLIcommand="arduino-cli upload -b arduino:avr:uno -p /dev/ttyACM1 " + sketchDir
    out = subprocess.run( ArdCLIcommand,shell=True,stdout=subprocess.PIPE) 
    flash(out.stdout, "success")

    return "completed"

@app.route("/account/", methods=['GET', 'POST'])
@login_required
def account():
    form = AccountUpdateForm(username=current_user.username, email=current_user.email)

    if request.method == 'POST' and form.validate_on_submit():

        current_user.username = form.username.data
        current_user.email = form.email.data

        # image_save(image, where, size)

        if form.profile_image.data:

            try:
                image_file = image_save(form.profile_image.data, 'profiles_images', (150, 150))
            except:
                abort(415)

            current_user.profile_image = image_file

        db.session.commit()

        flash(f"Ο λογαριασμός του χρήστη <b>{current_user.username}</b> ενημερώθηκε με επιτυχία", "success")

        return redirect(url_for('root'))


    return render_template("account_update.html", form=form)



@app.route("/edit_article/<int:article_id>", methods=['GET', 'POST'])
@login_required
def edit_article(article_id):

    article = Article.query.filter_by(id=article_id, author=current_user).first_or_404()

    form = NewArticleForm(article_title=article.article_title, article_body=article.article_body)

    if request.method == 'POST' and form.validate_on_submit():
        article.article_title = form.article_title.data
        article.article_body = form.article_body.data


        if form.article_image.data:
            try:
                image_file = image_save(form.article_image.data, 'articles_images', (640, 360))
            except:
                abort(415)

            article.article_image = image_file


        db.session.commit()

        flash(f"Το σχέδιο με τίτλο <b>{article.article_title}</b> ενημερώθηκε με επιτυχία.", "success")

        return render_template("full_article.html", article=article)

    return render_template("new_article.html", form=form, page_title="Επεξεργασία σχεδίου")

@app.route("/edit_activity/<int:activity_id>", methods=['GET', 'POST'])
@login_required
def edit_activity(activity_id):

    activity = Activities.query.filter_by(id=activity_id, author=current_user).first_or_404()
    form = NewActivityForm(activity_title=activity.activity_title, activity_body=activity.activity_body,activity_ctrl_sketch=activity.activity_ctrl_sketch,activity_microacts=activity.activity_microacts,activity_ml_model=activity.activity_ml_model)
    microActivities=MicroActivity.query.all()
    
    if request.method == 'POST' and form.validate_on_submit():
        activity.activity_title = form.activity_title.data
        activity.activity_body = form.activity_body.data
        activity.activity_ctrl_sketch = form.activity_ctrl_sketch.data
        activity.activity_microacts=form.activity_microacts.data
        activity.activity_ml_model=form.activity_ml_model.data

        if form.activity_image.data:
            try:
                image_file = image_save(form.activity_image.data, 'activities_images', (640, 360))
            except:
                abort(415)

            activity.activity_image = image_file

        db.session.commit()
 
        flash(f"Η δραστηριότητα με τίτλο <b>{activity.activity_title}</b> ενημερώθηκε με επιτυχία.", "success")

        return render_template("full_activity.html", activity=activity)
    return render_template("new_activity.html", form=form, page_title="Edit Activity",microActivities=microActivities)


#---------- pylti-app ----------
class ReverseProxied:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scheme = environ.get('HTTP_X_FORWARDED_PROTO')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


#app = Flask('pylti1p3-game-example', template_folder='templates', static_folder='static')
app.wsgi_app = ReverseProxied(app.wsgi_app)

config = {
    "DEBUG": True,
    "ENV": "development",
    "CACHE_TYPE": "simple",
    "CACHE_DEFAULT_TIMEOUT": 600,
    "SECRET_KEY": "replace-me",
    "SESSION_TYPE": "filesystem",
    "SESSION_FILE_DIR": mkdtemp(),
    "SESSION_COOKIE_NAME": "pylti1p3-flask-app-sessionid",
    "SESSION_COOKIE_HTTPONLY": True,
    "SESSION_COOKIE_SECURE": False,   # should be True in case of HTTPS usage (production)
    "SESSION_COOKIE_SAMESITE": None,  # should be 'None' in case of HTTPS usage (production)
    "DEBUG_TB_INTERCEPT_REDIRECTS": False    
}
app.config.from_mapping(config)
cache = Cache(app)

PAGE_TITLE = 'Game Example'


class ExtendedFlaskMessageLaunch(FlaskMessageLaunch):

    def validate_nonce(self):
        """
        Probably it is bug on "https://lti-ri.imsglobal.org":
        site passes invalid "nonce" value during deep links launch.
        Because of this in case of iss == http://imsglobal.org just skip nonce validation.

        """
        iss = self.get_iss()
        deep_link_launch = self.is_deep_link_launch()
        if iss == "http://imsglobal.org" and deep_link_launch:
            return self
        return super().validate_nonce()


def get_lti_config_path():
    return os.path.join(app.root_path, '..', 'configs', 'game.json')


def get_launch_data_storage():
    return FlaskCacheDataStorage(cache)


def get_jwk_from_public_key(key_name):
    key_path = os.path.join(app.root_path, '..', 'configs', key_name)
    f = open(key_path, 'r')
    key_content = f.read()
    jwk = Registration.get_jwk(key_content)
    f.close()
    return jwk


@app.route('/login/', methods=['GET', 'POST'])
def login():
    tool_conf = ToolConfJsonFile(get_lti_config_path())
    launch_data_storage = get_launch_data_storage()

    flask_request = FlaskRequest()
    target_link_uri = flask_request.get_param('target_link_uri')
    if not target_link_uri:
        raise Exception('Missing "target_link_uri" param')

    oidc_login = FlaskOIDCLogin(flask_request, tool_conf, launch_data_storage=launch_data_storage)
    return oidc_login\
        .enable_check_cookies()\
        .redirect(target_link_uri)

#===========Connect to Game for testing==============

@app.route('/launch_remotelab_/', methods=['POST'])
def launch():
    tool_conf = ToolConfJsonFile(get_lti_config_path())    
    flask_request = FlaskRequest()   
    launch_data_storage = get_launch_data_storage()    
    message_launch = ExtendedFlaskMessageLaunch(flask_request, tool_conf, launch_data_storage=launch_data_storage)
    message_launch_data = message_launch.get_launch_data()
    if get_DebugLevel() > 0:
        pprint.pprint(message_launch_data)

    difficulty = message_launch_data.get('https://purl.imsglobal.org/spec/lti/claim/custom', {}) \
        .get('difficulty', None)
    if not difficulty:
        difficulty = request.args.get('difficulty', 'normal')

    tpl_kwargs = {
        'page_title': PAGE_TITLE,
        'is_deep_link_launch': message_launch.is_deep_link_launch(),
        'launch_data': message_launch.get_launch_data(),
        'launch_id': message_launch.get_launch_id(),
        'curr_user_name': message_launch_data.get('name', ''),
        'curr_diff': difficulty
    }
    return render_template('game.html', **tpl_kwargs)

#======== Connect to Remote Lab ==========

@app.route('/launch_remotelab/', methods=['POST'])
def launch_remotelab():
    global ActiveActivity
    global launchId
    global MoodleActivityTitle
   
    
    
    tool_conf = ToolConfJsonFile(get_lti_config_path())    
    flask_request = FlaskRequest()   
    launch_data_storage = get_launch_data_storage()    
    message_launch = ExtendedFlaskMessageLaunch(flask_request, tool_conf, launch_data_storage=launch_data_storage)
    message_launch_data = message_launch.get_launch_data()
    if get_DebugLevel() > 0:
        pprint.pprint(message_launch_data)

    lms_username = message_launch_data.get('https://purl.imsglobal.org/spec/lti/claim/ext', {}).get('user_username',None)
    email = message_launch_data.get('email', '')
    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Ο χρήστης με email: {email} δεν έχει ξανασυνδεθεί.", "warning")
        if signup_lms(lms_username, email, lms_username):
            user = User.query.filter_by(email=email).first()            
            flash(f"Ο χρήστης με email: {email} δημιουργήθηκε με επιτυχία.", "success")            
        else:
            flash(f"Ο χρήστης με email: {email} ΔΕΝ δημιουργήθηκε στο εργαστήριο.", "warning")
            raise Exception('Ο χρήστης δεν δημιουργήθηκε.') 
    
    user = User.query.filter_by(email=email).first()
    #Ο Administrator μπορεί να συνδεθεί και από moodle όμως δεν ενεργοποιεί κάποια δραστηριότητα 
    AdminLogged = WorkingSessions.query.filter_by(email=user.email, workingStatus='admin').first()
    if not AdminLogged and user.usergroup=='admin' :
        if get_DebugLevel() > 0:
            print("not admin")
        InsertWorkingSession(email, 'admin')
        if get_Use_xAPI():
            mylrs.SendStatement(user.username, user.email,'Admin Logged from LMS','RemoteLab1')        
        flash(f"Συνδεθήκατε ως Διαχειριστής.", "success")
        login_user(user)
        return redirect(url_for("root"))
    elif AdminLogged:
        if get_DebugLevel() > 0:
            print("AdminLogged")        
        flash(f"Διαπιστώθηκε προηγούμενη σύνδεση, χωρίς σωστή έξοδο. Σύνδεση ξανά.", "success")
        if get_Use_xAPI():
            mylrs.SendStatement(user.username, user.email,'Admin Reconnected from LMS','RemoteLab1')        
        login_user(user)
        return redirect(url_for("root"))
 
    UserLogged = WorkingSessions.query.filter_by(email=user.email).first()
    if UserLogged:    
        if get_DebugLevel() > 0:
            print("AdminLogged")        
        flash(f"Διαπιστώθηκε προηγούμενη σύνδεση, χωρίς σωστή έξοδο. Σύνδεση ξανά.", "success")
        login_user(user)
        return redirect(url_for("root"))
    
    ActiveActivity = message_launch_data.get('https://purl.imsglobal.org/spec/lti/claim/custom', {}) \
        .get('activity', None)
    if set_ActiveActivity(ActiveActivity)==False:
        if get_DebugLevel() > 0:
            print('Δεν μπόρεσε να καταχωρηθεί η ActiveActivity')    
    if not ActiveActivity:
        Activity=Activities.query.filter_by(id=1).first()
        flash(f"Δεν έχει σταλεί παράμετρος Δραστηριοτητας. Ενεγοποιείται η 1η δραστηριοτητα.", "success")        
        #ActivityText= "Κωδικός Δραστηριότητας:" + str(Activity.id) + '- Τίτλος:' + str(Activity.activity_title) + '<br>Περιγραφή' + str(Activity.activity_body)
        #flash(ActivityText, "success")
        ActiveActivity=1
        if set_ActiveActivity(ActiveActivity)==False:
            if get_DebugLevel() > 0:
                print('Δεν μπόρεσε να καταχωρηθεί η ActiveActivity')    

    Activity=Activities.query.filter_by(id=ActiveActivity).first()
    if not Activity:
        Activity=Activities.query.filter_by(id=1).first()
        flash(f"H Δραστηριότητα που ζητείται να ενεργοποιηθεί δεν βρέθηκε. Ενεργοποιείται η 1η δραστηριότητα.", "success")
        #ActivityText= "Κωδικός Δραστηριότητας:" + str(Activity.id) + '- Τίτλος:' + str(Activity.activity_title) + '<br>Περιγραή' + str(Activity.activity_body)
        #flash(ActivityText, "success")
        ActiveActivity=1
        if set_ActiveActivity(ActiveActivity)==False:
            if get_DebugLevel() > 0:
                print('Δεν μπόρεσε να καταχωρηθεί η ActiveActivity')    
    launchId = message_launch.get_launch_id()    
    update_launch_id(launchId)
    if get_DebugLevel() > 0:
        print("******LaunchId set to "+ launchId + " **********")
    
    tpl_kwargs = {
        'page_title': PAGE_TITLE,
        'is_deep_link_launch': message_launch.is_deep_link_launch(),
        'launch_data': message_launch.get_launch_data(),
        'launch_id': message_launch.get_launch_id(),
        'curr_user_name': message_launch_data.get('name', ''),
        'curr_user_email': message_launch_data.get('email', ''),
        'curr_user_username': message_launch_data.get('https://purl.imsglobal.org/spec/lti/claim/ext', {}).get('user_username',None),
        'curr_activity': get_ActiveActivity()
    }
    if get_DebugLevel() > 0:
        print(tpl_kwargs)

    
    
    
    
        
    userLogged=WorkingSessions.query.filter_by(email=email).first()
    workingSession = WorkingSessions.query.filter_by(workingStatus='owner').first()
    workingSession2 = WorkingSessions.query.filter_by(workingStatus='moodleowner').first()

    BookingSystem=get_config_bookingsystem()
    if BookingSystem:
        flash(f"Βρέθηκε ενεργοποιημένο το Booking System.", "success")                                         
        if get_BookingTimeslot()=='True':
            flash(f"Timeslot is not free.", "success")
            UserBooked=CheckIf_UserBooked(email)
            if UserBooked=='True':                                   
                if not workingSession and not userLogged and not workingSession2:    
                    if InsertWorkingSession(email, 'moodleowner'):                
                        login_user(user)                                                                                
                        if get_Use_xAPI():
                            mylrs.SendStatement(user.username, user.email,'Login from LMS','RemoteLab1')
                        flash(f"Η είσοδος του χρήστη με email: {email} στο εργαστήριο έγινε με επιτυχία.", "success")
                        flash(f"Έχει κάνει κράτηση τη παρουσα χρονοθυρίδα.<br>Συνδεθήκατε ως Κύριος Χρήστης Εργαστηρίου.", "success")                                                                 

                else:
                    if userLogged:                    
                        flash(f"Διαπιστώθηκε προηγούμενη σύνδεση, χωρίς σωστή έξοδο. Σύνδεση ξανά.", "success")                                                                                                     
                    elif workingSession or workingSession2:
                        flash(f"H χρονοθυρίδα είναι δεσμευμένη από άλλο χρηστη.<br>Συνδέεστε ως θεατής.<br>Κάποιες λειτουργίες στο εργαστήριο είναι απενεργοποιημένες.", "success")         
                        InsertWorkingSession(email, 'spectator')
                        login_user(user)
                        return redirect(url_for("root"))                                            
                    else:
                        #Δεσμευση timeslot επειδη είναι ελέυθερο και κάνει συνδεση του χρηστη
                        flash(f"Η χρονοθυρίδα της ώρας αυτής είναι διαθέσιμη.<br> Μπορείτε να κάνετε κράτηση και να συνδεθείτε ξανά ώς κύριος χρήστης.", "success")                        
                        flash(f"Συνδέεστε ως θεατής.<br>Κάποιες λειτουργίες στο εργαστήριο είναι απενεργοποιημένες.", "success")         
                        InsertWorkingSession(email, 'spectator')
                        login_user(user)
                        return redirect(url_for("root"))                                            
        else:    
            flash(f"H χρονοθυρίδα δεν είναι δεσμευμένη από άλλο χρηστη.<br>Συνδέεστε ως θεατής.<br>Κάποιες λειτουργίες στο εργαστήριο είναι απενεργοποιημένες.<br>Εάν θελετε να συνδεθείτε ως κυριος χρήστης κάντε κράτηση της παρουσας χρονοθυρίδας.", "success")                     
            InsertWorkingSession(email, 'spectator')
            login_user(user)
            return redirect(url_for("root"))                                                        
    else:
        if not workingSession and not userLogged and not workingSession2:    
            if InsertWorkingSession(email, 'moodleowner'):                
               login_user(user)                                                                                
               if get_Use_xAPI():
                    mylrs.SendStatement(user.username, user.email,'Login','RemoteLab1')
               flash(f"Η είσοδος του χρήστη με email: {email} στο εργαστήριο έγινε με επιτυχία.", "success")
               flash(f"Δεν υπάρχει χρήστης που χρησιμοποιεί το εργαστήριο.<br>Συνδεθήκατε ως Κύριος Χρήστης Εργαστηρίου.", "success")                                 
               return redirect(url_for("root"))                
        else:
            flash(f"Yπάρχει ήδη χρήστης που χρησιμοποιεί το εργαστήριο.<br>Συνδέεστε ως θεατής.<br>Κάποιες λειτουργίες στο εργαστήριο είναι απενεργοποιημένες.", "success")         
            InsertWorkingSession(email, 'spectator')
            login_user(user)            
    scoreresults=remotelab_scoreboard(message_launch.get_launch_id())
    if get_DebugLevel() > 0:
        print(scoreresults)
        print("test2")                
    return render_template('index.html', **tpl_kwargs)

def InsertWorkingSession(email, status):
    LabUser=WorkingSessions(email=email,workingStatus=status)
    db.session.add(LabUser)
    db.session.commit() 
    return True

def signup_lms(username,email,password):
    #print(username)
    #print(email)
    #print(password)
    
    username = username 
    email = email
    password = password
    encrypted_password = bcrypt.generate_password_hash(password).decode('UTF-8')

    user = User(username=username, email=email, password=encrypted_password)
    db.session.add(user)
    db.session.commit()
    

    return True
    

   

@app.route('/jwks/', methods=['GET'])
def get_jwks():
    tool_conf = ToolConfJsonFile(get_lti_config_path())
    #return jsonify({'keys': tool_conf.get_jwks()})
    return jsonify( tool_conf.get_jwks())

@app.route('/configure/<launch_id>/<difficulty>/', methods=['GET', 'POST'])
def configure(launch_id, difficulty):
    tool_conf = ToolConfJsonFile(get_lti_config_path())
    flask_request = FlaskRequest()
    launch_data_storage = get_launch_data_storage()
    message_launch = ExtendedFlaskMessageLaunch.from_cache(launch_id, flask_request, tool_conf,
                                                           launch_data_storage=launch_data_storage)

    if not message_launch.is_deep_link_launch():
        raise Forbidden('Must be a deep link!')

    launch_url = url_for('launch', _external=True)

    resource = DeepLinkResource()
    resource.set_url(launch_url + '?difficulty=' + difficulty) \
        .set_custom_params({'difficulty': difficulty}) \
        .set_title('Breakout ' + difficulty + ' mode!')

    html = message_launch.get_deep_link().output_response_form([resource])
    return html


@app.route('/api/score/<launch_id>/<earned_score>/<time_spent>/', methods=['POST'])
def score(launch_id, earned_score, time_spent):
    if get_DebugLevel() > 0:
        print("Enter api/score/")
    tool_conf = ToolConfJsonFile(get_lti_config_path())
    flask_request = FlaskRequest()
    launch_data_storage = get_launch_data_storage()
    message_launch = ExtendedFlaskMessageLaunch.from_cache(launch_id, flask_request, tool_conf,
                                                           launch_data_storage=launch_data_storage)

    resource_link_id = message_launch.get_launch_data() \
        .get('https://purl.imsglobal.org/spec/lti/claim/resource_link', {}).get('id')
    if get_DebugLevel() > 0:
        print(resource_link_id)
    if not message_launch.has_ags():
        raise Forbidden("Don't have grades!")

    sub = message_launch.get_launch_data().get('sub')
    if get_DebugLevel() > 0:
        print("Sub passed")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    if get_DebugLevel() > 0:
        print(timestamp)
    earned_score = int(earned_score)
    if get_DebugLevel() > 0:
        print(earned_score)
    time_spent = int(time_spent)
    if get_DebugLevel() > 0:
        print(time_spent)

    grades = message_launch.get_ags()
    if get_DebugLevel() > 0:
        print(grades)
    sc = Grade()
    sc.set_score_given(earned_score) \
        .set_score_maximum(100) \
        .set_timestamp(timestamp) \
        .set_activity_progress('Completed') \
        .set_grading_progress('FullyGraded') \
        .set_user_id(sub)

    sc_line_item = LineItem()
    sc_line_item.set_tag('score') \
        .set_score_maximum(100) \
        .set_label('Score')
    if resource_link_id:
        sc_line_item.set_resource_id(resource_link_id)

    grades.put_grade(sc, sc_line_item)
    if get_DebugLevel() > 0:
        print("Passed put_grades")
    tm = Grade()
    tm.set_score_given(time_spent) \
        .set_score_maximum(999) \
        .set_timestamp(timestamp) \
        .set_activity_progress('Completed') \
        .set_grading_progress('FullyGraded') \
        .set_user_id(sub)

    tm_line_item = LineItem()
    tm_line_item.set_tag('time') \
        .set_score_maximum(999) \
        .set_label('Time Taken')
    if resource_link_id:
        tm_line_item.set_resource_id(resource_link_id)

    result = grades.put_grade(tm, tm_line_item)
    if get_DebugLevel() > 0:
        print("Exit api/score/")
    return jsonify({'success': True, 'result': result.get('body')})

@app.route('/api/remotelab_score/<launch_id>/<ActivityStatus>/<ActivityGrade>/', methods=['POST'])
def remotelab_score(launch_id, ActivityStatus, ActivityGrade):
    global ActiveActivity
    activity = Activities.query.filter_by(id = ActiveActivity).first()    
    if get_DebugLevel() > 0:
        print("Enter api/score/")
    tool_conf = ToolConfJsonFile(get_lti_config_path())
    flask_request = FlaskRequest()
    launch_data_storage = get_launch_data_storage()
    message_launch = ExtendedFlaskMessageLaunch.from_cache(launch_id, flask_request, tool_conf,
                                                           launch_data_storage=launch_data_storage)

    resource_link_id = message_launch.get_launch_data() \
        .get('https://purl.imsglobal.org/spec/lti/claim/resource_link', {}).get('id')
    if get_DebugLevel() > 0:
        print(resource_link_id)
    if not message_launch.has_ags():
        raise Forbidden("Don't have grades!")

    sub = message_launch.get_launch_data().get('sub')
    if get_DebugLevel() > 0:
        print("Sub passed")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    if get_DebugLevel() > 0:
        print(timestamp)
    ActivityStatus = int(ActivityStatus)
    if get_DebugLevel() > 0:
        print(ActivityStatus)
    ActivityGrade = int(ActivityGrade)
    if get_DebugLevel() > 0:
        print(ActivityGrade)

    grades = message_launch.get_ags()
    if get_DebugLevel() > 0:
        print(grades)
    sc = Grade()
    sc.set_score_given(ActivityStatus) \
        .set_score_maximum(1) \
        .set_timestamp(timestamp) \
        .set_activity_progress('Completed') \
        .set_grading_progress('FullyGraded') \
        .set_user_id(sub)

    sc_line_item = LineItem()
    sc_line_item.set_tag('ActivityStatus' + str(ActiveActivity) + ': ' + str(activity.activity_title)) \
        .set_score_maximum(1) \
        .set_label('Activity ' + str(ActiveActivity) + ' Status' + ': ' + str(activity.activity_title))
    if resource_link_id:
        sc_line_item.set_resource_id(resource_link_id)

    grades.put_grade(sc, sc_line_item)
    if get_DebugLevel() > 0:
        print("Passed put_grades")
    tm = Grade()
    tm.set_score_given(ActivityGrade) \
        .set_score_maximum(10) \
        .set_timestamp(timestamp) \
        .set_activity_progress('Completed') \
        .set_grading_progress('FullyGraded') \
        .set_user_id(sub)

    tm_line_item = LineItem()
    tm_line_item.set_tag('ActivityGrade' + str(ActiveActivity) + ': ' + str(activity.activity_title)) \
        .set_score_maximum(10) \
        .set_label('Activity ' + str(ActiveActivity) + ' Grade' + ': ' + str(activity.activity_title))
    if resource_link_id:
        tm_line_item.set_resource_id(resource_link_id)

    result = grades.put_grade(tm, tm_line_item)
    if get_DebugLevel() > 0:
        print("Exit api/score/")
    return jsonify({'success': True, 'result': result.get('body')})



@app.route('/api/scoreboard/<launch_id>/', methods=['GET', 'POST'])
def scoreboard(launch_id):
    if get_DebugLevel() > 0:
        print("Enter api/scoreboard/")
    tool_conf = ToolConfJsonFile(get_lti_config_path())
    flask_request = FlaskRequest()
    launch_data_storage = get_launch_data_storage()
    message_launch = ExtendedFlaskMessageLaunch.from_cache(launch_id, flask_request, tool_conf,
                                                           launch_data_storage=launch_data_storage)

    resource_link_id = message_launch.get_launch_data() \
        .get('https://purl.imsglobal.org/spec/lti/claim/resource_link', {}).get('id')
    if get_DebugLevel() > 0:
        print('******Resource Link:' + str(resource_link_id))
    if not message_launch.has_nrps():
       if get_DebugLevel() > 0:
            print("Don't have nrps") 
       raise Forbidden("Don't have names and roles!")

    if not message_launch.has_ags():
        if get_DebugLevel() > 0:
            ("Don't have ags") 
        raise Forbidden("Don't have grades!")

    ags = message_launch.get_ags()
    if get_DebugLevel() > 0:
        print('Getting ags:' + str(ags))
    if  ags.can_create_lineitem():
        if get_DebugLevel() > 0:
            print("**************App Can create ags**********") 
        score_line_item = LineItem()
        if get_DebugLevel() > 0:
            print("======= score_line_item =========")
            print(str(score_line_item))
            print("=================================")

        score_line_item.set_tag('score') \
            .set_score_maximum(100) \
            .set_label('Score')
        if resource_link_id:
            score_line_item.set_resource_id(resource_link_id)

        score_line_item = ags.find_or_create_lineitem(score_line_item)
        scores = ags.get_grades(score_line_item)
        
        time_line_item = LineItem()
        time_line_item.set_tag('time') \
            .set_score_maximum(999) \
            .set_label('Time Taken')
        if resource_link_id:
            time_line_item.set_resource_id(resource_link_id)

        time_line_item = ags.find_or_create_lineitem(time_line_item)
        if get_DebugLevel() > 0:
            print("get_grades in App Can create ags")
        times = ags.get_grades(time_line_item)
    else:
        if get_DebugLevel() > 0:
            print("**********Getting Grades***********") 
        scores = ags.get_grades()
        if get_DebugLevel() > 0:
            print("====== scores ==========")
            print(str(scores))
            print("================")
        times = None
        
    members = message_launch.get_nrps().get_members()
    if get_DebugLevel() > 0:
        print(str(members))
    scoreboard_result = []
    if get_DebugLevel() > 0:
        print("Enterning Loop in Scores looking for User Grades")
    for sc in scores:
        result = {'score': sc['resultScore']}
        for tm in times:
            if tm['userId'] == sc['userId']:
                result['time'] = tm['resultScore']
                if get_DebugLevel() > 0:
                    print("Set Time")
                break
        for member in members:
            if member['user_id'] == sc['userId']:
                result['name'] = member.get('name', 'Unknown')
                if get_DebugLevel() > 0:
                    print("Set Name")
                break
        scoreboard_result.append(result)
    if get_DebugLevel() > 0:
        print("Exit api/scoreboard/")
    return jsonify(scoreboard_result)

@app.route('/api/remotelab_scoreboard/<launch_id>/', methods=['GET', 'POST'])
def remotelab_scoreboard(launch_id):
    if get_DebugLevel() > 0:
        print("Enter api/remotelab_scoreboard/")
    tool_conf = ToolConfJsonFile(get_lti_config_path())
    flask_request = FlaskRequest()
    launch_data_storage = get_launch_data_storage()
    message_launch = ExtendedFlaskMessageLaunch.from_cache(launch_id, flask_request, tool_conf,
                                                           launch_data_storage=launch_data_storage)

    resource_link_id = message_launch.get_launch_data() \
        .get('https://purl.imsglobal.org/spec/lti/claim/resource_link', {}).get('id')
    if get_DebugLevel() > 0:
        print('****** Resource Link ***********')
        print (resource_link_id)
        print('********************************')
    if not message_launch.has_nrps():
       if get_DebugLevel() > 0:
            print("Don't have nrps") 
       raise Forbidden("Don't have names and roles!")

    if not message_launch.has_ags():
        if get_DebugLevel() > 0:
            print("Don't have ags") 
        raise Forbidden("Don't have grades!")

    ags = message_launch.get_ags()
    if get_DebugLevel() > 0:
        print('Getting ags:' + str(ags))
    if  ags.can_create_lineitem():
        if get_DebugLevel() > 0:
            print("**************App Can create ags**********") 
        score_line_item = LineItem()
        if get_DebugLevel() > 0:
            print("======= score_line_item =========")
            print(str(score_line_item))
            print("=================================")

        score_line_item.set_tag('ActivityStatus') \
            .set_score_maximum(1) \
            .set_label('Activity Status')
        if resource_link_id:
            score_line_item.set_resource_id(resource_link_id)

        score_line_item = ags.find_or_create_lineitem(score_line_item)
        scores = ags.get_grades(score_line_item)
        
        time_line_item = LineItem()
        time_line_item.set_tag('ActivityGrade') \
            .set_score_maximum(10) \
            .set_label('Activity Grade')
        if resource_link_id:
            time_line_item.set_resource_id(resource_link_id)

        time_line_item = ags.find_or_create_lineitem(time_line_item)
        if get_DebugLevel() > 0:
            print("get_grades in App Can create ags")
        times = ags.get_grades(time_line_item)
    else:
        if get_DebugLevel() > 0:
            print("**********Getting Grades***********") 
        scores = ags.get_grades()
        if get_DebugLevel() > 0:
            print("====== scores ==========")
            print(str(scores))
            print("========================")
        times = None
        
    members = message_launch.get_nrps().get_members()
    if get_DebugLevel() > 0:
        print(str(members))        
    scoreboard_result = []
    if get_DebugLevel() > 0:
        print("Enterning Loop in Scores looking for User Grades")
    for sc in scores:
        result = {'ActivityStatus': sc['resultScore']}
        for tm in times:
            if tm['userId'] == sc['userId']:
                result['Grade'] = tm['resultScore']
                if get_DebugLevel() > 0:
                    print("Getting Grades")
                break
        for member in members:
            if member['user_id'] == sc['userId']:
                result['name'] = member.get('name', 'Unknown')
                if get_DebugLevel() > 0:
                    print("Set Name")
                break
        scoreboard_result.append(result)
    if get_DebugLevel() > 0:
        print("Exit api/scoreboard/")
        print("====== scoreboard_result ==========")
        print(scoreboard_result)
        print("===================================")

    return jsonify(scoreboard_result)
