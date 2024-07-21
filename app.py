from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

# Initialize Flask app
app = Flask(__name__)

# Configure session to use filesystem (you can change this for production)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SQLAlchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define User model for SQLAlchemy
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

# Function to check password requirements
def check_password_requirements(password):
    missing_requirements = []
    if len(password) < 8:
        missing_requirements.append('be at least 8 characters long')
    if not any(c.islower() for c in password):
        missing_requirements.append('at least one lowercase letter')
    if not any(c.isupper() for c in password):
        missing_requirements.append('at least one uppercase letter')
    if not any(c.isdigit() for c in password):
        missing_requirements.append('at least one digit')
    return missing_requirements

# Initialize database (create tables if they don't exist)
with app.app_context():
    db.create_all()

# Route for index page (sign-in form)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check user credentials
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('secret'))
        else:
            return render_template('index.html', error="Invalid email or password")

    return render_template('index.html')

# Route for sign-up page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check password requirements
        missing_requirements = check_password_requirements(password)
        if password != confirm_password:
            missing_requirements.append("Passwords do not match")

        if missing_requirements:
            return render_template('signup.html', missing_requirements=missing_requirements)

        # Check if email is already used
        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error="Email address already registered")

        # Save new user to database
        new_user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('thankyou'))

    return render_template('signup.html')

# Route for thank-you page
@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

# Route for secret page
@app.route('/secret')
def secret():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('secretPage.html')

# Route for sign-in report page
@app.route('/report')
def report():
    return render_template('report.html')

if __name__ == '__main__':
    app.run(debug=True)
