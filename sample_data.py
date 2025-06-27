from app import db, app
from app.models.models import User, Project, Task, ProjectMember
from datetime import datetime
import random

if __name__ == "__main__":
    with app.app_context():
        # 1. Seed Users
        users_data = [
            {"username": "Admin", "email": "Admin@admin.com", "password_hash": "Admin123!", "is_admin": True},
            {"username": "Tyrone", "email": "Tyrone@tyrone.com", "password_hash": "Tyrone123!", "is_admin": False},
            {"username": "Alice", "email": "Alice@alice.com", "password_hash": "Alice123!", "is_admin": False},
            {"username": "Jordan", "email": "Jordan@jordan.com", "password_hash": "Jordan123!", "is_admin": False},
            {"username": "Sasha", "email": "Sasha@sasha.com", "password_hash": "Sasha123!", "is_admin": False},
            {"username": "Mason", "email": "Mason@mason.com", "password_hash": "Mason123!", "is_admin": False},
            {"username": "Nolan", "email": "Nolan@nolan.com", "password_hash": "Nolan123!", "is_admin": False},
            {"username": "Layla", "email": "Layla@layla.com", "password_hash": "Layla123!", "is_admin": False},
            {"username": "Elias", "email": "Elias@elias.com", "password_hash": "Elias123!", "is_admin": False},
            {"username": "Kiwi", "email": "Kiwi@kiwi.com", "password_hash": "Kiwi123!", "is_admin": False},
        ]

        users = []
        for data in users_data:
            user = User(username=data["username"], email=data["email"], is_admin=data["is_admin"])
            user.set_password(data["password_hash"])
            db.session.add(user)
            users.append(user)

        db.session.commit()

        # 2. Seed Projects
        project_data = [
            ("Website Redesign", "Revamp the corporate website"),
            ("Mobile App Launch", "Launch the Android version"),
            ("Marketing Campaign Q3", "Plan and execute Q3 strategy"),
            ("Employee Onboarding", "Streamline new hire setup"),
            ("Customer Feedback System", "Implement customer voice tracking"),
            ("Cloud Infrastructure Migration", "Move systems to AWS"),
            ("E-commerce Product Launch", "Launch the new product line"),
            ("Financial Report Q2", "Compile and analyze Q2 financials"),
            ("Internal Tool Dev", "Build internal productivity tools"),
            ("SEO Optimization", "Improve search visibility"),
        ]

        projects = []
        for title, description in project_data:
            owner = random.choice(users)
            project = Project(title=title, description=description, user_id=owner.id)
            db.session.add(project)
            projects.append(project)

        db.session.commit()

        # 3. Seed Tasks (2–3 per project)
        task_templates = {
            "Website Redesign": ["Design homepage", "Migrate blog", "Test responsiveness"],
            "Mobile App Launch": ["Finalize Android build", "Set up analytics", "Submit to store"],
            "Marketing Campaign Q3": ["Draft email copy", "Design ad banners", "Schedule social posts"],
            "Employee Onboarding": ["Create checklist", "Set up accounts", "Assign training"],
            "Customer Feedback System": ["Build form", "Integrate CRM", "Set up alerts"],
            "Cloud Infrastructure Migration": ["Migrate DB", "Setup load balancer", "CI/CD pipeline"],
            "E-commerce Product Launch": ["Write product copy", "Upload images", "Test checkout"],
            "Financial Report Q2": ["Gather data", "Build dashboard", "Review draft"],
            "Internal Tool Dev": ["Design DB schema", "Build auth system", "Write docs"],
            "SEO Optimization": ["Audit site", "Optimize metadata", "Generate sitemap"],
        }

        for project in projects:
            task_titles = task_templates.get(project.title, ["Task 1", "Task 2"])
            selected_titles = random.sample(task_titles, k=random.choice([2, 3]))

            for title in selected_titles:
                assigned_user = random.choice(users)
                task = Task(
                    title=title,
                    description=f"{title} for {project.title}",
                    project_id=project.id,
                    user_id=assigned_user.id,
                )
                db.session.add(task)

        db.session.commit()

        # 4. Seed Project Members
        for project in projects:
            member_pool = [u for u in users if u.id != project.user_id]
            selected_members = random.sample(member_pool, k=3)
            for member in selected_members:
                db.session.add(ProjectMember(project_id=project.id, user_id=member.id))

        db.session.commit()
