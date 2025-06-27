from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from app import app, db
from app import admin_required
from app.models.models import Task, Project, User, ProjectMember
from app.forms import TaskForm

@app.route('/projects/<int:project_id>/tasks')
@login_required
def project_tasks(project_id):
    project = Project.query.get_or_404(project_id)
    tasks = Task.query.filter_by(project_id=project_id).all()
    return render_template('tasks/tasks.html', tasks=tasks, project=project)

@app.route('/projects/<int:project_id>/tasks/new', methods=['GET', 'POST'])
@login_required
def new_task(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check if user is admin, project owner, or project member
    is_project_member = ProjectMember.query.filter_by(project_id=project_id, user_id=current_user.id).first() is not None
    if not current_user.is_admin and project.user_id != current_user.id and not is_project_member:
        flash('You do not have permission to add tasks to this project!', 'danger')
        return redirect(url_for('projects'))
    
    form = TaskForm()
    # Only allow project members as assignees, add Unassigned option
    member_ids = [m.user_id for m in ProjectMember.query.filter_by(project_id=project_id).all()]
    member_users = User.query.filter(User.id.in_(member_ids)).all()
    form.user_id.choices = [(-1, 'Unassigned')] + [(user.id, user.username) for user in member_users]
    
    if form.validate_on_submit():
        # Validate assignee is a project member (if assigned)
        if form.user_id.data and form.user_id.data != -1 and form.user_id.data not in member_ids:
            flash('Selected assignee is not a member of this project!', 'danger')
            return render_template('tasks/new_task.html', project=project, form=form)
        new_task = Task(
            title=form.title.data,
            description=form.description.data,
            status=form.status.data,
            priority=form.priority.data,
            effort_points=form.effort_points.data,
            project_id=project_id,
            user_id=None if form.user_id.data == -1 else form.user_id.data
        )
        
        db.session.add(new_task)
        db.session.commit()
        
        flash('Task created successfully!', 'success')
        return redirect(url_for('view_project', project_id=project_id))
    
    return render_template('tasks/new_task.html', project=project, form=form)

@app.route('/projects/<int:project_id>/tasks/<int:task_id>')
@login_required
def view_task(project_id, task_id):
    project = Project.query.get_or_404(project_id)
    task = Task.query.filter_by(id=task_id, project_id=project_id).first_or_404()
    
    # Check if user is admin, project owner, or task assignee
    if not current_user.is_admin and project.user_id != current_user.id and task.user_id != current_user.id:
        flash('You do not have permission to view this task!', 'danger')
        return redirect(url_for('projects'))
        
    return render_template('tasks/view_task.html', task=task, project=project)

@app.route('/projects/<int:project_id>/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(project_id, task_id):
    project = Project.query.get_or_404(project_id)
    task = Task.query.filter_by(id=task_id, project_id=project_id).first_or_404()
    
    # Check if user is admin, project owner, or task assignee
    if not current_user.is_admin and project.user_id != current_user.id and task.user_id != current_user.id:
        flash('You do not have permission to edit this task!', 'danger')
        return redirect(url_for('projects'))
    
    form = TaskForm(obj=task)
    # Only allow project members as assignees, add Unassigned option
    member_ids = [m.user_id for m in ProjectMember.query.filter_by(project_id=project_id).all()]
    member_users = User.query.filter(User.id.in_(member_ids)).all()
    form.user_id.choices = [(-1, 'Unassigned')] + [(user.id, user.username) for user in member_users]
    
    if form.validate_on_submit():
        # Validate assignee is a project member (if assigned)
        if form.user_id.data and form.user_id.data != -1 and form.user_id.data not in member_ids:
            flash('Selected assignee is not a member of this project!', 'danger')
            return render_template('tasks/edit_task.html', task=task, project=project, form=form)
        task.title = form.title.data
        task.description = form.description.data
        task.status = form.status.data
        task.priority = form.priority.data
        task.user_id = None if form.user_id.data == -1 else form.user_id.data
        task.effort_points = form.effort_points.data
        
        db.session.commit()
        
        flash('Task updated successfully!', 'success')
        return redirect(url_for('view_task', project_id=project_id, task_id=task_id))
    
    return render_template('tasks/edit_task.html', task=task, project=project, form=form)

@app.route('/projects/<int:project_id>/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(project_id, task_id):
    project = Project.query.get_or_404(project_id)
    task = Task.query.filter_by(id=task_id, project_id=project_id).first_or_404()
    
    # Only admin or project owner can delete a task
    if not current_user.is_admin and project.user_id != current_user.id:
        flash('You do not have permission to delete this task!', 'danger')
        return redirect(url_for('projects'))
        
    db.session.delete(task)
    db.session.commit()
    
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('view_project', project_id=project_id))

@app.route('/projects/<int:project_id>/tasks/<int:task_id>/update-status', methods=['POST'])
@login_required
def update_task_status(project_id, task_id):
    project = Project.query.get_or_404(project_id)
    task = Task.query.filter_by(id=task_id, project_id=project_id).first_or_404()
    
    # Regular users can update task status if they are the task assignee or project owner
    if not current_user.is_admin and project.user_id != current_user.id and task.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    status = request.form.get('status')
    if not status:
        return jsonify({'success': False, 'message': 'Status is required'}), 400
    
    task.status = status
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Task status updated successfully'}) 