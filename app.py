from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from ultralytics import YOLO
from PIL import Image
import numpy as np
import cv2
import os 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.message import EmailMessage
from datetime import datetime
import mimetypes


# Initialize the Flask app and configure the database
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# Path to save uploaded images
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Model for User table in the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)

# Routes for pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id  # Store user ID in session
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('auth.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        age = request.form.get('age')
        gender = request.form.get('gender')
        mobile = request.form.get('mobile')

        if len(mobile) != 10 or not mobile.isdigit():
            flash('Mobile number must be exactly 10 digits.', 'danger')
            return render_template('auth.html')

        if User.query.filter_by(email=email).first():
            flash('Email address already in use. Please choose a different one.', 'danger')
            return render_template('auth.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('auth.html')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password, age=age, gender=gender, mobile=mobile)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('auth.html')

@app.route('/home')
def home():
    return render_template('home.html')

# Load the pre-trained YOLOv8 model
model = YOLO('best.pt')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the uploaded file
        uploaded_file = request.files['image_file']

        if uploaded_file.filename != '':
            # Save the uploaded file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(file_path)

            # Read the image using OpenCV
            image = cv2.imread(file_path)

            # Perform inference using YOLOv8
            results = model(image)
            result = results[0]  # This is the detection result object

            # Get bounding boxes (xywh format) and class labels
            boxes = result.boxes.xywh.cpu().numpy()  # Get bounding boxes in xywh format
            labels = result.names  # Class names (labels)

            # Check if any accident class is detected
            accident_detected = False
            for i, box in enumerate(boxes):
                class_id = int(result.boxes.cls[i])  # Get the class index from the result
                label_name = labels[class_id]  # Get the class name from the class index

                # You can define the accident-related class name (you can replace it with your class)
                if "accident" in label_name.lower():  # Assuming accident label contains "accident"
                    accident_detected = True

                # Draw bounding box and label on the image
                x_center, y_center, width, height = box  # Extract xywh
                x1 = int((x_center - width / 2))
                y1 = int((y_center - height / 2))
                x2 = int((x_center + width / 2))
                y2 = int((y_center + height / 2))

                # Draw bounding box and label on the image
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Draw box
                cv2.putText(image, label_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Save the result image with bounding boxes
            result_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result_' + uploaded_file.filename)
            cv2.imwrite(result_image_path, image)

            # Return the result image and accident detection status to the user
            detection_message = "Accident Detected" if accident_detected else "No Accident Detected"
            print(detection_message)

            # Send email notification if an accident is detected
            if accident_detected:
                send_email_notification(uploaded_file.filename)
                print("Send")

            return render_template('upload.html', result_image=url_for('uploaded_file', filename='result_' + uploaded_file.filename), detection_message=detection_message)

    # If it's a GET request, render the upload form
    return render_template('upload.html')

def send_email_notification(filename):
    # Content for the email
    msg = 'Dear Sir,'
    m = 'We have detected an accident in the uploaded image.'
    dt = "Detected on "
    tm = 'at '
    im = "Kindly have a look at the attached photo and take necessary actions."
    t = 'Regards,'
    t1 = 'Vehicle Accident Detection System'

    date = datetime.now().strftime("%Y-%m-%d")
    timeStamp = datetime.now().strftime("%H:%M:%S")

    mail_content = msg + '\n' + m + ' ' + dt + date + tm + timeStamp + '.' + im + '\n' + '\n' + t + '\n' + t1

    # Sender details
    sender_address = "cse.takeoff@gmail.com"  # Use your own email address
    sender_pass = "digkagfgyxcjltup" # Use your own email password
    receiver_addresses = ["yashasgupta68@gmail.com"]  # Admin email to receive the notification

    # Create the email message
    newMessage = EmailMessage()
    newMessage['Subject'] = "Vehicle Accident Detection"
    newMessage['From'] = sender_address
    newMessage['To'] = ', '.join(receiver_addresses)
    newMessage.set_content(mail_content)

    # Attach the image
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result_' + filename)
    with open(image_path, 'rb') as f:
        image_data = f.read()
        # Get mime type from filename extension
        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type and mime_type.startswith('image/'):
            image_type = mime_type.split('/')[1]
        else:
            image_type = 'jpeg'  # default fallback
        image_name = os.path.basename(image_path)

    newMessage.add_attachment(image_data, maintype='image', subtype=image_type, filename=image_name)

    # Send the email (using SMTP with SSL for Gmail)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_address, sender_pass)
        smtp.send_message(newMessage)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Get port from environment variable for deployment (Render, Railway, etc.)
    port = int(os.environ.get('PORT', 5000))
    # Bind to 0.0.0.0 for deployment, 127.0.0.1 for local development
    host = '0.0.0.0' if os.environ.get('PORT') else '127.0.0.1'
    app.run(host=host, port=port, debug=os.environ.get('FLASK_DEBUG', 'True') == 'True')
