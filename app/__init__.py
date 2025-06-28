from flask import Flask, flash, redirect, url_for, render_template, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_required
from flask_migrate import Migrate
from functools import wraps
import os
from dotenv import load_dotenv
from datetime import datetime
import sys

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app with correct template and static paths
app = Flask(__name__,
            template_folder='templates',
            static_folder='static')

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')

# Use test DB if running under pytest or FLASK_ENV is 'testing'
if ('pytest' in sys.modules) or (os.environ.get('FLASK_ENV') == 'testing'):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///project_manager.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set explicit USE_COGNITO_AUTH value
app.config['USE_COGNITO_AUTH'] = os.environ.get('USE_COGNITO_AUTH', 'false').lower() == 'true'

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Override any platform-set CSP headers
@app.after_request
def override_csp_headers(response):
    # Remove any existing CSP headers that might be set by platform
    response.headers.pop('Content-Security-Policy', None)
    response.headers.pop('X-Content-Security-Policy', None)
    response.headers.pop('X-WebKit-CSP', None)
    
    # Set a permissive CSP that allows all necessary scripts
    response.headers['Content-Security-Policy'] = (
    "default-src 'self' https:; "
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; "
    "script-src-elem 'self' 'unsafe-inline' 'unsafe-eval' https:; "
    "script-src-attr 'self' 'unsafe-inline'; "
    "style-src 'self' 'unsafe-inline' https:; "
    "font-src 'self' https:; "
    "img-src 'self' data: https:; "
    "connect-src 'self' https:; "
    "frame-ancestors 'none';"
)
    
    return response

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Import models
from app.models.models import User, Project, Task, ProjectMember

# Set up the login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Add context processor for templates
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Basic routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        projects = Project.query.all()
    else:
        # Show projects where the user is a member or owner
        project_ids = db.session.query(ProjectMember.project_id).filter_by(user_id=current_user.id).all()
        owned_project_ids = db.session.query(Project.id).filter_by(user_id=current_user.id).all()
        all_project_ids = [pid[0] for pid in project_ids] + [pid[0] for pid in owned_project_ids]
        projects = Project.query.filter(Project.id.in_(all_project_ids)).all()
    return render_template('dashboard.html', projects=projects)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

# Import controllers (must be after route definitions to avoid circular imports)
from app.controllers import auth_controller, project_controller, task_controller