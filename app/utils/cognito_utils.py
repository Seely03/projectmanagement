import requests
import json
import base64
import time
from jose import jwk, jwt
from jose.utils import base64url_decode
from app.config.cognito import CognitoConfig

def validate_jwt_token(token):
    """
    Validate the JWT token from Cognito
    
    Args:
        token: The JWT token to validate
        
    Returns:
        dict: The claims from the token if valid, False otherwise
    """
    # Get the key id from the token header
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']
    
    # Get the public keys from Cognito
    keys_url = f'https://cognito-idp.{CognitoConfig.AWS_REGION}.amazonaws.com/{CognitoConfig.COGNITO_USER_POOL_ID}/.well-known/jwks.json'
    keys_response = requests.get(keys_url)
    keys = json.loads(keys_response.text)['keys']
    
    # Find the key matching the kid
    key = next((k for k in keys if k['kid'] == kid), None)
    if not key:
        return False
    
    # Verify the signature
    hmac_key = jwk.construct(key)
    message, encoded_signature = token.rsplit('.', 1)
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    
    # Verify token
    if not hmac_key.verify(message.encode('utf-8'), decoded_signature):
        return False
        
    # Parse claims
    claims = jwt.get_unverified_claims(token)
    
    # Verify token is not expired
    if time.time() > claims['exp']:
        return False
        
    # Verify audience (client id)
    if claims['aud'] != CognitoConfig.COGNITO_APP_CLIENT_ID:
        return False
        
    # Verify issuer
    issuer = f'https://cognito-idp.{CognitoConfig.AWS_REGION}.amazonaws.com/{CognitoConfig.COGNITO_USER_POOL_ID}'
    if claims['iss'] != issuer:
        return False
        
    return claims

def refresh_tokens(refresh_token):
    """
    Refresh the access and ID tokens using the refresh token
    
    Args:
        refresh_token: The refresh token
        
    Returns:
        dict: The new tokens if successful, None otherwise
    """
    # Create a basic auth header if client secret is provided
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # Add client authentication if client secret exists
    client_secret = getattr(CognitoConfig, 'COGNITO_APP_CLIENT_SECRET', None)
    if client_secret:
        auth = base64.b64encode(
            f"{CognitoConfig.COGNITO_APP_CLIENT_ID}:{client_secret}".encode('utf-8')
        ).decode('utf-8')
        headers['Authorization'] = f'Basic {auth}'
    
    # Prepare data for token refresh
    data = {
        'grant_type': 'refresh_token',
        'client_id': CognitoConfig.COGNITO_APP_CLIENT_ID,
        'refresh_token': refresh_token
    }
    
    # Make the request to the token endpoint
    token_url = f'https://{CognitoConfig.COGNITO_DOMAIN}/oauth2/token'
    response = requests.post(token_url, headers=headers, data=data)
    
    # Return tokens if successful
    if response.status_code == 200:
        tokens = response.json()
        return {
            'access_token': tokens['access_token'],
            'id_token': tokens['id_token']
        }
    
    return None

def get_user_info(access_token):
    """
    Get user info from Cognito using the access token
    
    Args:
        access_token: The access token
        
    Returns:
        dict: User information if successful, None otherwise
    """
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    userinfo_url = f'https://{CognitoConfig.COGNITO_DOMAIN}/oauth2/userInfo'
    response = requests.get(userinfo_url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    
    return None 