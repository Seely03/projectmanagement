# AWS Cognito Integration Guide

This guide explains how to integrate Amazon Cognito authentication with the Flask Project Manager application.

## Overview

AWS Cognito provides a secure, scalable user directory that can be integrated with our Flask application. This allows us to:
- Manage user sign-up, sign-in, and access control
- Add multi-factor authentication
- Support social identity providers like Google, Facebook, and Amazon
- Implement secure, standards-based authentication

## Prerequisites

- AWS account with access to create Cognito resources
- Project Manager application set up
- Basic understanding of OAuth 2.0 flows

## Step 1: Create a Cognito User Pool

1. Sign in to the AWS Management Console and open the Cognito console
2. Choose "Manage User Pools" and "Create a user pool"
3. Enter a name for your user pool (e.g., "ProjectManagerUserPool")
4. Configure sign-in options:
   - Enable email and username as sign-in options
   - Configure password policies
5. Configure security requirements:
   - Choose password strength
   - Enable MFA if needed
   - Configure account recovery options
6. Configure sign-up experience:
   - Select required attributes (email at minimum)
   - Configure auto-verification of email
7. Configure message delivery:
   - Use Cognito's default email functionality or configure SES
8. Integrate your app:
   - Create an app client
   - Disable client secret generation if using the Authorization Code grant with PKCE
   - Set the callback URLs (e.g., https://yourdomain.com/auth/callback)
   - Configure OAuth 2.0 settings:
     - Authorization Code Grant flow
     - Enable "openid", "email", "profile" scopes
9. Review and create the user pool

## Step 2: Install Required Packages

Add the following packages to your requirements.txt file:

```
boto3==1.28.62
flask-awscognito==1.3.0
```

Then install the dependencies:

```bash
pip install -r requirements.txt
```

## Step 3: Configure Cognito Environment Variables

Update your .env file with the following variables:

```
# AWS Cognito Configuration
AWS_REGION=your-aws-region
COGNITO_USER_POOL_ID=your-user-pool-id
COGNITO_APP_CLIENT_ID=your-app-client-id
COGNITO_DOMAIN=your-cognito-domain.auth.your-region.amazoncognito.com
COGNITO_REDIRECT_URI=https://yourdomain.com/auth/callback
COGNITO_LOGOUT_URI=https://yourdomain.com/
```

## Step 4: Create Cognito Configuration File

Create a new file `app/config/cognito.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

class CognitoConfig:
    AWS_REGION = os.environ.get('AWS_REGION')
    COGNITO_USER_POOL_ID = os.environ.get('COGNITO_USER_POOL_ID')
    COGNITO_APP_CLIENT_ID = os.environ.get('COGNITO_APP_CLIENT_ID')
    COGNITO_DOMAIN = os.environ.get('COGNITO_DOMAIN')
    COGNITO_REDIRECT_URI = os.environ.get('COGNITO_REDIRECT_URI')
    COGNITO_LOGOUT_URI = os.environ.get('COGNITO_LOGOUT_URI')
    
    # OAuth2 Settings
    OAUTH2_SCOPES = ['openid', 'email', 'profile']
    
    # JWT Claims
    JWT_HEADER_TYPE = 'JWT'
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_SECRET_KEY = os.environ.get('SECRET_KEY')
```

## Step 5: Implement Cognito Authentication

### 1. Update the auth_controller.py file

Modify the `auth_controller.py` file to use Cognito authentication:

```python
from flask import redirect, url_for, session, request, make_response
from flask_awscognito import AWSCognitoAuthentication
import boto3
import json
import requests
from app import app
from app.config.cognito import CognitoConfig
from app.models.models import User

# Initialize Cognito
app.config.from_object(CognitoConfig)
aws_auth = AWSCognitoAuthentication(app)
cognito_client = boto3.client('cognito-idp', region_name=CognitoConfig.AWS_REGION)

def setup_cognito_auth():
    """Set up Cognito auth routes and integration"""
    
    @app.route('/auth/login')
    def login():
        return redirect(aws_auth.get_sign_in_url())
        
    @app.route('/auth/logout')
    def logout():
        session.clear()
        logout_url = f"https://{CognitoConfig.COGNITO_DOMAIN}/logout?client_id={CognitoConfig.COGNITO_APP_CLIENT_ID}&logout_uri={CognitoConfig.COGNITO_LOGOUT_URI}"
        return redirect(logout_url)
        
    @app.route('/auth/callback')
    def callback():
        # Exchange authorization code for tokens
        tokens = aws_auth.get_access_token(request.args)
        access_token = tokens['access_token']
        id_token = tokens['id_token']
        refresh_token = tokens['refresh_token']
        
        # Get user info from Cognito
        user_info = aws_auth.get_user_info(access_token)
        
        # Check if user exists in our database
        user = User.query.filter_by(email=user_info['email']).first()
        
        if not user:
            # Create new user
            new_user = User(
                username=user_info.get('preferred_username', user_info['email']),
                email=user_info['email'],
                password_hash='cognito_user',  # Not used for authentication
                is_admin=False  # Default to regular user
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
        session['refresh_token'] = refresh_token
        session['user_id'] = user.id
        
        return redirect(url_for('dashboard'))
    
    # Modify the load_user function in app.py
    @app.login_manager.request_loader
    def load_user_from_request(request):
        # Check if user is logged in via session
        user_id = session.get('user_id')
        if user_id:
            return User.query.get(int(user_id))
            
        # Check if access token is provided in Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            access_token = auth_header.split('Bearer ')[1]
            try:
                # Verify the token with Cognito
                user_info = aws_auth.get_user_info(access_token)
                user = User.query.filter_by(email=user_info['email']).first()
                return user
            except:
                pass
                
        return None
```

### 2. Add a cognito_utils.py helper file

Create a new file `app/utils/cognito_utils.py` for helper functions:

```python
import requests
import json
import base64
import time
from jose import jwk, jwt
from jose.utils import base64url_decode
from app.config.cognito import CognitoConfig

def validate_jwt_token(token):
    """Validate the JWT token from Cognito"""
    # Get the key id from the token header
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']
    
    # Get the public keys from Cognito
    keys_url = f'https://cognito-idp.{CognitoConfig.AWS_REGION}.amazonaws.com/{CognitoConfig.COGNITO_USER_POOL_ID}/.well-known/jwks.json'
    keys_response = requests.get(keys_url)
    keys = json.loads(keys_response.text)['keys']
    
    # Find the key matching the kid
    key = [k for k in keys if k['kid'] == kid][0]
    
    # Verify the signature
    hmac_key = jwk.construct(key)
    message, encoded_signature = token.rsplit('.', 1)
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    
    # Verify token
    if not hmac_key.verify(message.encode('utf-8'), decoded_signature):
        return False
        
    # Parse claims
    claims = jwt.get_unverified_claims(token)
    
    # Verify expiration
    if time.time() > claims['exp']:
        return False
        
    # Verify audience (client id)
    if claims['aud'] != CognitoConfig.COGNITO_APP_CLIENT_ID:
        return False
        
    # Verify issuer
    if claims['iss'] != f'https://cognito-idp.{CognitoConfig.AWS_REGION}.amazonaws.com/{CognitoConfig.COGNITO_USER_POOL_ID}':
        return False
        
    return claims

def refresh_tokens(refresh_token):
    """Refresh the access and ID tokens using the refresh token"""
    auth = base64.b64encode(f"{CognitoConfig.COGNITO_APP_CLIENT_ID}:{CognitoConfig.COGNITO_APP_CLIENT_SECRET}".encode('utf-8')).decode('utf-8')
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {auth}'
    }
    
    data = {
        'grant_type': 'refresh_token',
        'client_id': CognitoConfig.COGNITO_APP_CLIENT_ID,
        'refresh_token': refresh_token
    }
    
    response = requests.post(
        f'https://{CognitoConfig.COGNITO_DOMAIN}/oauth2/token',
        headers=headers,
        data=data
    )
    
    if response.status_code == 200:
        tokens = response.json()
        return {
            'access_token': tokens['access_token'],
            'id_token': tokens['id_token']
        }
    
    return None
```

## Step 6: Update Templates for Cognito

Update your login and register templates to redirect to Cognito:

In `app/templates/auth/login.html`, replace the form with:

```html
{% extends 'base.html' %}

{% block title %}Login - Project Manager{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card shadow">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0">Login</h4>
                </div>
                <div class="card-body p-4 text-center">
                    <p>You will be redirected to Amazon Cognito for secure authentication.</p>
                    <a href="{{ url_for('login') }}" class="btn btn-primary btn-lg mt-3">
                        <i class="fas fa-sign-in-alt"></i> Sign in with Cognito
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

## Step 7: Switch Between Development and Production Auth

To easily switch between development (local) and production (Cognito) authentication:

1. Add an environment variable to control which auth method to use:

```
# In .env file
USE_COGNITO_AUTH=false  # Set to true in production
```

2. Update app.py to conditionally initialize the appropriate auth method:

```python
# In app.py
import os
from dotenv import load_dotenv

load_dotenv()

# ... other imports and app setup ...

# Determine which auth method to use
use_cognito = os.environ.get('USE_COGNITO_AUTH', 'false').lower() == 'true'

if use_cognito:
    # Initialize Cognito auth
    from app.controllers.auth_controller import setup_cognito_auth
    setup_cognito_auth()
else:
    # Use local authentication (development)
    from app.controllers.auth_controller import *  # Import local auth routes
```

## Testing Cognito Integration

1. Create test users in the Cognito User Pool:
   - Go to the User Pool in AWS Console
   - Select "Users and groups"
   - Click "Create user"
   - Enter user details and create the user
   
2. Test the authentication flow:
   - Access your application
   - Click "Login"
   - You should be redirected to the Cognito hosted UI
   - Log in with a test user
   - You should be redirected back to your application and be logged in

## Troubleshooting

- **Redirect URI Issues**: Ensure the callback URL is exactly as configured in Cognito
- **Token Validation Errors**: Check your AWS region and User Pool ID
- **CORS Errors**: Update your CORS settings in both your Flask app and Cognito
- **Missing User Attributes**: Ensure required attributes are collected during registration

## Security Considerations

- Store tokens securely in server-side sessions, not localStorage
- Implement CSRF protection for all authenticated requests
- Set secure and httpOnly flags on cookies
- Always validate tokens on the server before granting access
- Implement proper token refresh logic to handle expired tokens 