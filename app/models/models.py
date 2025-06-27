from datetime import datetime
from flask_login import UserMixin
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    owned_projects = db.relationship('Project', backref='owner', lazy=True)
    tasks = db.relationship('Task', backref='assignee', lazy=True)
    project_memberships = db.relationship('ProjectMember', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='In Progress')  # In Progress, Completed, On Hold
    priority = db.Column(db.String(20), default='Medium')  # Low, Medium, High
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    tasks = db.relationship('Task', backref='project', lazy=True, cascade="all, delete-orphan")
    members = db.relationship('ProjectMember', backref='project', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Project {self.title}>'

class ProjectMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure a user can only be a member of a project once
    __table_args__ = (db.UniqueConstraint('project_id', 'user_id', name='unique_project_member'),)
    
    def __repr__(self):
        return f'<ProjectMember {self.user_id} -> {self.project_id}>'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='To Do')  # To Do, In Progress, Done
    priority = db.Column(db.String(20), default='Medium')  # Low, Medium, High
    effort_points = db.Column(db.Integer, default=1)  # Story points/effort estimation (1, 2, 3, 5, 8, 13, 21)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'<Task {self.title}>' 