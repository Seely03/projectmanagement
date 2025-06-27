from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from app import app, db
from app import admin_required
from app.models.models import Project, Task, User, ProjectMember
from app.forms import ProjectForm

@app.route('/projects')
@login_required
def projects():
    # Get filter and search parameters
    filter_type = request.args.get('filter', 'all')  # all, assigned, owned
    search_query = request.args.get('search', '').strip()
    
    if current_user.is_admin:
        # Admin can see all projects or filter by assigned/owned
        if filter_type == 'assigned':
            # Get projects where user is a member (including owned)
            project_ids = db.session.query(ProjectMember.project_id).filter_by(user_id=current_user.id).all()
            owned_project_ids = db.session.query(Project.id).filter_by(user_id=current_user.id).all()
            all_project_ids = [pid[0] for pid in project_ids] + [pid[0] for pid in owned_project_ids]
            projects = Project.query.filter(Project.id.in_(all_project_ids)).all()
        elif filter_type == 'owned':
            # Only projects owned by the admin
            projects = Project.query.filter_by(user_id=current_user.id).all()
        else:
            # All projects (default for admin)
            projects = Project.query.all()
    else:
        # Regular users see projects they own or are a member of
        project_ids = db.session.query(ProjectMember.project_id).filter_by(user_id=current_user.id).all()
        owned_project_ids = db.session.query(Project.id).filter_by(user_id=current_user.id).all()
        all_project_ids = [pid[0] for pid in project_ids] + [pid[0] for pid in owned_project_ids]
        projects = Project.query.filter(Project.id.in_(all_project_ids)).all()
    
    # Apply search filter if query provided
    if search_query:
        search_filter = f"%{search_query}%"
        projects = [p for p in projects if (
            search_query.lower() in p.title.lower() or
            search_query.lower() in (p.description or '').lower() or
            search_query.lower() in p.status.lower() or
            search_query.lower() in p.priority.lower()
        )]
    
    return render_template('projects/projects.html', 
                         projects=projects, 
                         filter_type=filter_type, 
                         search_query=search_query)

@app.route('/projects/new', methods=['GET', 'POST'])
@login_required
def new_project():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        status = request.form.get('status')
        priority = request.form.get('priority')
        
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        # Validation
        if not title:
            flash('Project title is required!', 'danger')
            return redirect(url_for('new_project'))
        
        # Parse dates if provided
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else datetime.utcnow()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
        except ValueError:
            flash('Invalid date format! Please use YYYY-MM-DD format.', 'danger')
            return redirect(url_for('new_project'))
        
        # Date validation
        today = datetime.utcnow().date()
        
        # Check if start date is in the past
        if start_date.date() < today:
            flash('Start date cannot be in the past! Please select today or a future date.', 'danger')
            return redirect(url_for('new_project'))
        
        # Check if end date is provided and valid
        if end_date:
            # Check if end date is in the past
            if end_date.date() < today:
                flash('End date cannot be in the past! Please select today or a future date.', 'danger')
                return redirect(url_for('new_project'))
            
            # Check if end date is before start date
            if end_date.date() < start_date.date():
                flash('End date cannot be earlier than start date!', 'danger')
                return redirect(url_for('new_project'))
        
        # Create new project
        new_project = Project(
            title=title,
            description=description,
            status=status or 'In Progress',
            priority=priority or 'Medium',
            start_date=start_date,
            end_date=end_date,
            user_id=current_user.id
        )
        
        db.session.add(new_project)
        db.session.flush()  # Get the project ID
        
        # Automatically add the creator as a project member
        project_member = ProjectMember(
            project_id=new_project.id,
            user_id=current_user.id
        )
        db.session.add(project_member)
        db.session.commit()
        
        flash('Project created successfully! You have been automatically added as a member.', 'success')
        return redirect(url_for('projects'))
        
    return render_template('projects/new_project.html')

@app.route('/projects/<int:project_id>')
@login_required
def view_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check if user is admin or project owner
    if not current_user.is_admin and project.user_id != current_user.id:
        # Check if user is a project member
        is_member = ProjectMember.query.filter_by(project_id=project_id, user_id=current_user.id).first() is not None
        if not is_member:
            flash('You do not have permission to view this project!', 'danger')
            return redirect(url_for('projects'))
    
    tasks = Task.query.filter_by(project_id=project_id).all()
    users = User.query.all()
    project_members = ProjectMember.query.filter_by(project_id=project_id).all()
    member_ids = [member.user_id for member in project_members]
    
    return render_template('projects/view_project.html', 
                         project=project, 
                         tasks=tasks, 
                         users=users,
                         project_members=project_members,
                         member_ids=member_ids)

