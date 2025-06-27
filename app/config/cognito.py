import os
from dotenv import load_dotenv

load_dotenv()

class CognitoConfig:
    """AWS Cognito configuration settings for authentication"""
    
    # AWS Region and Cognito Pool settings
    AWS_REGION = os.environ.get('AWS_REGION')
    COGNITO_USER_POOL_ID = os.environ.get('COGNITO_USER_POOL_ID')
    COGNITO_APP_CLIENT_ID = os.environ.get('COGNITO_APP_CLIENT_ID')
    COGNITO_DOMAIN = os.environ.get('COGNITO_DOMAIN')
    
    # OAuth2 redirect URIs
    COGNITO_REDIRECT_URI = os.environ.get('COGNITO_REDIRECT_URI')
    COGNITO_LOGOUT_URI = os.environ.get('COGNITO_LOGOUT_URI')
    
    # OAuth2 Scopes
    OAUTH2_SCOPES = ['openid', 'email', 'profile']
    
    # JWT Settings
    JWT_HEADER_TYPE = 'JWT'
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = True  # Set to False in dev environment
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Token expiration settings (in seconds)
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days 