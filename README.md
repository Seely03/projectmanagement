# Project Manager

A web-based project management tool built with Flask that allows users to create, track, and manage projects and tasks.

## Features

- User authentication with role-based access control (admin and regular users)
- Project management with status tracking
- Task management with assignees and due dates
- Dashboard with project and task overview
- Responsive design for desktop and mobile devices

## Requirements

- Python 3.7+
- Flask and other dependencies listed in requirements.txt

## Local Development Setup

1. Clone the repository:
```
git clone <repository-url>
cd project-manager
```

2. Create a virtual environment and activate it:
```
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Set up environment variables (create a .env file):
```
SECRET_KEY=your-secret-key
FLASK_APP=app.py
FLASK_ENV=development
```

5. Run the application:
```
flask run
or
python run.py
```

6. Access the application at http://localhost:5000

## Authentication

The application includes a built-in authentication system for development. In production, it can be configured to use Amazon Cognito for authentication.

### Development Authentication

- First registered user is automatically assigned admin role
- Subsequent users are assigned regular user role

### AWS Deployment & Cognito Authentication (Production)

For production deployment on AWS Lightsail:

1. Create an AWS Lightsail instance
2. Set up a Cognito User Pool for authentication
3. Configure the application to use Cognito for authentication
4. Deploy the application to Lightsail

Detailed instructions for AWS deployment are in the `docs/aws-deployment.md` file.

## Database Schema

The application uses SQLite for development and can be configured to use other databases in production. The schema includes:

- Users (id, username, email, password_hash, is_admin, created_at)
- Projects (id, title, description, status, priority, start_date, end_date, created_at, user_id)
- Tasks (id, title, description, status, priority, due_date, created_at, project_id, user_id)

## License

This project is licensed under the MIT License - see the LICENSE file for details. 