from app import db, app
from app.models.models import User, Project, Task, ProjectMember
from datetime import datetime, timedelta
import random

def seed_database():
    """Seed the database with sample data"""
    print("Starting database seeding...")
    
    with app.app_context():
        # Check if already seeded
        if User.query.count() > 0:
            print("Database already has users, skipping seeding")
            return
            
        # 1. Seed Users with proper password hashing
        users_data = [
            {"username": "Admin", "email": "admin@admin.com", "password": "Admin123!", "is_admin": True},
            {"username": "Tyrone", "email": "tyrone@tyrone.com", "password": "Tyrone123!", "is_admin": False},
            {"username": "Alice", "email": "alice@alice.com", "password": "Alice123!", "is_admin": False},
            {"username": "Jordan", "email": "jordan@jordan.com", "password": "Jordan123!", "is_admin": False},
            {"username": "Sasha", "email": "sasha@sasha.com", "password": "Sasha123!", "is_admin": False},
            {"username": "Mason", "email": "mason@mason.com", "password": "Mason123!", "is_admin": False},
            {"username": "Nolan", "email": "nolan@nolan.com", "password": "Nolan123!", "is_admin": False},
            {"username": "Layla", "email": "layla@layla.com", "password": "Layla123!", "is_admin": False},
            {"username": "Elias", "email": "elias@elias.com", "password": "Elias123!", "is_admin": False},
            {"username": "Kiwi", "email": "kiwi@kiwi.com", "password": "Kiwi123!", "is_admin": False},
        ]

        users = []
        for data in users_data:
            user = User(
                username=data["username"], 
                email=data["email"], 
                is_admin=data["is_admin"]
            )
            user.set_password(data["password"])  # Use the set_password method
            db.session.add(user)
            users.append(user)

        db.session.commit()
        print(f"✅ Created {len(users)} users")

        # 2. Seed Projects with enhanced fields
        project_data = [
            {
                "title": "Website Redesign",
                "description": "Revamp the corporate website with modern UI/UX",
                "status": "In Progress",
                "priority": "High",
                "days_from_now": 30
            },
            {
                "title": "Mobile App Launch", 
                "description": "Launch the Android version of our mobile app",
                "status": "In Progress",
                "priority": "High", 
                "days_from_now": 45
            },
            {
                "title": "Marketing Campaign Q3",
                "description": "Plan and execute Q3 marketing strategy",
                "status": "In Progress",
                "priority": "Medium",
                "days_from_now": 60
            },
            {
                "title": "Employee Onboarding",
                "description": "Streamline new hire onboarding process",
                "status": "On Hold",
                "priority": "Low",
                "days_from_now": 90
            },
            {
                "title": "Customer Feedback System",
                "description": "Implement comprehensive customer voice tracking",
                "status": "In Progress",
                "priority": "Medium",
                "days_from_now": 75
            },
            {
                "title": "Cloud Infrastructure Migration",
                "description": "Migrate all systems to AWS cloud infrastructure",
                "status": "In Progress",
                "priority": "High",
                "days_from_now": 120
            },
            {
                "title": "E-commerce Product Launch",
                "description": "Launch the new product line on e-commerce platform",
                "status": "Completed",
                "priority": "High",
                "days_from_now": 15
            },
            {
                "title": "Financial Report Q2",
                "description": "Compile and analyze Q2 financial performance",
                "status": "Completed",
                "priority": "Medium",
                "days_from_now": 7
            },
            {
                "title": "Internal Tool Development",
                "description": "Build internal productivity and collaboration tools",
                "status": "In Progress",
                "priority": "Medium",
                "days_from_now": 100
            },
            {
                "title": "SEO Optimization",
                "description": "Improve search engine visibility and rankings",
                "status": "On Hold",
                "priority": "Low",
                "days_from_now": 50
            },
        ]

        projects = []
        for data in project_data:
            owner = random.choice(users)
            end_date = datetime.utcnow() + timedelta(days=data["days_from_now"])
            
            project = Project(
                title=data["title"],
                description=data["description"],
                status=data["status"],
                priority=data["priority"],
                end_date=end_date,
                user_id=owner.id
            )
            db.session.add(project)
            projects.append(project)

        db.session.commit()
        print(f"✅ Created {len(projects)} projects")

        # 3. Seed Tasks with enhanced fields (2–4 per project)
        task_templates = {
            "Website Redesign": [
                {"title": "Design homepage mockup", "status": "Done", "priority": "High", "effort": 8},
                {"title": "Implement responsive navigation", "status": "In Progress", "priority": "High", "effort": 5},
                {"title": "Migrate blog content", "status": "To Do", "priority": "Medium", "effort": 3},
                {"title": "Test cross-browser compatibility", "status": "To Do", "priority": "Medium", "effort": 3}
            ],
            "Mobile App Launch": [
                {"title": "Finalize Android build", "status": "In Progress", "priority": "High", "effort": 13},
                {"title": "Set up analytics tracking", "status": "Done", "priority": "Medium", "effort": 5},
                {"title": "Submit to Google Play Store", "status": "To Do", "priority": "High", "effort": 2},
                {"title": "Create app store screenshots", "status": "To Do", "priority": "Low", "effort": 2}
            ],
            "Marketing Campaign Q3": [
                {"title": "Draft email campaign copy", "status": "Done", "priority": "Medium", "effort": 3},
                {"title": "Design social media banners", "status": "In Progress", "priority": "Medium", "effort": 5},
                {"title": "Schedule social media posts", "status": "To Do", "priority": "Low", "effort": 2},
                {"title": "Set up campaign analytics", "status": "To Do", "priority": "Medium", "effort": 3}
            ],
            "Employee Onboarding": [
                {"title": "Create onboarding checklist", "status": "To Do", "priority": "High", "effort": 5},
                {"title": "Set up new hire accounts", "status": "To Do", "priority": "Medium", "effort": 3},
                {"title": "Assign training modules", "status": "To Do", "priority": "Medium", "effort": 2}
            ],
            "Customer Feedback System": [
                {"title": "Build feedback form interface", "status": "In Progress", "priority": "High", "effort": 8},
                {"title": "Integrate with CRM system", "status": "To Do", "priority": "High", "effort": 13},
                {"title": "Set up email alerts", "status": "To Do", "priority": "Medium", "effort": 3},
                {"title": "Create analytics dashboard", "status": "To Do", "priority": "Medium", "effort": 8}
            ],
            "Cloud Infrastructure Migration": [
                {"title": "Migrate database to AWS RDS", "status": "In Progress", "priority": "High", "effort": 21},
                {"title": "Setup load balancer", "status": "To Do", "priority": "High", "effort": 8},
                {"title": "Configure CI/CD pipeline", "status": "To Do", "priority": "Medium", "effort": 13},
                {"title": "Set up monitoring alerts", "status": "To Do", "priority": "Medium", "effort": 5}
            ],
            "E-commerce Product Launch": [
                {"title": "Write product descriptions", "status": "Done", "priority": "High", "effort": 5},
                {"title": "Upload product images", "status": "Done", "priority": "Medium", "effort": 3},
                {"title": "Test checkout process", "status": "Done", "priority": "High", "effort": 8},
                {"title": "Launch marketing campaign", "status": "Done", "priority": "High", "effort": 5}
            ],
            "Financial Report Q2": [
                {"title": "Gather financial data", "status": "Done", "priority": "High", "effort": 5},
                {"title": "Build reporting dashboard", "status": "Done", "priority": "Medium", "effort": 8},
                {"title": "Review and finalize report", "status": "Done", "priority": "High", "effort": 3}
            ],
            "Internal Tool Development": [
                {"title": "Design database schema", "status": "Done", "priority": "High", "effort": 8},
                {"title": "Build authentication system", "status": "In Progress", "priority": "High", "effort": 13},
                {"title": "Create user interface", "status": "To Do", "priority": "Medium", "effort": 13},
                {"title": "Write documentation", "status": "To Do", "priority": "Low", "effort": 5}
            ],
            "SEO Optimization": [
                {"title": "Conduct SEO audit", "status": "To Do", "priority": "High", "effort": 8},
                {"title": "Optimize page metadata", "status": "To Do", "priority": "Medium", "effort": 5},
                {"title": "Generate XML sitemap", "status": "To Do", "priority": "Low", "effort": 2},
                {"title": "Implement schema markup", "status": "To Do", "priority": "Medium", "effort": 5}
            ],
        }

        task_count = 0
        for project in projects:
            project_tasks = task_templates.get(project.title, [])
            # Select 2-4 tasks per project
            num_tasks = min(len(project_tasks), random.choice([2, 3, 4]))
            selected_tasks = random.sample(project_tasks, k=num_tasks) if project_tasks else []

            for task_data in selected_tasks:
                assigned_user = random.choice(users)
                task = Task(
                    title=task_data["title"],
                    description=f"{task_data['title']} for {project.title}",
                    status=task_data["status"],
                    priority=task_data["priority"],
                    effort_points=task_data["effort"],
                    project_id=project.id,
                    user_id=assigned_user.id,
                )
                db.session.add(task)
                task_count += 1

        db.session.commit()
        print(f"✅ Created {task_count} tasks")

        # 4. Seed Project Members (3-5 members per project)
        member_count = 0
        for project in projects:
            # Get users who aren't the project owner
            member_pool = [u for u in users if u.id != project.user_id]
            # Add 3-5 random members to each project
            num_members = random.choice([3, 4, 5])
            selected_members = random.sample(member_pool, k=min(num_members, len(member_pool)))
            
            for member in selected_members:
                project_member = ProjectMember(
                    project_id=project.id, 
                    user_id=member.id
                )
                db.session.add(project_member)
                member_count += 1

        db.session.commit()

if __name__ == "__main__":
    seed_database()