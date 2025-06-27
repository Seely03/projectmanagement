from flask import render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import requests
from datetime import datetime, timedelta

from app import app, db, admin_required
from app.models.models import User, Project, Task, ProjectMember

# Temporary authentication solution for development
# This will be replaced with Amazon Cognito in production

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Username validation
        if not username:
            flash('Username is required!', 'danger')
            return redirect(url_for('register'))
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long!', 'danger')
            return redirect(url_for('register'))
        
        if len(username) > 50:
            flash('Username must be less than 50 characters!', 'danger')
            return redirect(url_for('register'))
        
        # Username format validation (letters only)
        import re
        if not re.match(r'^[a-zA-Z]+$', username):
            flash('Username can only contain letters!', 'danger')
            return redirect(url_for('register'))
        
        # Email validation
        if not email:
            flash('Email is required!', 'danger')
            return redirect(url_for('register'))
        
        # Check for email tags (plus sign in email)
        if '+' in email:
            flash('Email tags (using + symbol) are not allowed. Please use your primary email address.', 'danger')
            return redirect(url_for('register'))
        
        # Basic email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash('Please enter a valid email address!', 'danger')
            return redirect(url_for('register'))
        
        # Password validation
        if not password:
            flash('Password is required!', 'danger')
            return redirect(url_for('register'))
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long!', 'danger')
            return redirect(url_for('register'))
        
        if len(password) > 128:
            flash('Password must be less than 128 characters!', 'danger')
            return redirect(url_for('register'))
        
        # Password strength validation
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        
        if not (has_upper and has_lower and has_digit and has_special):
            flash('Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character!', 'danger')
            return redirect(url_for('register'))
        
        # Confirm password validation
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))
        
        # Check if username or email already exists
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            if user_exists.username == username:
                flash('Username already exists!', 'danger')
            else:
                flash('Email already exists!', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            is_admin=False  # Default is regular user
        )
        new_user.set_password(password)
        
        # Make first user an admin
        if User.query.count() == 0:
            new_user.is_admin = True
            
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('auth/register.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required!', 'danger')
            return redirect(url_for('login'))
            
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Invalid username or password!', 'danger')
            return redirect(url_for('login'))
            
        login_user(user)
        next_page = request.args.get('next')
        
        flash('Login successful!', 'success')
        return redirect(next_page or url_for('dashboard'))
        
    return render_template('auth/login.html')
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful!', 'success')
    return redirect(url_for('index'))
    
@app.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')
    
@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        
        if not username or not email:
            flash('Username and email are required!', 'danger')
            return redirect(url_for('edit_profile'))
            
        # Check if username or email already exists for other users
        user_exists = User.query.filter(
            (User.username == username) | (User.email == email),
            User.id != current_user.id
        ).first()
        
        if user_exists:
            flash('Username or email already exists!', 'danger')
            return redirect(url_for('edit_profile'))
            
        current_user.username = username
        current_user.email = email
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
        
    return render_template('auth/edit_profile.html')
    
@app.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('change_password'))
            
        if new_password != confirm_password:
            flash('New passwords do not match!', 'danger')
            return redirect(url_for('change_password'))
            
        if not current_user.check_password(current_password):
            flash('Current password is incorrect!', 'danger')
            return redirect(url_for('change_password'))
            
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('profile'))
        
    return render_template('auth/change_password.html')

