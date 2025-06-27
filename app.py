from app import app
from app import db
from app.models.models import User, Project, Task
import os

# Determine which auth method to use
use_cognito = os.environ.get('USE_COGNITO_AUTH', 'false').lower() == 'true'

if use_cognito:
    # Initialize Cognito authentication
    try:
        from app.config.cognito import CognitoConfig
        app.config.from_object(CognitoConfig)
        from app.controllers.auth_controller import setup_cognito_auth
        setup_cognito_auth()
        print("Using Cognito authentication")
    except Exception as e:
        print(f"Error setting up Cognito auth: {e}")
        print("Falling back to local authentication")
        from app.controllers.auth_controller import *
else:
    # Use local authentication (development)
    from app.controllers.auth_controller import *
    print("Using local authentication")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 