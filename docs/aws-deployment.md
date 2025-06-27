# AWS Deployment Guide

This guide explains how to deploy the Project Manager application to AWS Lightsail and integrate it with Amazon Cognito for authentication.

## Setting Up AWS Lightsail

1. Create an AWS account if you don't have one
2. Navigate to the AWS Lightsail console
3. Create a new Lightsail instance:
   - Choose a platform: Linux/Unix
   - Select a blueprint: OS Only (Ubuntu 20.04 LTS)
   - Choose an instance plan (2 GB RAM recommended)
   - Name your instance (e.g., project-manager)
   - Click "Create Instance"
4. Once the instance is running, set up a static IP:
   - Go to the Networking tab
   - Create a static IP and attach it to your instance
5. Configure firewall rules:
   - Go to the Networking tab
   - Add custom rules for HTTP (port 80) and HTTPS (port 443)

## Setting Up the Application on Lightsail

1. SSH into your instance (use the browser-based SSH or your own SSH client)
2. Update the system:
   ```bash
   sudo apt-get update
   sudo apt-get upgrade -y
   ```
3. Install required packages:
   ```bash
   sudo apt-get install -y python3-pip python3-venv nginx git
   ```
4. Clone the repository:
   ```bash
   git clone <repository-url> /home/ubuntu/project-manager
   cd /home/ubuntu/project-manager
   ```
5. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
6. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install gunicorn
   ```
7. Create a .env file:
   ```bash
   nano .env
   ```
   Add environment variables:
   ```
   SECRET_KEY=your-secure-secret-key
   DATABASE_URL=sqlite:///project_manager.db
   FLASK_APP=app.py
   FLASK_ENV=production
   ```

## Setting Up Amazon Cognito for Authentication

1. Go to the Amazon Cognito console
2. Create a new User Pool:
   - Name your User Pool (e.g., ProjectManagerUsers)
   - Configure sign-in options (email and username)
   - Configure security requirements
   - Configure MFA (optional)
   - Configure email delivery
   - Add required attributes (email, name)
   - Set up a domain name
3. Create a new App Client:
   - Name your app client (e.g., ProjectManagerWebApp)
   - Generate a client secret
   - Configure callback URLs (https://your-lightsail-ip/auth/callback)
   - Configure OAuth flows and scopes
4. Note the User Pool ID, App Client ID, and App Client Secret

## Integrating Cognito with the Application

1. Install the required packages:
   ```bash
   pip install boto3 flask-awscognito
   ```
2. Update your .env file with Cognito settings:
   ```
   AWS_REGION=your-region
   COGNITO_USER_POOL_ID=your-user-pool-id
   COGNITO_APP_CLIENT_ID=your-app-client-id
   COGNITO_APP_CLIENT_SECRET=your-app-client-secret
   COGNITO_DOMAIN=your-cognito-domain
   ```
3. Replace the local authentication in auth_controller.py with the Cognito implementation:
   - Edit the file to use the setup_cognito_auth() function
   - Configure callback routes for OAuth flows

## Setting Up Nginx and Gunicorn

1. Create a new Nginx site configuration:
   ```bash
   sudo nano /etc/nginx/sites-available/project-manager
   ```
   Add the following configuration:
   ```nginx
   server {
       listen 80;
       server_name your-domain-or-ip;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```
2. Enable the site and restart Nginx:
   ```bash
   sudo ln -s /etc/nginx/sites-available/project-manager /etc/nginx/sites-enabled
   sudo systemctl restart nginx
   ```
3. Create a systemd service file for Gunicorn:
   ```bash
   sudo nano /etc/systemd/system/project-manager.service
   ```
   Add the following:
   ```
   [Unit]
   Description=Gunicorn instance to serve project-manager
   After=network.target
   
   [Service]
   User=ubuntu
   Group=www-data
   WorkingDirectory=/home/ubuntu/project-manager
   Environment="PATH=/home/ubuntu/project-manager/venv/bin"
   EnvironmentFile=/home/ubuntu/project-manager/.env
   ExecStart=/home/ubuntu/project-manager/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 -m 007 app:app
   
   [Install]
   WantedBy=multi-user.target
   ```
4. Start and enable the service:
   ```bash
   sudo systemctl start project-manager
   sudo systemctl enable project-manager
   ```

## Setting Up HTTPS with Let's Encrypt

If you're using a custom domain:

1. Install Certbot:
   ```bash
   sudo apt-get install -y certbot python3-certbot-nginx
   ```
2. Obtain an SSL certificate:
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```
3. Follow the prompts to configure HTTPS
4. Update your callback URLs in Cognito to use HTTPS

## Testing the Deployment

1. Open your browser and navigate to your domain or IP address
2. Test the application functionality
3. Verify that Cognito authentication is working correctly

## Maintenance and Updates

To update the application:

1. SSH into your Lightsail instance
2. Navigate to the project directory:
   ```bash
   cd /home/ubuntu/project-manager
   ```
3. Pull the latest changes:
   ```bash
   git pull
   ```
4. Install any new dependencies:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```
5. Restart the service:
   ```bash
   sudo systemctl restart project-manager
   ```

## Monitoring and Logs

- Application logs: `/var/log/syslog`
- Nginx access logs: `/var/log/nginx/access.log`
- Nginx error logs: `/var/log/nginx/error.log`

You can also set up AWS CloudWatch for more advanced monitoring. 