@app.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check if user is admin or project owner
    if not current_user.is_admin and project.user_id != current_user.id:
        flash('You do not have permission to edit this project!', 'danger')
        return redirect(url_for('projects'))
    
    form = ProjectForm(obj=project)
    
    if form.validate_on_submit():
        # Date validation
        today = datetime.utcnow().date()
        
        # Helper function to get date from form data
        def get_date_from_form_data(form_date):
            if form_date is None:
                return None
            if hasattr(form_date, 'date'):
                return form_date.date()
            return form_date
        
        # Check if start date is being changed and is in the past
        if form.start_date.data:
            start_date = get_date_from_form_data(form.start_date.data)
            original_start_date = get_date_from_form_data(project.start_date)
            
            # Only validate if the date is being changed and the new date is in the past
            if start_date != original_start_date and start_date and start_date < today:
                flash('Start date cannot be in the past! Please select today or a future date.', 'danger')
                return render_template('projects/edit_project.html', project=project, form=form)
        
        # Check if end date is being changed and is in the past
        if form.end_date.data:
            end_date = get_date_from_form_data(form.end_date.data)
            original_end_date = get_date_from_form_data(project.end_date)
            
            # Only validate if the date is being changed and the new date is in the past
            if end_date != original_end_date and end_date and end_date < today:
                flash('End date cannot be in the past! Please select today or a future date.', 'danger')
                return render_template('projects/edit_project.html', project=project, form=form)
            
            # Check if end date is before start date (this should always be validated)
            if form.start_date.data:
                start_date = get_date_from_form_data(form.start_date.data)
                if start_date and end_date and end_date < start_date:
                    flash('End date cannot be earlier than start date!', 'danger')
                    return render_template('projects/edit_project.html', project=project, form=form)
        
        project.title = form.title.data
        project.description = form.description.data
        project.status = form.status.data
        project.priority = form.priority.data
        project.start_date = form.start_date.data
        project.end_date = form.end_date.data
        
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('view_project', project_id=project_id))
    
    return render_template('projects/edit_project.html', project=project, form=form)

@app.route('/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Only admin or project owner can delete a project
    if not current_user.is_admin and project.user_id != current_user.id:
        flash('You do not have permission to delete this project!', 'danger')
        return redirect(url_for('projects'))
        
    db.session.delete(project)
    db.session.commit()
    
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('projects'))

@app.route('/projects/<int:project_id>/members/add', methods=['POST'])
@login_required
def add_project_member(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Only admin or project owner can add members
    if not current_user.is_admin and project.user_id != current_user.id:
        flash('You do not have permission to add members to this project!', 'danger')
        return redirect(url_for('view_project', project_id=project_id))
    
    user_id = request.form.get('user_id', type=int)
    if not user_id:
        flash('User ID is required!', 'danger')
        return redirect(url_for('view_project', project_id=project_id))
    
    # Check if user exists
    user = User.query.get(user_id)
    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('view_project', project_id=project_id))
    
    # Check if user is already a member
    existing_member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()
    if existing_member:
        flash('User is already a member of this project!', 'warning')
        return redirect(url_for('view_project', project_id=project_id))
    
    # Add user as project member
    member = ProjectMember(project_id=project_id, user_id=user_id)
    db.session.add(member)
    db.session.commit()
    
    flash(f'{user.username} has been added to the project!', 'success')
    return redirect(url_for('view_project', project_id=project_id))

@app.route('/projects/<int:project_id>/members/<int:user_id>/remove', methods=['POST'])
@login_required
def remove_project_member(project_id, user_id):
    project = Project.query.get_or_404(project_id)
    
    # Only admin or project owner can remove members
    if not current_user.is_admin and project.user_id != current_user.id:
        flash('You do not have permission to remove members from this project!', 'danger')
        return redirect(url_for('view_project', project_id=project_id))
    
    # Cannot remove project owner
    if user_id == project.user_id:
        flash('Cannot remove the project owner!', 'danger')
        return redirect(url_for('view_project', project_id=project_id))
    
    # Remove member
    member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()
    if member:
        db.session.delete(member)
        db.session.commit()
        flash('Member has been removed from the project!', 'success')
    else:
        flash('User is not a member of this project!', 'warning')
    
    return redirect(url_for('view_project', project_id=project_id))

@app.route('/api/projects/search')
@login_required
def api_search_projects():
    """API endpoint for dynamic project search"""
    search_query = request.args.get('q', '').strip()
    filter_type = request.args.get('filter', 'all')  # all, assigned, owned
    
    # Get projects based on user permissions and filter
    if current_user.is_admin:
        # Admin can see all projects or filter by assigned/owned
        if filter_type == 'assigned':
            # Get projects where user is a member (including owned)
            project_ids = db.session.query(ProjectMember.project_id).filter_by(user_id=current_user.id).all()
            owned_project_ids = db.session.query(Project.id).filter_by(user_id=current_user.id).all()
            all_project_ids = [pid[0] for pid in project_ids] + [pid[0] for pid in owned_project_ids]
            projects = Project.query.filter(Project.id.in_(all_project_ids)).all()
        elif filter_type == 'owned':
            # Only projects owned by the admin
            projects = Project.query.filter_by(user_id=current_user.id).all()
        else:
            # All projects (default for admin)
            projects = Project.query.all()
    else:
        # Regular users see their own projects
        projects = Project.query.filter_by(user_id=current_user.id).all()
    
    # Apply search filter if query provided
    if search_query:
        search_filter = f"%{search_query}%"
        projects = [p for p in projects if (
            search_query.lower() in p.title.lower() or
            search_query.lower() in (p.description or '').lower() or
            search_query.lower() in p.status.lower() or
            search_query.lower() in p.priority.lower()
        )]
    
    # Convert projects to JSON-serializable format
    projects_data = []
    for project in projects[:50]:  # Increased limit for projects page
        project_data = {
            'id': project.id,
            'title': project.title,
            'description': project.description or '',
            'status': project.status,
            'priority': project.priority,
            'start_date': project.start_date.strftime('%Y-%m-%d') if project.start_date else None,
            'end_date': project.end_date.strftime('%Y-%m-%d') if project.end_date else None,
            'created_at': project.created_at.strftime('%Y-%m-%d'),
            'is_overdue': project.end_date and project.end_date < datetime.utcnow() and project.status != 'Completed',
            'task_count': len(project.tasks),
            'url': url_for('view_project', project_id=project.id)
        }
        projects_data.append(project_data)
    
    return jsonify({
        'projects': projects_data,
        'total': len(projects),
        'query': search_query,
        'filter': filter_type
    }) 