@app.route('/users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    
    # Calculate statistics
    total_users = len(users)
    admin_users = len([u for u in users if u.is_admin])
    regular_users = total_users - admin_users
    
    # Get recent users (last 7 days)
    recent_cutoff = datetime.utcnow() - timedelta(days=7)
    recent_users = len([u for u in users if u.created_at > recent_cutoff])
    
    stats = {
        'total_users': total_users,
        'admin_users': admin_users,
        'regular_users': regular_users,
        'recent_users': recent_users
    }
    
    return render_template('auth/manage_users.html', users=users, stats=stats)

@app.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin_status(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent self-demotion
    if user.id == current_user.id:
        flash('You cannot change your own admin status!', 'danger')
        return redirect(url_for('manage_users'))
    
    # Toggle admin status
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin privileges {status} for user {user.username}.', 'success')
    return redirect(url_for('manage_users'))

@app.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        is_admin = request.form.get('is_admin') == 'on'
        
        # Username validation
        if not username:
            flash('Username is required!', 'danger')
            return redirect(url_for('create_user'))
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long!', 'danger')
            return redirect(url_for('create_user'))
        
        if len(username) > 50:
            flash('Username must be less than 50 characters!', 'danger')
            return redirect(url_for('create_user'))
        
        # Username format validation (letters only)
        import re
        if not re.match(r'^[a-zA-Z]+$', username):
            flash('Username can only contain letters!', 'danger')
            return redirect(url_for('create_user'))
        
        # Email validation
        if not email:
            flash('Email is required!', 'danger')
            return redirect(url_for('create_user'))
        
        # Check for email tags (plus sign in email)
        if '+' in email:
            flash('Email tags (using + symbol) are not allowed. Please use your primary email address.', 'danger')
            return redirect(url_for('create_user'))
        
        # Basic email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash('Please enter a valid email address!', 'danger')
            return redirect(url_for('create_user'))
        
        # Password validation
        if not password:
            flash('Password is required!', 'danger')
            return redirect(url_for('create_user'))
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long!', 'danger')
            return redirect(url_for('create_user'))
        
        if len(password) > 128:
            flash('Password must be less than 128 characters!', 'danger')
            return redirect(url_for('create_user'))
        
        # Password strength validation
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        
        if not (has_upper and has_lower and has_digit and has_special):
            flash('Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character!', 'danger')
            return redirect(url_for('create_user'))
        
        # Confirm password validation
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('create_user'))
        
        # Check if username or email already exists
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            if user_exists.username == username:
                flash('Username already exists!', 'danger')
            else:
                flash('Email already exists!', 'danger')
            return redirect(url_for('create_user'))
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            is_admin=is_admin
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        user_type = 'admin' if is_admin else 'regular user'
        flash(f'User {username} created successfully as {user_type}!', 'success')
        return redirect(url_for('manage_users'))
        
    return render_template('auth/create_user.html')

@app.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent self-deletion
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('manage_users'))
    
    # Check if user is the last admin
    if user.is_admin and User.query.filter_by(is_admin=True).count() == 1:
        flash('Cannot delete the last admin user!', 'danger')
        return redirect(url_for('manage_users'))
    
    # Check for user dependencies
    owned_projects = Project.query.filter_by(user_id=user.id).count()
    if owned_projects > 0:
        flash(f'Cannot delete user {user.username}. They own {owned_projects} project(s). Please reassign or delete these projects first.', 'danger')
        return redirect(url_for('manage_users'))
    
    # Check if user has assigned tasks
    assigned_tasks = Task.query.filter_by(user_id=user.id).count()
    if assigned_tasks > 0:
        flash(f'Cannot delete user {user.username}. They have {assigned_tasks} assigned task(s). Please reassign these tasks first.', 'danger')
        return redirect(url_for('manage_users'))
    
    # Remove user from project memberships
    ProjectMember.query.filter_by(user_id=user.id).delete()
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {username} has been deleted successfully.', 'success')
    return redirect(url_for('manage_users'))

# Cognito authentication setup (will be called in app.py if USE_COGNITO_AUTH=true)
def setup_cognito_auth():
    """Set up Cognito auth routes and integration"""
    try:
        # Import Cognito configuration and utilities
        from app.config.cognito import CognitoConfig
        from app.utils.cognito_utils import validate_jwt_token, refresh_tokens, get_user_info
        from flask import jsonify, make_response
        import boto3
        
        # Initialize boto3 Cognito client
        cognito_idp = boto3.client('cognito-idp', 
                                 region_name=CognitoConfig.AWS_REGION)
        
        # Override existing routes
        @app.route('/login', methods=['GET', 'POST'])
        def login():
            if current_user.is_authenticated:
                return redirect(url_for('dashboard'))
                
            if request.method == 'POST':
                # For API clients that expect local auth
                return jsonify({'error': 'Cognito authentication is enabled'}), 400
                
            # Redirect to the Cognito hosted UI
            cognito_login_url = (
                f"https://{CognitoConfig.COGNITO_DOMAIN}/login"
                f"?client_id={CognitoConfig.COGNITO_APP_CLIENT_ID}"
                f"&response_type=code"
                f"&scope={'+'.join(CognitoConfig.OAUTH2_SCOPES)}"
                f"&redirect_uri={CognitoConfig.COGNITO_REDIRECT_URI}"
            )
            return render_template('auth/cognito_login.html', cognito_login_url=cognito_login_url)
            
        @app.route('/register')
        def register():
            if current_user.is_authenticated:
                return redirect(url_for('dashboard'))
                
            # Redirect to Cognito hosted UI signup page
            cognito_signup_url = (
                f"https://{CognitoConfig.COGNITO_DOMAIN}/signup"
                f"?client_id={CognitoConfig.COGNITO_APP_CLIENT_ID}"
                f"&response_type=code"
                f"&scope={'+'.join(CognitoConfig.OAUTH2_SCOPES)}"
                f"&redirect_uri={CognitoConfig.COGNITO_REDIRECT_URI}"
            )
            return render_template('auth/cognito_register.html', cognito_signup_url=cognito_signup_url)
            
        @app.route('/logout')
        def logout():
            # Clear Flask-Login session
            if current_user.is_authenticated:
                logout_user()
                
            # Clear session data
            session.clear()
            
            # Redirect to Cognito logout
            cognito_logout_url = (
                f"https://{CognitoConfig.COGNITO_DOMAIN}/logout"
                f"?client_id={CognitoConfig.COGNITO_APP_CLIENT_ID}"
                f"&logout_uri={CognitoConfig.COGNITO_LOGOUT_URI}"
            )
            return redirect(cognito_logout_url)
            
        @app.route('/auth/callback')
        def callback():
            # Get authorization code from query parameters
            code = request.args.get('code')
            
            if not code:
                flash('Authentication failed. Please try again.', 'danger')
                return redirect(url_for('login'))
                
            try:
                # Exchange authorization code for tokens
                token_endpoint = f"https://{CognitoConfig.COGNITO_DOMAIN}/oauth2/token"
                payload = {
                    'grant_type': 'authorization_code',
                    'client_id': CognitoConfig.COGNITO_APP_CLIENT_ID,
                    'code': code,
                    'redirect_uri': CognitoConfig.COGNITO_REDIRECT_URI
                }
                
                # Add client secret if it exists in config
                client_secret = getattr(CognitoConfig, 'COGNITO_APP_CLIENT_SECRET', None)
                if client_secret:
                    payload['client_secret'] = client_secret
                    
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                
                # Make the token request
                token_response = requests.post(token_endpoint, data=payload, headers=headers)
                
                if token_response.status_code != 200:
                    flash('Failed to authenticate with Cognito.', 'danger')
                    return redirect(url_for('login'))
                    
                token_data = token_response.json()
                access_token = token_data['access_token']
                id_token = token_data['id_token']
                refresh_token = token_data.get('refresh_token')
                
                # Get user info from Cognito
                user_info = get_user_info(access_token)
                
                if not user_info or 'email' not in user_info:
                    flash('Failed to retrieve user information.', 'danger')
                    return redirect(url_for('login'))
                    
                email = user_info['email']
                
                # Check if user exists in our database
                user = User.query.filter_by(email=email).first()
                
                if not user:
                    # Create new user
                    username = user_info.get('preferred_username', email.split('@')[0])
                    
                    # Ensure username is unique
                    base_username = username
                    counter = 1
                    while User.query.filter_by(username=username).first():
                        username = f"{base_username}{counter}"
                        counter += 1
                        
                    new_user = User(
                        username=username,
                        email=email,
                        is_admin=False  # Default is regular user
                    )
                    
                    # Make first user an admin
                    if User.query.count() == 0:
                        new_user.is_admin = True
                        
                    db.session.add(new_user)
                    db.session.commit()
                    user = new_user
                    
                # Store tokens in session
                session['access_token'] = access_token
                session['id_token'] = id_token
                if refresh_token:
                    session['refresh_token'] = refresh_token
                    
                # Log in the user
                login_user(user)
                
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                app.logger.error(f"Cognito callback error: {str(e)}")
                flash('An error occurred during authentication.', 'danger')
                return redirect(url_for('login'))
                
        @app.route('/auth/refresh-token')
        @login_required
        def token_refresh():
            """Refresh the Cognito tokens"""
            refresh_token = session.get('refresh_token')
            
            if not refresh_token:
                return jsonify({'error': 'No refresh token found'}), 400
                
            try:
                tokens = refresh_tokens(refresh_token)
                
                if not tokens:
                    # If refresh fails, redirect to login
                    logout_user()
                    session.clear()
                    flash('Your session has expired. Please log in again.', 'warning')
                    return redirect(url_for('login'))
                    
                # Update session with new tokens
                session['access_token'] = tokens['access_token']
                session['id_token'] = tokens['id_token']
                
                return jsonify({'success': True})
                
            except Exception as e:
                app.logger.error(f"Token refresh error: {str(e)}")
                logout_user()
                session.clear()
                return jsonify({'error': 'Failed to refresh token'}), 400
                
        # Create templates for Cognito auth
        # These templates will be created later
                
        print("Cognito authentication routes have been set up")
        
    except Exception as e:
        app.logger.error(f"Error setting up Cognito auth: {str(e)}")
        print(f"Error setting up Cognito auth: {str(e)}")
        # Fallback to local auth is handled in app.py 